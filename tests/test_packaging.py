from __future__ import annotations
import hashlib,json,subprocess,sys,unittest,zipfile,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest_path = ROOT / "dist/RELEASE-MANIFEST.json"
        if not manifest_path.is_file():
            r=subprocess.run([sys.executable,"scripts/build-release.py"],cwd=ROOT,text=True,capture_output=True)
            if r.returncode: raise AssertionError(r.stdout+r.stderr)
        cls.m=json.loads(manifest_path.read_text())
        src=[x for x in cls.m["assets"] if x.endswith("_source.zip")]
        if len(src)!=1: raise AssertionError(src)
        cls.z=ROOT/"dist"/src[0]
    def test_zip_integrity(self):
        with zipfile.ZipFile(self.z) as z: self.assertIsNone(z.testzip())
    def test_no_runtime_secrets(self):
        with zipfile.ZipFile(self.z) as z: names=[x.filename.lower() for x in z.infolist()]
        for n in names:
            self.assertNotIn("/.dev-state/",n); self.assertNotIn("/runtime/",n)
            self.assertFalse(n.endswith((".secret",".token",".key",".pem",".p12",".pfx",".mobileprovision",".provisionprofile")))
    def test_manifest_asset_set(self):
        actual={p.name for p in (ROOT/"dist").iterdir() if p.is_file()}
        self.assertEqual(set(self.m["assets"]),actual)
    def test_checksums(self):
        for line in (ROOT/"dist/SHA256SUMS.txt").read_text().splitlines():
            h,n=line.split(maxsplit=1); p=ROOT/"dist"/n.strip()
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),h)
    def test_deterministic_source(self):
        with tempfile.TemporaryDirectory() as td:
            copy=Path(td)/"repo"
            ignore=shutil.ignore_patterns(".git",".dev-state","dist","build","tmp",
                                          "__pycache__",".pytest_cache",".venv","venv")
            shutil.copytree(ROOT,copy,ignore=ignore)

            first_run=subprocess.run([sys.executable,"scripts/build-release.py"],
                                     cwd=copy,text=True,capture_output=True)
            self.assertEqual(first_run.returncode,0,first_run.stdout+first_run.stderr)
            first_manifest=json.loads((copy/"dist/RELEASE-MANIFEST.json").read_text())
            first_src=[x for x in first_manifest["assets"] if x.endswith("_source.zip")][0]
            first=hashlib.sha256((copy/"dist"/first_src).read_bytes()).hexdigest()

            second_run=subprocess.run([sys.executable,"scripts/build-release.py"],
                                      cwd=copy,text=True,capture_output=True)
            self.assertEqual(second_run.returncode,0,second_run.stdout+second_run.stderr)
            second_manifest=json.loads((copy/"dist/RELEASE-MANIFEST.json").read_text())
            second_src=[x for x in second_manifest["assets"] if x.endswith("_source.zip")][0]
            second=hashlib.sha256((copy/"dist"/second_src).read_bytes()).hexdigest()
            self.assertEqual(first,second)
    def test_revision_metadata(self):
        for k in ["project_version","release_revision","republish_mode","expected_tag"]: self.assertIn(k,self.m)
if __name__=="__main__": unittest.main()
