#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, sys
from pathlib import Path

EXCLUDED_DIRS={".git",".dev-state","dist","build","tmp","__pycache__",".pytest_cache",".venv","venv"}
EXCLUDED_NAMES={"SHA256SUMS.txt",".DS_Store"}

def root_dir(): return Path(__file__).resolve().parents[1]
def sensitive(rel):
    low=rel.as_posix().lower()
    return rel.name==".env" or "/.env." in "/"+low or low.endswith((".secret",".token",".key",".pem")) or any(x.lower() in {"secrets","credentials","runtime"} for x in rel.parts)

def source_files(root):
    out=[]
    for p in root.rglob("*"):
        rel=p.relative_to(root)
        if p.is_symlink() and not any(x in EXCLUDED_DIRS for x in rel.parts):
            raise RuntimeError(f"源码中禁止 symlink: {rel}")
        if not p.is_file(): continue
        if any(x in EXCLUDED_DIRS for x in rel.parts) or p.name in EXCLUDED_NAMES: continue
        if sensitive(rel): raise RuntimeError(f"敏感路径进入源码集合: {rel}")
        out.append(p)
    return sorted(out,key=lambda p:p.relative_to(root).as_posix())

def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def expected(root):
    return "".join(f"{digest(p)}  {p.relative_to(root).as_posix()}\n" for p in source_files(root))

def main():
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true"); g.add_argument("--check",action="store_true")
    a=ap.parse_args(); root=root_dir(); target=root/"SHA256SUMS.txt"
    try: text=expected(root)
    except Exception as e: print(e,file=sys.stderr); return 1
    if a.write:
        target.write_text(text,encoding="utf-8"); target.chmod(0o644); print(f"Source manifest: {text.count(chr(10))} files"); return 0
    if not target.is_file() or target.read_text(encoding="utf-8")!=text:
        print("SHA256SUMS.txt is stale. Run --write.",file=sys.stderr); return 1
    print("Source manifest: OK"); return 0
if __name__=="__main__": raise SystemExit(main())
