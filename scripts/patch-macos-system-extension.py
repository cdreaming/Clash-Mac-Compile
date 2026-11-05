#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ACTIVATOR_SOURCE = r"""
#if os(macOS)
import Foundation
@preconcurrency import SystemExtensions

enum ClashMacSystemExtensionActivationError: LocalizedError {
    case missingApplicationIdentifier
    case restartRequired

    var errorDescription: String? {
        switch self {
        case .missingApplicationIdentifier:
            return "Clash could not determine its application identifier for System Extension activation."
        case .restartRequired:
            return "The Clash Network Extension update requires a Mac restart before it can become active."
        }
    }
}

@MainActor
enum ClashMacSystemExtensionActivator {
    private static var activeDelegate: RequestDelegate?
    private static var activeRequest: OSSystemExtensionRequest?

    static func activate(onWaiting: @escaping () -> Void) async throws {
        guard let appIdentifier = Bundle.main.bundleIdentifier else {
            throw ClashMacSystemExtensionActivationError.missingApplicationIdentifier
        }

        // Keep this suffix in sync with ClashmacOSExtension's PRODUCT_BUNDLE_IDENTIFIER.
        let extensionIdentifier = appIdentifier + ".packet-tunnel"

        try await withCheckedThrowingContinuation { (continuation: CheckedContinuation<Void, Error>) in
            let delegate = RequestDelegate(onWaiting: onWaiting)
            delegate.continuation = continuation
            activeDelegate = delegate

            let request = OSSystemExtensionRequest.activationRequest(
                forExtensionWithIdentifier: extensionIdentifier,
                queue: .main
            )
            request.delegate = delegate
            activeRequest = request
            OSSystemExtensionManager.shared.submitRequest(request)
        }
    }

    private static func finish(
        _ result: Swift.Result<Void, Error>,
        delegate: RequestDelegate
    ) {
        guard activeDelegate === delegate else { return }
        activeDelegate = nil
        activeRequest = nil
        let continuation = delegate.continuation
        delegate.continuation = nil
        continuation?.resume(with: result)
    }

    @MainActor
    private final class RequestDelegate: NSObject, @preconcurrency OSSystemExtensionRequestDelegate {
        var continuation: CheckedContinuation<Void, Error>?
        private let onWaiting: () -> Void

        init(onWaiting: @escaping () -> Void) {
            self.onWaiting = onWaiting
            super.init()
        }

        func requestNeedsUserApproval(_ request: OSSystemExtensionRequest) {
            // macOS will show the approval flow / direct the user to System Settings.
            // Keep the activation request alive; VPN preference registration must wait
            // until the System Extension activation callback succeeds.
            onWaiting()
        }

        func request(
            _ request: OSSystemExtensionRequest,
            didFinishWithResult result: OSSystemExtensionRequest.Result
        ) {
            switch result {
            case .completed:
                ClashMacSystemExtensionActivator.finish(.success(()), delegate: self)
            case .willCompleteAfterReboot:
                ClashMacSystemExtensionActivator.finish(
                    .failure(ClashMacSystemExtensionActivationError.restartRequired),
                    delegate: self
                )
            @unknown default:
                let error = NSError(
                    domain: "ClashMacSystemExtensionActivation",
                    code: -1,
                    userInfo: [NSLocalizedDescriptionKey: "macOS returned an unknown System Extension activation result."]
                )
                ClashMacSystemExtensionActivator.finish(.failure(error), delegate: self)
            }
        }

        func request(_ request: OSSystemExtensionRequest, didFailWithError error: Error) {
            ClashMacSystemExtensionActivator.finish(.failure(error), delegate: self)
        }

        func request(
            _ request: OSSystemExtensionRequest,
            actionForReplacingExtension existing: OSSystemExtensionProperties,
            withExtension newExtension: OSSystemExtensionProperties
        ) -> OSSystemExtensionRequest.ReplacementAction {
            .replace
        }
    }
}
#endif
"""

def fail(message: str) -> None:
    raise RuntimeError(message)


def patch_project(project_file: Path) -> dict:
    data = yaml.safe_load(project_file.read_text(encoding="utf-8"))
    targets = data.get("targets", {})
    app = targets.get("ClashmacOS")
    extension = targets.get("ClashmacOSExtension")
    widgets = targets.get("ClashmacOSWidgets")
    if not isinstance(app, dict) or not isinstance(extension, dict):
        fail("Pinned upstream project.yml does not contain ClashmacOS / ClashmacOSExtension targets.")

    extension["type"] = "system-extension"
    extension.setdefault("settings", {}).setdefault("base", {})["PRODUCT_BUNDLE_IDENTIFIER"] = "$(CLASH_BUNDLE_BASE).packet-tunnel"
    extension["settings"]["base"]["PRODUCT_NAME"] = "ClashmacOSExtension"

    ext_entitlements = extension.setdefault("entitlements", {}).setdefault("properties", {})
    ext_entitlements["com.apple.developer.networking.networkextension"] = [
        "packet-tunnel-provider-systemextension"
    ]

    app_entitlements = app.setdefault("entitlements", {}).setdefault("properties", {})
    app_entitlements["com.apple.developer.networking.networkextension"] = [
        "packet-tunnel-provider-systemextension"
    ]
    app_entitlements["com.apple.developer.system-extension.install"] = True

    dependencies = app.setdefault("dependencies", [])
    provider_dependency = next(
        (item for item in dependencies
         if isinstance(item, dict) and item.get("target") == "ClashmacOSExtension"),
        None
    )
    if provider_dependency is None:
        dependencies.append({"target": "ClashmacOSExtension", "embed": True})
    else:
        provider_dependency["embed"] = True

    has_system_extensions_framework = any(
        isinstance(item, dict) and item.get("sdk") == "SystemExtensions.framework"
        for item in dependencies
    )
    if not has_system_extensions_framework:
        dependencies.append({"sdk": "SystemExtensions.framework"})

    # Widgets do not host the Packet Tunnel provider and should not carry its entitlement.
    if isinstance(widgets, dict):
        widget_properties = widgets.get("entitlements", {}).get("properties", {})
        widget_properties.pop("com.apple.developer.networking.networkextension", None)

    project_file.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False),
        encoding="utf-8"
    )
    return {
        "app_target": "ClashmacOS",
        "provider_target": "ClashmacOSExtension",
        "provider_product_type": extension["type"],
        "provider_bundle_identifier": extension["settings"]["base"]["PRODUCT_BUNDLE_IDENTIFIER"],
        "network_extension_entitlement": "packet-tunnel-provider-systemextension",
        "system_extension_install_entitlement": bool(
            app_entitlements.get("com.apple.developer.system-extension.install")
        ),
        "system_extensions_framework_linked": True,
    }


def patch_authorization_source(source_file: Path) -> None:
    if not source_file.is_file():
        fail(f"Upstream VPN authorization source is missing: {source_file}")

    text = source_file.read_text(encoding="utf-8")
    import_line = "#if os(macOS)\nimport SystemExtensions\n#endif\n"
    if "import SystemExtensions" not in text:
        text = text.replace("import Foundation\n", "import Foundation\n" + import_line, 1)

    call = """#if os(macOS)
            try await ClashMacSystemExtensionActivator.activate(onWaiting: onWaiting)
#endif
"""
    anchor = """        do {
            try await IPStackProfileWriter.awaitConfirmation(
"""
    if "ClashMacSystemExtensionActivator.activate" not in text:
        if anchor not in text:
            fail("Could not find the VPN saveToPreferences authorization sequence in VPNStartAuthorization.swift.")
        text = text.replace(anchor, "        do {\n" + call + "            try await IPStackProfileWriter.awaitConfirmation(\n", 1)

    source_file.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch the pinned ProjectClash macOS Packet Tunnel to a direct-distribution System Extension.")
    parser.add_argument("--client-dir", required=True, type=Path)
    args = parser.parse_args()

    client = args.client_dir.resolve()
    project_file = client / "apple/ClashClient/project.yml"
    authorization_source = client / "apple/ClashClient/Sources/VPNStartAuthorization.swift"
    sources_dir = client / "apple/ClashClient/Sources"

    result = patch_project(project_file)
    patch_authorization_source(authorization_source)

    activator_file = sources_dir / "ClashMacSystemExtensionActivator.swift"
    activator_file.write_text(ACTIVATOR_SOURCE, encoding="utf-8")

    # Validate the transformed spec after writing it.
    data = yaml.safe_load(project_file.read_text(encoding="utf-8"))
    ext = data["targets"]["ClashmacOSExtension"]
    app = data["targets"]["ClashmacOS"]
    if ext.get("type") != "system-extension":
        fail("ClashmacOSExtension is not a system-extension target after patching.")
    if "packet-tunnel-provider-systemextension" not in ext["entitlements"]["properties"].get(
        "com.apple.developer.networking.networkextension", []
    ):
        fail("System Extension Packet Tunnel entitlement is missing.")
    if not app["entitlements"]["properties"].get("com.apple.developer.system-extension.install"):
        fail("Main app System Extension installation entitlement is missing.")
    if "ClashMacSystemExtensionActivator.activate" not in authorization_source.read_text(encoding="utf-8"):
        fail("VPN activation flow is not wired to the System Extension activator.")

    print("macOS System Extension patch: OK")
    print(yaml.safe_dump(result, sort_keys=False, allow_unicode=True).strip())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"System Extension patch failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
