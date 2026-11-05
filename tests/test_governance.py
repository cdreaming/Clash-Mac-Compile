from __future__ import annotations
import json,re,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
IGNORE=shutil.ignore_patterns(".git",".dev-state","dist","build","tmp","__pycache__",".pytest_cache",".venv","venv")
class GovernanceTests(unittest.TestCase):
    def run_cmd(self,*args,cwd=ROOT):
        return subprocess.run(list(args),cwd=cwd,text=True,capture_output=True)

    def test_development_governance_passes(self):
        r=self.run_cmd(sys.executable,"scripts/check-governance.py","--scope","development")
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_structure_current(self):
        r=self.run_cmd(sys.executable,"scripts/update-repository-structure.py","--check")
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)

    def test_structure_drift_is_warning_not_development_lock(self):
        with tempfile.TemporaryDirectory() as td:
            c=Path(td)/"repo"; shutil.copytree(ROOT,c,ignore=IGNORE)
            (c/"unexpected.txt").write_text("x")
            strict=self.run_cmd(sys.executable,"scripts/update-repository-structure.py","--check",cwd=c)
            self.assertNotEqual(strict.returncode,0)
            dev=self.run_cmd(sys.executable,"scripts/check-governance.py","--scope","development",cwd=c)
            self.assertEqual(dev.returncode,0,dev.stdout+dev.stderr)
            self.assertIn("WARNING",dev.stderr)

    def test_quality_config_requires_explicit_user_override(self):
        with tempfile.TemporaryDirectory() as td:
            c=Path(td)/"repo"; shutil.copytree(ROOT,c,ignore=IGNORE)
            pth=c/".ai/PROJECT-PROFILE.json"; p=json.loads(pth.read_text())
            p["quality"]["project_tests_configured"]=False
            p["quality"]["simulation_configured"]=False
            p["quality"]["commands"]={"static":["python3 -c \"print('ok')\""],"unit":[],"integration":[],"smoke":[],"security":[],"simulation":[]}
            pth.write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n")
            blocked=self.run_cmd(sys.executable,"scripts/run-quality-gates.py","--scope","candidate",cwd=c)
            self.assertNotEqual(blocked.returncode,0)
            allowed=self.run_cmd(sys.executable,"scripts/run-quality-gates.py","--scope","candidate",
                             "--override-quality-config","--override-reason","用户明确接受风险",cwd=c)
            self.assertEqual(allowed.returncode,0,allowed.stdout+allowed.stderr)

    def test_pending_previous_does_not_block_new_version_or_release_governance(self):
        with tempfile.TemporaryDirectory() as td:
            c=Path(td)/"repo"; shutil.copytree(ROOT,c,ignore=IGNORE)
            old=(c/"VERSION").read_text().strip()
            r=self.run_cmd(sys.executable,"scripts/prepare-version.py","--version","0.2.0","--risk","L2","--write",cwd=c)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            self.assertIn("WARNING",r.stderr)
            rel=self.run_cmd(sys.executable,"scripts/check-governance.py","--scope","release",cwd=c)
            self.assertEqual(rel.returncode,0,rel.stdout+rel.stderr)
            self.assertIn("上一版本",rel.stderr)

    def test_revision_republish_reopens_published_version(self):
        with tempfile.TemporaryDirectory() as td:
            c=Path(td)/"repo"; shutil.copytree(ROOT,c,ignore=IGNORE)
            v=(c/"VERSION").read_text().strip(); check=c/"docs/releases"/f"v{v}"/"RELEASE-CHECKLIST.md"
            t=check.read_text().replace("RELEASE-ARCHIVE-STATUS: pending","RELEASE-ARCHIVE-STATUS: complete")
            t=t.replace("- RELEASE-URL: pending","- RELEASE-URL: https://example.invalid/release")
            t=t.replace("- TAG-COMMIT: pending","- TAG-COMMIT: abcdef1234567")
            t=t.replace("- ASSET-SHA256-VERIFIED: no","- ASSET-SHA256-VERIFIED: yes")
            t=t.replace("- ONLINE-ASSETS-VERIFIED: no","- ONLINE-ASSETS-VERIFIED: yes")
            check.write_text(t)
            journal=check.parent/"DEVELOPMENT-JOURNAL.md"
            journal_text=journal.read_text(encoding="utf-8")
            journal_text=re.sub(r"(?m)^##[ \t]+完成摘要(?:[ \t].*)?\n?", "", journal_text)
            journal_text=re.sub(
                r"(?m)^<!-- DEVELOPMENT-(?:SESSION-STATUS|LAST-CHECKPOINT|COMPLETION-SOURCE):[^>]*-->\n?",
                "", journal_text
            )
            existing_checkpoints=[int(x) for x in re.findall(r"(?m)^### CP-(\d+)",journal_text)]
            expected_checkpoint=f"CP-{max(existing_checkpoints,default=0)+1:03d}"
            journal.write_text(journal_text,encoding="utf-8")
            r=self.run_cmd(sys.executable,"scripts/prepare-republish.py","--mode","revision","--reason","发布后补充代码","--write",cwd=c)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            self.assertEqual((c/"RELEASE_REVISION").read_text().strip(),"1")
            u=check.read_text()
            self.assertIn("REPUBLISH-MODE: revision",u)
            self.assertIn(f"RELEASE-TAG: v{v}-r1",u)
            self.assertTrue((check.parent/"REPUBLISH-HISTORY.md").is_file())
            repaired=journal.read_text(encoding="utf-8")
            self.assertIn("## 完成摘要",repaired)
            self.assertIn("DEVELOPMENT-SESSION-STATUS: active",repaired)
            self.assertIn(f"DEVELOPMENT-LAST-CHECKPOINT: {expected_checkpoint}",repaired)
            self.assertIn("DEVELOPMENT-COMPLETION-SOURCE: pending",repaired)
            self.assertIn("开始/重新打开开发",repaired)

    def test_republish_preflight_does_not_mutate_release_when_journal_missing(self):
        with tempfile.TemporaryDirectory() as td:
            c=Path(td)/"repo"; shutil.copytree(ROOT,c,ignore=IGNORE)
            v=(c/"VERSION").read_text().strip()
            check=c/"docs/releases"/f"v{v}"/"RELEASE-CHECKLIST.md"
            original=check.read_text(encoding="utf-8")
            check.write_text(original.replace("RELEASE-ARCHIVE-STATUS: pending",
                                              "RELEASE-ARCHIVE-STATUS: complete"),encoding="utf-8")
            journal=check.parent/"DEVELOPMENT-JOURNAL.md"
            journal.unlink()
            r=self.run_cmd(sys.executable,"scripts/prepare-republish.py","--mode","revision",
                           "--reason","验证 preflight", "--write",cwd=c)
            self.assertNotEqual(r.returncode,0)
            self.assertEqual((c/"RELEASE_REVISION").read_text().strip(),"0")
            self.assertIn("RELEASE-ARCHIVE-STATUS: complete",check.read_text(encoding="utf-8"))
            self.assertFalse((check.parent/"REPUBLISH-HISTORY.md").exists())

    def test_disposition_closes_unreleased_without_lock(self):
        with tempfile.TemporaryDirectory() as td:
            c=Path(td)/"repo"; shutil.copytree(ROOT,c,ignore=IGNORE)
            v=(c/"VERSION").read_text().strip()
            r=self.run_cmd(sys.executable,"scripts/set-release-disposition.py","--version",v,"--status","superseded",
                       "--reason","该候选未正式发布，由后续版本取代","--write",cwd=c)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            t=(c/"docs/releases"/f"v{v}"/"RELEASE-CHECKLIST.md").read_text()
            self.assertIn("RELEASE-ARCHIVE-STATUS: superseded",t)

    def test_dual_macos_profile_rejects_incomplete_config(self):
        with tempfile.TemporaryDirectory() as td:
            c=Path(td)/"repo"; shutil.copytree(ROOT,c,ignore=IGNORE)
            pth=c/".ai/PROJECT-PROFILE.json"; p=json.loads(pth.read_text())
            p["release"]["macos_dual_implementation"]["enabled"]=True
            pth.write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n")
            r=self.run_cmd(sys.executable,"scripts/check-governance.py","--scope","development",cwd=c)
            self.assertNotEqual(r.returncode,0)
            self.assertIn("macos_dual_implementation",r.stderr)

    def test_dual_macos_profile_accepts_shared_builder_and_two_pkg_variants(self):
        with tempfile.TemporaryDirectory() as td:
            c=Path(td)/"repo"; shutil.copytree(ROOT,c,ignore=IGNORE)
            (c/"scripts/dummy-preview-builder.sh").write_text("#!/bin/sh\nexit 0\n")
            (c/"GoWebUI-RELEASE-LOCK.json").write_text("{}\n")
            pth=c/".ai/PROJECT-PROFILE.json"; p=json.loads(pth.read_text())
            d=p["release"]["macos_dual_implementation"]
            d["enabled"]=True
            d["preview_delivery"].update({
                "portable_build_command":"bash scripts/build-portable-installer.sh",
                "portable_asset":"dist-portable/Product-v0.1.0-GoWebUI-arm64-portable-installer.zip",
                "shared_app_builder":"scripts/dummy-preview-builder.sh",
                "toolchain_version":"go1.23.2",
            })
            d["release_lock"].update({
                "path":"GoWebUI-RELEASE-LOCK.json",
                "check_command":"python3 scripts/check-lock.py --check",
            })
            d["github_pkg_variants"]=[
                {"name":"GoWebUI","build_command":"bash scripts/build-go.sh","asset_pattern":"*-GoWebUI-arm64.pkg"},
                {"name":"SwiftUI","build_command":"bash scripts/build-swift.sh","asset_pattern":"*-SwiftUI-arm64.pkg"},
            ]
            pth.write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n")
            r=self.run_cmd(sys.executable,"scripts/check-governance.py","--scope","candidate",cwd=c)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)

if __name__=="__main__": unittest.main()
