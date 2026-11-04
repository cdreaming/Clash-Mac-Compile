#!/usr/bin/env python3
from __future__ import annotations
import argparse, os, re, subprocess, sys
from datetime import datetime,timezone
from pathlib import Path

def root_dir(): return Path(__file__).resolve().parents[1]
def atomic(path,text):
    tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(text,encoding="utf-8"); os.replace(tmp,path)
def get(text,key):
    m=re.search(rf"<!--\s*{re.escape(key)}:\s*([^>]+?)\s*-->",text)
    if not m: raise RuntimeError(f"缺少 {key}")
    return m.group(1).strip()
def setm(text,key,value):
    out,n=re.subn(rf"(<!--\s*{re.escape(key)}:\s*)[^>]+?(\s*-->)",rf"\g<1>{value}\g<2>",text,count=1)
    if n!=1: raise RuntimeError(f"无法更新 {key}")
    return out
def append_cp(text,stage,done,next_step,verify):
    nums=[int(x) for x in re.findall(r"(?m)^### CP-(\d+)",text)]
    cp=f"CP-{max(nums,default=0)+1:03d}"; now=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    block=f"""### {cp} · {stage}

- 时间：{now}
- 已完成：{done}
- 下一步：{next_step}
- 验证状态：{verify}

"""
    if "## 完成摘要" not in text: raise RuntimeError("开发日志缺少完成摘要")
    return setm(text.replace("## 完成摘要",block+"## 完成摘要",1),"DEVELOPMENT-LAST-CHECKPOINT",cp),cp
def paths(root):
    v=(root/"VERSION").read_text().strip(); base=root/"docs/releases"/f"v{v}"
    return base/"DEVELOPMENT-JOURNAL.md",base/"RELEASE-CHECKLIST.md"

def main():
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest="cmd",required=True)
    p=sp.add_parser("start"); p.add_argument("--goal",required=True)
    p=sp.add_parser("checkpoint"); p.add_argument("--stage",required=True); p.add_argument("--done",required=True); p.add_argument("--next",dest="next_step",required=True); p.add_argument("--verification",required=True)
    p=sp.add_parser("complete"); p.add_argument("--source",default="ai-delivery"); p.add_argument("--summary",default="当前源码快照已完成 AI 开发与本地验证。")
    sp.add_parser("status")
    a=ap.parse_args(); root=root_dir(); j,c=paths(root); text=j.read_text(encoding="utf-8")
    if a.cmd=="status":
        for k in ["DEVELOPMENT-SESSION-STATUS","DEVELOPMENT-LAST-CHECKPOINT","DEVELOPMENT-COMPLETION-SOURCE"]: print(f"{k}={get(text,k)}")
        return 0
    if a.cmd=="start":
        if "<!-- RELEASE-ARCHIVE-STATUS: complete -->" in c.read_text(encoding="utf-8"):
            print("WARNING: 已发布版本允许重新开发；再次 Release 前必须运行 prepare-republish.py。",file=sys.stderr)
        text=setm(setm(text,"DEVELOPMENT-SESSION-STATUS","active"),"DEVELOPMENT-COMPLETION-SOURCE","pending")
        text,cp=append_cp(text,"开始/重新打开开发",f"目标：{a.goal}","按风险等级开发和验证","开发状态 active")
        atomic(j,text); print("Started",cp); return 0
    if a.cmd=="checkpoint":
        text,cp=append_cp(text,a.stage,a.done,a.next_step,a.verification); atomic(j,text); print("Checkpoint",cp); return 0
    if a.cmd=="complete":
        r=subprocess.run([sys.executable,"scripts/check-governance.py","--scope","development"],cwd=root)
        if r.returncode: return r.returncode
        if get(text,"DEVELOPMENT-SESSION-STATUS")=="complete": print("Development already complete."); return 0
        text,cp=append_cp(text,"自动完成开发阶段",a.summary,"进入 candidate gate / 用户本地测试 / GitHub CI","development gate 已通过")
        text=setm(setm(text,"DEVELOPMENT-SESSION-STATUS","complete"),"DEVELOPMENT-COMPLETION-SOURCE",a.source)
        text=re.sub(r"(?s)(## 完成摘要\n).*",rf"\1\n{a.summary}\n\n完成来源：`{a.source}`。该状态不等于 GitHub Release 已发布。\n",text,count=1)
        atomic(j,text); print("Development complete",cp); return 0
if __name__=="__main__": raise SystemExit(main())
