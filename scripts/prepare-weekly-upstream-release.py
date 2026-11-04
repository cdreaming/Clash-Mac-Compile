#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def run(args: list[str]) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def next_patch(version: str) -> str:
    match = SEMVER_RE.fullmatch(version)
    if not match:
        raise RuntimeError(f"Invalid current VERSION: {version}")
    major, minor, patch = map(int, match.groups())
    return f"{major}.{minor}.{patch + 1}"


def replace_file(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected text not found in {path.relative_to(ROOT)}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare a patch release for a new pinned ProjectClash Client commit"
    )
    parser.add_argument("--client-sha", required=True)
    parser.add_argument("--risk", choices=["L1", "L2", "L3"], default="L2")
    parser.add_argument("--force", action="store_true",
                        help="Create a new patch version even if the Client SHA is unchanged")
    args = parser.parse_args()

    client_sha = args.client_sha.lower()
    if not SHA_RE.fullmatch(client_sha):
        raise RuntimeError("client-sha must be a full 40-character lowercase commit SHA")

    current_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    current_sha = (ROOT / "UPSTREAM_CLIENT_REF").read_text(encoding="utf-8").strip()
    if client_sha == current_sha and not args.force:
        print("No upstream change; weekly release preparation skipped.")
        return 10

    version = next_patch(current_version)
    run([sys.executable, "scripts/prepare-version.py",
         "--version", version, "--risk", args.risk, "--write"])

    (ROOT / "UPSTREAM_CLIENT_REF").write_text(client_sha + "\n", encoding="utf-8")
    (ROOT / "RELEASE_REVISION").write_text("0\n", encoding="utf-8")

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = re.sub(
        r"当前版本 `[^`]+`",
        f"当前版本 `{version}`",
        text,
        count=1
    )
    text = re.sub(
        r"`UPSTREAM_CLIENT_REF` 当前固定为官方 Client commit `[0-9a-f]{40}`",
        f"`UPSTREAM_CLIENT_REF` 当前固定为官方 Client commit `{client_sha}`",
        text,
        count=1
    )
    readme.write_text(text, encoding="utf-8")

    build_info = ROOT / "BUILD-INFO.md"
    text = build_info.read_text(encoding="utf-8")
    text = re.sub(r"当前版本 `[^`]+`", f"当前版本 `{version}`", text, count=1)
    text = re.sub(
        r"(- 上游客户端 Ref：`)[0-9a-f]{40}(`)",
        rf"\g<1>{client_sha}\2",
        text,
        count=1
    )
    build_info.write_text(text, encoding="utf-8")

    changelog = ROOT / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8")
    text = text.replace(
        "- 待记录本版真实变化。",
        f"- 跟进 ProjectClash/Clash-Client 新提交 `{client_sha}`。\n"
        "- 由该 Client 提交的 `Dependencies.lock.json` 固定 Clash Kernel 与 Adapter。\n"
        "- 自动生成 arm64 性能优先构建、构建元数据和 GitHub Pre-release。",
        1
    )
    changelog.write_text(text, encoding="utf-8")

    release_dir = ROOT / "docs/releases" / f"v{version}"
    tag = f"v{version}"
    release_notes = f"""# Clash_Mac_Compile {tag} · Weekly Preview

## 下载说明

普通用户下载 **`Clash_Mac_Compile-v{version}-macos-arm64-unsigned.zip`**；开发者下载 **`Clash_Mac_Compile_v{version}_source.zip`**。

## 上游来源与构建配置

- ProjectClash Client: `{client_sha}`
- Kernel / Adapter: 由 Client 的 `Dependencies.lock.json` 固定。
- 架构：Apple Silicon `arm64`。
- Swift 优化：`-O`，运行速度优先。
- Xcode 并行任务：最多 2。
- 签名：关闭，不需要 Apple Developer 证书。
- VPN 限制：无签名构建不支持 Packet Tunnel / Network Extension 系统授权。

## 下载资产说明

| 文件 | 用途 |
|---|---|
| `Clash_Mac_Compile-v{version}-macos-arm64-unsigned.zip` | Apple Silicon macOS 原生 APP（无签名） |
| `Clash_Mac_Compile_v{version}_source.zip` | 完整构建工程源码 |
| `BUILD-METADATA.json` | 上游 commit、Xcode、Go 和优化配置 |
| `SHA256SUMS.txt` | 下载文件完整性校验 |
| `RELEASE-MANIFEST.json` | Release 资产清单 |

## 安装说明

1. 下载 APP ZIP 并解压，确认包含 `Clash.app`。
2. 将 APP 放入 `/Applications`。
3. macOS 可能提示无法验证开发者或阻止打开；本项目不提供签名或公证，因此不能保证所有 macOS 安全策略都允许启动。
4. 本版本主要用于验证 GUI / 编译产物，不应视为可用的 VPN 客户端安装包。

## VPN 与配置目录限制

本版本不使用 Apple Developer 签名、Provisioning Profile 或公证服务。点击“重试，并允许添加 VPN 配置”时，macOS 可能不会弹出授权提示，Packet Tunnel 也不能保证创建或启动。

预期 App Group 路径（仅供参考，未签名版本不保证该目录存在）：

`~/Library/Group Containers/group.com.cdreaming.clash/`

配置工作区由官方 `ConfigResourceStore` 管理；无签名版本可能没有有效 App Groups entitlement。

## 性能说明

本版使用 Swift `-O` 运行速度优先构建。它是编译器优化策略，不代表已经完成 Instruments 实测；实际 CPU、内存、启动和 UI 流畅度仍需在目标 Mac 上测量。

## 发布通道

这是 GitHub Pre-release / Weekly Preview，不是稳定版。确认 GUI 和非 VPN 功能后，再由维护者决定是否提升为 Stable Release。

## 上游许可

本项目使用 ProjectClash 上游客户端、Clash Kernel 和 Adapter。分发时请遵守对应 GPL-3.0 及第三方依赖许可要求。
"""
    (release_dir / "RELEASE-NOTES.md").write_text(release_notes, encoding="utf-8")

    (release_dir / "DEVELOPMENT-JOURNAL.md").write_text(
        f"""# {tag} Development Journal

<!-- DEVELOPMENT-SESSION-STATUS: complete -->
<!-- DEVELOPMENT-LAST-CHECKPOINT: WEEKLY-UPSTREAM -->
<!-- DEVELOPMENT-COMPLETION-SOURCE: automated-weekly-release -->

## 目标

跟进 ProjectClash 官方 Client 新提交并生成每周预览版。

## 上游固定版本

- Client commit: `{client_sha}`
- Kernel / Adapter: 由该 Client 的 `Dependencies.lock.json` 固定。

## 自动化步骤

1. 每周定时查询 Client `main`。
2. 仅在 commit 变化时递增 Patch 版本。
3. 执行质量检查和 macOS arm64 构建。
4. 构建成功后提交版本更新、创建 tag 和 GitHub Pre-release。

## 完成边界

本日志随源码包生成；云端构建、发布与线上资产验证以本次 GitHub Actions 运行记录为准。
""", encoding="utf-8"
    )

    (release_dir / "VALIDATION-REPORT.md").write_text(
        f"""# {tag} Validation Report

## 固定源码

- Client commit: `{client_sha}`
- Kernel / Adapter: 由该 Client 的 `Dependencies.lock.json` 固定。
- Swift optimization: `-O`。
- Architecture: arm64。

## 自动化验证

本报告随本次周度工作流生成。发布前工作流必须执行：
- 项目配置和完整 40 位 SHA 检查。
- Python / Shell 语法检查。
- 项目单元测试和打包回归测试。
- macOS Xcode 原生 APP 构建。
- APP 主执行文件 arm64 检查。
- ZIP / SHA-256 检查和 Release 在线资产复核。

实际通过与否以本次 Actions 运行日志和 Release 资产为准；若工作流失败，不应创建或发布 tag。

## 已知限制 / 尚未验证

- 本版无签名，不支持 Packet Tunnel / Network Extension 系统授权。
- macOS Gatekeeper 是否允许启动取决于系统安全策略。
- Instruments 运行性能基准尚未在目标 Mac 完成。
""", encoding="utf-8"
    )

    (release_dir / "RELEASE-EXPERIENCE-REPORT.md").write_text(
        f"""# {tag} Release Experience Report

本版由每周上游检查自动准备，Client commit 为 `{client_sha}`。

自动化仅在上游 SHA 变化时递增 Patch 版本。APP 构建成功后才会提交 main、创建 tag 和 GitHub Pre-release。失败时不创建 tag / Release。

本版本使用 Swift `-O`，后续必须以 Instruments 的可重复基准比较启动、CPU、内存、网络和 UI 响应。
""", encoding="utf-8"
    )

    (ROOT / "docs/release-lessons" / f"v{version}.md").write_text(
        f"""# {tag} Release Lesson

- 上游 Client 固定 commit：`{client_sha}`。
- 周度检查仅在上游 commit 变化时递增 Patch 版本。
- 只有完整构建和产物校验成功后才创建 Git tag 与 Pre-release。
- GitHub Actions 使用 GITHUB_TOKEN 推送的事件不会自动触发另一条 push/tag workflow；周度工作流在同一条 run 中完成构建、tag 和 Release。
- 每周预览版本保持 Pre-release，Stable 需要维护者确认。
""", encoding="utf-8"
    )

    # Add the release download guide and performance strategy to README.
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    if "docs/github/RELEASE-DOWNLOAD-GUIDE.md" not in text:
        text += "\n## 下载与性能说明\n\n- GitHub Releases 下载说明：`docs/github/RELEASE-DOWNLOAD-GUIDE.md`\n- macOS 配置目录：`docs/macos/CONFIGURATION-DIRECTORIES.md`\n- 运行性能策略：`docs/performance/PERFORMANCE-STRATEGY.md`\n"
    readme.write_text(text, encoding="utf-8")

    # Keep repository catalog and generated indexes accurate.
    run([sys.executable, "scripts/update-repository-structure.py", "--sync"])
    catalog_path = ROOT / ".ai/REPOSITORY-CATALOG.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    descriptions = {
        "scripts/prepare-weekly-upstream-release.py": "检测到上游新 Client SHA 后自动递增 Patch 版本并生成周度 Preview 文档。",
                "docs/macos/CONFIGURATION-DIRECTORIES.md": "说明 App Group 配置容器、无签名限制和数据目录检查方法。",
        "docs/performance/PERFORMANCE-STRATEGY.md": "运行速度优先的 Swift -O 构建策略与 Instruments / Go pprof 基准计划。",
        "docs/github/RELEASE-DOWNLOAD-GUIDE.md": "GitHub Releases 下载资产说明、安装步骤、配置路径和 Weekly Preview / Stable 区别。",
    }
    for rel, description in descriptions.items():
        catalog.setdefault("files", {})[rel] = description
    catalog.setdefault("folders", {})["docs/macos/"] = "macOS 配置目录、App Group 容器和安装后数据检查说明。"
    catalog.setdefault("folders", {})["docs/performance/"] = "运行性能优化策略、基准测试和 Instruments / Go pprof 指南。"
    catalog.setdefault("folders", {})[".github/workflows/"] = "GitHub Actions CI、arm64 构建、正式 Release 与每周上游自动预览发布工作流。"
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    run([sys.executable, "scripts/update-repository-structure.py", "--write"])
    run([sys.executable, "scripts/build-source-manifest.py", "--write"])

    output = Path(__import__("os").environ.get("GITHUB_OUTPUT", "/dev/null"))
    if output != Path("/dev/null"):
        with output.open("a", encoding="utf-8") as f:
            f.write(f"version={version}\n")
            f.write(f"tag={tag}\n")
            f.write(f"client_sha={client_sha}\n")
    print(f"Prepared weekly preview {tag} for Client {client_sha}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Weekly upstream preparation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
