from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ".github/workflows/build-macos.yml",
    ".github/workflows/release.yml",
    ".github/workflows/upstream-weekly.yml",
)


def build_step(workflow_path: str) -> str:
    lines = (ROOT / workflow_path).read_text(encoding="utf-8").splitlines()
    marker = "      - name: Build and verify native macOS app"
    starts = [index for index, line in enumerate(lines) if line == marker]
    if len(starts) != 1:
        raise AssertionError(f"{workflow_path}: expected one build-and-verify step, found {len(starts)}")
    start = starts[0]
    end = next(
        (index for index in range(start + 1, len(lines))
         if lines[index].startswith("      - name: ")),
        len(lines),
    )
    step_lines = lines[start + 1:end]
    try:
        run_index = step_lines.index("        run: |")
    except ValueError as exc:
        raise AssertionError(f"{workflow_path}: build step must use a literal run block") from exc
    run_lines = []
    for line in step_lines[run_index + 1:]:
        if not line.strip():
            run_lines.append("")
        elif line.startswith("          "):
            run_lines.append(line[10:])
        else:
            break
    return "\n".join(run_lines).rstrip() + "\n"


class WorkflowShellTests(unittest.TestCase):
    def test_all_build_steps_have_valid_bash_and_no_doubled_continuations(self):
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow):
                run = build_step(workflow)
                result = subprocess.run(["bash", "-n"], input=run, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("printf '%s\\n'", run)
                self.assertFalse(
                    any(line.rstrip().endswith("\\\\") for line in run.splitlines()),
                    f"{workflow} contains a doubled-backslash line continuation",
                )

    def _run_build_step(self, fake_build_body: str):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "scripts").mkdir()
            shutil.copy2(ROOT / "scripts/verify-build-outputs.py", root / "scripts/verify-build-outputs.py")
            (root / "VERSION").write_text("0.1.4\n", encoding="utf-8")
            fake_build = root / "scripts/build-macos-app.sh"
            fake_build.write_text(fake_build_body, encoding="utf-8")
            fake_build.chmod(0o755)

            run = build_step(".github/workflows/build-macos.yml")
            env = os.environ.copy()
            env["GITHUB_WORKSPACE"] = str(root)
            env["BUILD_OUTPUT_DIR"] = str(root / "build/ci")
            result = subprocess.run(
                ["bash", "-c", run],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
            )
            status_file = root / "build/ci/BUILD-WORKFLOW-STATUS.txt"
            status = status_file.read_text(encoding="utf-8") if status_file.exists() else ""
            return result, status

    def test_build_step_success_creates_workflow_status(self):
        fake = r'''#!/usr/bin/env bash
set -Eeuo pipefail
out="$2"
mkdir -p "$out"
version="$(cat VERSION)"
app="Clash_Mac_Compile-v${version}-macos-arm64-unsigned.zip"
printf 'app' > "$out/$app"
printf '{"project_version":"%s","distribution_mode":"unsigned"}\n' "$version" > "$out/BUILD-METADATA.json"
printf '{"distribution_architecture_ready":true}\n' > "$out/VPN-ARCHITECTURE-REPORT.json"
printf 'checksum  %s\n' "$app" > "$out/SHA256SUMS.txt"
printf 'status=success\nexit_code=0\nversion=%s\n' "$version" > "$out/BUILD-SCRIPT-STATUS.txt"
printf 'project=Clash_Mac_Compile\nversion=%s\noutput_directory=%s\n' "$version" "$out" > "$out/BUILD-RUN-CONTEXT.txt"
python3 - "$out" "$version" "$app" <<'PY'
import json, sys
from pathlib import Path
out=Path(sys.argv[1]); version=sys.argv[2]; app=sys.argv[3]
required=[app,"BUILD-METADATA.json","VPN-ARCHITECTURE-REPORT.json","SHA256SUMS.txt"]
(out/"BUILD-OUTPUT-MANIFEST.json").write_text(json.dumps({
 "project_version":version,"app_artifact":app,"required_files":required
}),encoding="utf-8")
PY
'''
        result, status = self._run_build_step(fake)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("status=success", status)
        self.assertIn("exit_code=0", status)
        self.assertIn("BUILD-OUTPUT-MANIFEST.json", result.stdout)

    def test_build_step_failure_preserves_exit_code(self):
        fake = r'''#!/usr/bin/env bash
set -Eeuo pipefail
out="$2"
mkdir -p "$out"
printf 'status=failed\nexit_code=65\n' > "$out/BUILD-SCRIPT-STATUS.txt"
exit 65
'''
        result, status = self._run_build_step(fake)
        self.assertEqual(result.returncode, 65)
        self.assertIn("status=failed", status)
        self.assertIn("exit_code=65", status)


if __name__ == "__main__":
    unittest.main()
