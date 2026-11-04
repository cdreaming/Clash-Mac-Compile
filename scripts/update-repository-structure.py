#!/usr/bin/env python3
from __future__ import annotations
import argparse, fnmatch, json, os, sys
from pathlib import Path

EXCLUDED_DIRS={".git",".dev-state","dist","build","tmp","__pycache__",".pytest_cache",".venv","venv"}
EXCLUDED_FILES={".DS_Store"}

def root_dir(): return Path(__file__).resolve().parents[1]
def load_catalog(root): return json.loads((root/".ai/REPOSITORY-CATALOG.json").read_text(encoding="utf-8"))

def actual_files(root):
    out=[]
    for p in root.rglob("*"):
        if not p.is_file(): continue
        rel=p.relative_to(root)
        if any(x in EXCLUDED_DIRS for x in rel.parts) or p.name in EXCLUDED_FILES: continue
        out.append(rel.as_posix())
    return sorted(out)

def actual_dirs(files):
    out=set()
    for rel in files:
        parts=rel.split("/")[:-1]
        for i in range(1,len(parts)+1): out.add("/".join(parts[:i])+"/")
    return sorted(out)

def resolve(path,exact,patterns):
    if path in exact: return exact[path]
    for x in patterns:
        if fnmatch.fnmatch(path,x["glob"]): return x["description"]
    return None

def sync(root,catalog,files,dirs):
    changed=0
    fe=catalog.setdefault("files",{}); de=catalog.setdefault("folders",{})
    for rel in files:
        if resolve(rel,fe,catalog.get("file_patterns",[])) is None:
            fe[rel]="TODO: 请填写该文件的具体职责、输入输出和关键风险。"; changed+=1
    for rel in dirs:
        if resolve(rel,de,catalog.get("folder_patterns",[])) is None:
            de[rel]="TODO: 请填写该目录保存什么内容、由谁维护以及生命周期。"; changed+=1
    for rel in list(fe):
        if rel not in files: del fe[rel]; changed+=1
    for rel in list(de):
        if rel not in dirs: del de[rel]; changed+=1
    if changed:
        p=root/".ai/REPOSITORY-CATALOG.json"; tmp=p.with_suffix(".tmp")
        tmp.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); os.replace(tmp,p)
    return changed

def render(catalog,files,dirs):
    fe=catalog.get("files",{}); de=catalog.get("folders",{})
    fp=catalog.get("file_patterns",[]); dp=catalog.get("folder_patterns",[])
    missing=[]
    for rel in files:
        d=resolve(rel,fe,fp)
        if not d or d.startswith("TODO:"): missing.append(rel)
    for rel in dirs:
        d=resolve(rel,de,dp)
        if not d or d.startswith("TODO:"): missing.append(rel)
    if missing: raise ValueError("以下路径缺少详细职责说明：\n- "+"\n- ".join(missing))

    lines=["# Repository Structure","",
           "> 本文件由 `scripts/update-repository-structure.py` 从真实文件系统和 `.ai/REPOSITORY-CATALOG.json` 生成。每次开发新增、删除、移动文件都必须更新。","",
           "## 目录与文件",""]
    children={}
    for d in dirs:
        p=d.rstrip("/"); parent="/".join(p.split("/")[:-1]); children.setdefault(parent,[]).append((p,True))
    for f in files:
        parent="/".join(f.split("/")[:-1]); children.setdefault(parent,[]).append((f,False))
    def walk(parent,prefix=""):
        uniq=[]; seen=set()
        for item in children.get(parent,[]):
            if item not in seen: seen.add(item); uniq.append(item)
        uniq.sort(key=lambda x:(not x[1],x[0].lower()))
        for i,(path,is_dir) in enumerate(uniq):
            last=i==len(uniq)-1
            key=path+("/" if is_dir else "")
            desc=resolve(key,de if is_dir else fe,dp if is_dir else fp)
            name=path.split("/")[-1]+("/" if is_dir else "")
            lines.append(f"`{prefix}{'└── ' if last else '├── '}{name}` — {desc}")
            if is_dir: walk(path,prefix+("    " if last else "│   "))
    walk("")
    lines += ["","## 维护规则","",
              "1. 新文件先执行 `--sync`，未登记路径会写成 `TODO`。",
              "2. AI 必须把所有 `TODO` 改成真实职责说明。",
              "3. 再执行 `--write` 生成本文件。",
              "4. CI 使用 `--check` 验证完全一致。",""]
    return "\n".join(lines)

def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--sync",action="store_true"); g.add_argument("--write",action="store_true"); g.add_argument("--check",action="store_true")
    a=ap.parse_args(); root=root_dir(); cat=load_catalog(root); files=actual_files(root); dirs=actual_dirs(files)
    if a.sync:
        n=sync(root,cat,files,dirs); print(f"Repository catalog sync: {n} change(s).")
        if n: print("请填写新增 TODO 描述，再执行 --write。")
        return 0
    expected=render(cat,files,dirs); out=root/"docs/REPOSITORY-STRUCTURE.md"
    if a.write:
        out.write_text(expected,encoding="utf-8"); print("Repository structure written."); return 0
    if not out.is_file() or out.read_text(encoding="utf-8")!=expected:
        print("Repository structure is stale. Run --write.",file=sys.stderr); return 1
    print("Repository structure: OK"); return 0

if __name__=="__main__": raise SystemExit(main())
