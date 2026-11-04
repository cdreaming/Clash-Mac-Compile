#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,shutil,subprocess,sys,zipfile
from pathlib import Path
FIXED=(2020,1,1,0,0,0)
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def zi(name,ex=False):
    z=zipfile.ZipInfo(name,FIXED); z.compress_type=zipfile.ZIP_DEFLATED; z.create_system=3
    z.external_attr=((0o755 if ex else 0o644)&0xFFFF)<<16; return z
def run(root,*cmd):
    print("[HANDOFF]"," ".join(map(str,cmd))); subprocess.check_call(list(map(str,cmd)),cwd=root)
def main():
    root=Path(__file__).resolve().parents[1]; v=(root/"VERSION").read_text().strip(); tv=(root/"TEMPLATE_VERSION").read_text().strip()
    rev=int((root/"RELEASE_REVISION").read_text().strip()) if (root/"RELEASE_REVISION").is_file() else 0
    suffix=f"-r{rev}" if rev>0 else ""
    profile=json.loads((root/".ai/PROJECT-PROFILE.json").read_text(encoding="utf-8")); slug=profile["project_slug"]
    run(root,sys.executable,"scripts/check-governance.py","--scope","development")
    run(root,sys.executable,"scripts/dev-session.py","complete","--source","ai-delivery",
        "--summary","AI 已完成本轮源码、文档与验证，进入用户本地测试和 GitHub CI 阶段。")
    run(root,sys.executable,"scripts/update-repository-structure.py","--write")
    run(root,sys.executable,"scripts/build-source-manifest.py","--write")
    run(root,sys.executable,"scripts/run-quality-gates.py","--scope","candidate")
    run(root,sys.executable,"scripts/build-release.py")
    run(root,sys.executable,"-m","unittest","-q","tests.test_packaging")
    dist=root/"dist"; hand=dist/"handoff"; hand.mkdir(parents=True,exist_ok=True)
    rm=json.loads((dist/"RELEASE-MANIFEST.json").read_text(encoding="utf-8"))
    sources=[x for x in rm["assets"] if x.endswith("-source.zip")]
    if len(sources)!=1: raise RuntimeError("无法唯一确定 source ZIP")
    project=hand/f"{slug}-project-source-v{v}{suffix}.zip"; shutil.copy2(dist/sources[0],project)
    tm=json.loads((root/".ai/TEMPLATE-MANIFEST.json").read_text(encoding="utf-8"))
    gov=hand/f"governance-template-v{tv}.zip"
    with zipfile.ZipFile(gov,"w") as z:
        for rel in tm["include"]:
            p=root/rel
            if not p.is_file(): raise RuntimeError(f"模板清单不存在: {rel}")
            ex=p.suffix==".sh" or (rel.startswith("scripts/") and p.suffix==".py")
            z.writestr(zi(rel,ex),p.read_bytes())
    (hand/"HANDOFF.md").write_text(
        f"# AI Handoff\n\n- Project version: {v}\n- Release revision: {rev}\n- Template version: {tv}\n- Expected tag: {rm['expected_tag']}\n",
        encoding="utf-8")
    (hand/"HANDOFF-SHA256SUMS.txt").write_text(f"{sha(project)}  {project.name}\n{sha(gov)}  {gov.name}\n",encoding="utf-8")
    combo=hand/f"{slug}-ai-handoff-v{v}{suffix}.zip"
    with zipfile.ZipFile(combo,"w") as z:
        for p in [project,gov,hand/"HANDOFF.md",hand/"HANDOFF-SHA256SUMS.txt"]: z.writestr(zi(p.name),p.read_bytes())
    print("AI handoff complete:",project.name,gov.name,combo.name); return 0
if __name__=="__main__":
    try: raise SystemExit(main())
    except subprocess.CalledProcessError as e: raise SystemExit(e.returncode)
