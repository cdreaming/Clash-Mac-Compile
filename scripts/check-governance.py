#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,subprocess,sys
from pathlib import Path

SEMVER=re.compile(r"^\d+\.\d+\.\d+$")
EXCLUDED={".git",".dev-state","dist","build","tmp","__pycache__",".pytest_cache",".venv","venv"}

def root_dir(): return Path(__file__).resolve().parents[1]
def warn(items,msg):
    items.append(msg); print(f"WARNING: {msg}",file=sys.stderr)
def mark(text,key,default=None):
    m=re.search(rf"<!--\s*{re.escape(key)}:\s*([^>]+?)\s*-->",text)
    return m.group(1).strip() if m else default
def previous(root,current):
    cur=tuple(map(int,current.split("."))); found=[]
    for p in (root/"docs/releases").glob("v*"):
        if p.is_dir() and SEMVER.fullmatch(p.name[1:]):
            v=tuple(map(int,p.name[1:].split(".")))
            if v<cur: found.append((v,p))
    return sorted(found)[-1][1] if found else None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--scope",choices=["development","candidate","release","archive"],required=True)
    ap.add_argument("--override-governance",action="store_true")
    ap.add_argument("--override-reason",default="")
    a=ap.parse_args(); root=root_dir(); warnings=[]
    try:
        if a.override_governance and not a.override_reason.strip():
            raise RuntimeError("使用 --override-governance 必须填写 --override-reason")
        for rel in ["README.md","AGENTS.md","VERSION","TEMPLATE_VERSION",".ai/AI-START-HERE.md",".ai/PROJECT-PROFILE.json"]:
            if not (root/rel).is_file(): raise RuntimeError(f"缺少关键机器文件: {rel}")
        version=(root/"VERSION").read_text().strip()
        tver=(root/"TEMPLATE_VERSION").read_text().strip()
        if not SEMVER.fullmatch(version) or not SEMVER.fullmatch(tver): raise RuntimeError("VERSION/TEMPLATE_VERSION 非 semver")
        revision=int((root/"RELEASE_REVISION").read_text().strip()) if (root/"RELEASE_REVISION").is_file() else 0
        if revision<0: raise RuntimeError("RELEASE_REVISION 不能为负数")
        profile=json.loads((root/".ai/PROJECT-PROFILE.json").read_text(encoding="utf-8"))
        if "quality" not in profile or "release" not in profile: raise RuntimeError("PROJECT-PROFILE 缺少 quality/release")
        dual=profile.get("release",{}).get("macos_dual_implementation",{})
        if dual.get("enabled"):
            preview=str(dual.get("preview_variant","")).strip()
            if not preview: raise RuntimeError("macos_dual_implementation 缺少 preview_variant")
            delivery=dual.get("preview_delivery") or {}
            for key in ["portable_build_command","portable_asset","shared_app_builder","toolchain_version"]:
                if not str(delivery.get(key,"")).strip():
                    raise RuntimeError(f"macos_dual_implementation.preview_delivery 缺少 {key}")
            if delivery.get("source_required") is not True or delivery.get("portable_installer_required") is not True:
                raise RuntimeError("macos_dual_implementation 要求源码 + portable installer 双交付")
            lock=dual.get("release_lock") or {}
            if lock.get("required") is not True or not str(lock.get("path","")).strip() or not str(lock.get("check_command","")).strip():
                raise RuntimeError("macos_dual_implementation 必须配置 release lock path/check_command")
            variants=dual.get("github_pkg_variants") or []
            if len(variants)!=2: raise RuntimeError("macos_dual_implementation 必须声明两个 GitHub PKG variants")
            names=[str(v.get("name","")).strip() for v in variants]
            if not all(names) or len(set(names))!=2 or preview not in names:
                raise RuntimeError("GitHub PKG variant 名称必须唯一，并包含 preview_variant")
            for v in variants:
                if not str(v.get("build_command","")).strip() or not str(v.get("asset_pattern","")).strip().endswith(".pkg"):
                    raise RuntimeError("每个 GitHub PKG variant 必须配置 build_command 和 .pkg asset_pattern")
            if dual.get("manual_approval_before_github_release") not in {True,False}:
                raise RuntimeError("manual_approval_before_github_release 必须是 boolean")
            # Candidate/release 阶段要求共享 builder 与 lock 实体存在；development 允许先配置后创建。
            if a.scope in {"candidate","release"}:
                for rel,label in [(delivery["shared_app_builder"],"shared_app_builder"),(lock["path"],"release lock")]:
                    if not (root/rel).is_file(): raise RuntimeError(f"macOS 双实现 {label} 不存在: {rel}")

        base=root/"docs/releases"/f"v{version}"
        if not base.is_dir(): raise RuntimeError(f"当前版本目录不存在: docs/releases/v{version}")
        cp=base/"RELEASE-CHECKLIST.md"; jp=base/"DEVELOPMENT-JOURNAL.md"
        checklist=cp.read_text(encoding="utf-8") if cp.is_file() else ""
        journal=jp.read_text(encoding="utf-8") if jp.is_file() else ""
        ready=mark(checklist,"RELEASE-READY-STATUS","auto")
        archive=mark(checklist,"RELEASE-ARCHIVE-STATUS","pending")
        mode=mark(checklist,"REPUBLISH-MODE","none")
        check_rev=int(mark(checklist,"RELEASE-REVISION",str(revision)))
        dev=mark(journal,"DEVELOPMENT-SESSION-STATUS","active")
        if check_rev!=revision: raise RuntimeError("RELEASE_REVISION 与 Release Checklist 不一致")

        # Advisory governance checks: they must not lock development.
        for script,label in [
            ("scripts/update-repository-structure.py","Repository Structure"),
            ("scripts/build-source-manifest.py","Source manifest"),
        ]:
            if (root/script).is_file():
                r=subprocess.run([sys.executable,script,"--check"],cwd=root,text=True,capture_output=True)
                if r.returncode: warn(warnings,f"{label} 已漂移；请在收尾同步，但不会锁死开发/发布。")
        prev=previous(root,version)
        if prev:
            t=(prev/"RELEASE-CHECKLIST.md").read_text(encoding="utf-8") if (prev/"RELEASE-CHECKLIST.md").is_file() else ""
            state=mark(t,"RELEASE-ARCHIVE-STATUS","unknown")
            if state=="pending": warn(warnings,f"上一版本 {prev.name} 仍 pending；不会阻止当前版本。")
            elif state in {"superseded","abandoned","failed"}:
                print(f"INFO: 上一版本 {prev.name} 已闭环为 {state}。",file=sys.stderr)

        if dev!="complete" and a.scope in {"candidate","release"}:
            warn(warnings,"Development Journal 尚未 complete；这是治理记录，不锁死 candidate/release。")
        if ready=="draft" and a.scope=="release":
            if a.override_governance: warn(warnings,f"用户 override draft：{a.override_reason}")
            else: raise RuntimeError("RELEASE-READY-STATUS=draft；用户确认后可 --override-governance --override-reason")
        if a.scope=="release":
            if archive!="pending": raise RuntimeError("当前版本不是 pending；已发布版本请先运行 prepare-republish.py")
            if mode=="none" and revision!=0: raise RuntimeError("REPUBLISH-MODE=none 但 RELEASE_REVISION 非 0")
            if mode in {"revision","force-overwrite"} and revision<1: raise RuntimeError("重发模式要求 RELEASE_REVISION>=1")
        if a.scope=="archive" and archive!="complete": raise RuntimeError("archive scope 要求 complete")

        print(f"Governance gate ({a.scope}): OK with {len(warnings)} warning(s)")
        return 0
    except Exception as e:
        print(f"Governance gate ({a.scope}): FAILED: {e}",file=sys.stderr); return 1
if __name__=="__main__": raise SystemExit(main())
