from __future__ import annotations
import hashlib,json,subprocess,sys,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r=subprocess.run([sys.executable,"scripts/build-release.py"],cwd=ROOT,text=True,capture_output=True)
        if r.returncode: raise AssertionError(r.stdout+r.stderr)
        cls.m=json.loads((ROOT/"dist/RELEASE-MANIFEST.json").read_text())
        src=[x for x in cls.m["assets"] if x.endswith("-source.zip")]
        if len(src)!=1: raise AssertionError(src)
        cls.z=ROOT/"dist"/src[0]
    def test_zip_integrity(self):
        with zipfile.ZipFile(self.z) as z: self.assertIsNone(z.testzip())
    def test_no_runtime_secrets(self):
        with zipfile.ZipFile(self.z) as z: names=[x.filename.lower() for x in z.infolist()]
        for n in names:
            self.assertNotIn("/.dev-state/",n); self.assertNotIn("/runtime/",n)
            self.assertFalse(n.endswith((".secret",".token",".key",".pem")))
    def test_manifest_asset_set(self):
        actual={p.name for p in (ROOT/"dist").iterdir() if p.is_file()}
        self.assertEqual(set(self.m["assets"]),actual)
    def test_checksums(self):
        for line in (ROOT/"dist/SHA256SUMS.txt").read_text().splitlines():
            h,n=line.split(maxsplit=1); p=ROOT/"dist"/n.strip()
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),h)
    def test_deterministic_source(self):
        first=hashlib.sha256(self.z.read_bytes()).hexdigest()
        r=subprocess.run([sys.executable,"scripts/build-release.py"],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        m=json.loads((ROOT/"dist/RELEASE-MANIFEST.json").read_text()); src=[x for x in m["assets"] if x.endswith("-source.zip")][0]
        self.assertEqual(first,hashlib.sha256((ROOT/"dist"/src).read_bytes()).hexdigest())
    def test_revision_metadata(self):
        for k in ["project_version","release_revision","republish_mode","expected_tag"]: self.assertIn(k,self.m)
if __name__=="__main__": unittest.main()
