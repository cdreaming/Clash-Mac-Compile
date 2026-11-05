#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,shutil,subprocess,sys,zipfile
from pathlib import Path
EXCLUDED={".git",".dev-state","dist","build","tmp",".venv","venv","__pycache__",".pytest_cache"}
FIXED=(2020,1,1,0,0,0)
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def marker(t,k,d):
    m=re.search(rf"<!--\s*{re.escape(k)}:\s*([^>]+?)\s*-->",t); return m.group(1).strip() if m else d
def sensitive(rel):
    low=rel.as_posix().lower()
    return rel.name==".env" or "/.env." in "/"+low or low.endswith((".secret",".token",".key",".pem",".p12",".pfx",".mobileprovision",".provisionprofile")) or any(x.lower() in {"secrets","credentials","runtime"} for x in rel.parts)
def zi(name,ex=False):
    z=zipfile.ZipInfo(name,FIXED); z.compress_type=zipfile.ZIP_DEFLATED; z.create_system=3
    z.external_attr=((0o755 if ex else 0o644)&0xFFFF)<<16; return z
def main():
    root=Path(__file__).resolve().parents[1]; version=(root/"VERSION").read_text().strip()
    revision=int((root/"RELEASE_REVISION").read_text().strip()) if (root/"RELEASE_REVISION").is_file() else 0
    check=(root/"docs/releases"/f"v{version}"/"RELEASE-CHECKLIST.md").read_text(encoding="utf-8")
    mode=marker(check,"REPUBLISH-MODE","none")
    suffix=f"-r{revision}" if revision>0 else ""
    tag=f"v{version}-r{revision}" if mode=="revision" and revision>0 else f"v{version}"
    profile=json.loads((root/".ai/PROJECT-PROFILE.json").read_text(encoding="utf-8")); slug=profile["project_slug"]
    dist=root/"dist"
    if dist.exists(): shutil.rmtree(dist)
    dist.mkdir()
    files=[]
    for p in root.rglob("*"):
        rel=p.relative_to(root)
        if p.is_symlink() and not any(x in EXCLUDED for x in rel.parts): raise RuntimeError(f"Release 拒绝 symlink: {rel}")
        if not p.is_file() or any(x in EXCLUDED for x in rel.parts): continue
        if sensitive(rel): raise RuntimeError(f"Release 拒绝敏感文件: {rel}")
        files.append(p)
    files.sort(key=lambda p:p.relative_to(root).as_posix())
    package=f"{profile['project_name']}_v{version}{suffix}_source.zip"; top=f"{profile['project_name']}_v{version}{suffix}"
    with zipfile.ZipFile(dist/package,"w") as z:
        for p in files:
            rel=p.relative_to(root).as_posix()
            ex=p.suffix==".sh" or (rel.startswith("scripts/") and p.suffix==".py")
            z.writestr(zi(f"{top}/{rel}",ex),p.read_bytes())
    validation=f"release_v{version}{suffix}_validation_zh-CN.md"
    shutil.copy2(root/"docs/releases"/f"v{version}"/"VALIDATION-REPORT.md",dist/validation)
    assets=[package,validation]; cfg=profile["release"]
    for cmd in cfg.get("build_commands",[]):
        print(f"[RELEASE:build] {cmd}")
        rc=subprocess.run(cmd,cwd=root,shell=True,executable="/bin/bash").returncode
        if rc: raise RuntimeError(f"Release build command failed ({rc}): {cmd}")
    if cfg.get("installer_required") and not cfg.get("installer_assets"): raise RuntimeError("installer_required=true 但 installer_assets 为空")
    for rel in list(cfg.get("installer_assets",[]))+list(cfg.get("extra_assets",[])):
        p=root/rel
        if not p.is_file(): raise RuntimeError(f"配置 Release 资产不存在: {rel}")
        shutil.copy2(p,dist/p.name); assets.append(p.name)
    all_assets=sorted(set(assets+["SHA256SUMS.txt","RELEASE-MANIFEST.json"]))
    manifest={"project":profile["project_name"],"project_version":version,"release_revision":revision,
              "republish_mode":mode,"expected_tag":tag,"assets":all_assets}
    (dist/"RELEASE-MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    sums=""
    for name in sorted(set(assets+["RELEASE-MANIFEST.json"])): sums+=f"{sha(dist/name)}  {name}\n"
    (dist/"SHA256SUMS.txt").write_text(sums,encoding="utf-8")
    with zipfile.ZipFile(dist/package) as z:
        bad=z.testzip()
        if bad: raise RuntimeError(f"ZIP CRC 失败: {bad}")
    print(f"Release state: version={version}, revision={revision}, mode={mode}, tag={tag}")
    return 0
if __name__=="__main__":
    try: raise SystemExit(main())
    except Exception as e: print(f"Build release failed: {e}",file=sys.stderr); raise SystemExit(1)
