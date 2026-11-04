#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path

EXCLUDE={".git",".dev-state","dist","build","tmp",".venv","venv","__pycache__",".pytest_cache"}

def copy_clean(src,dst):
    for p in src.rglob("*"):
        rel=p.relative_to(src)
        if any(x in EXCLUDE for x in rel.parts): continue
        target=dst/rel
        if p.is_symlink(): raise RuntimeError(f"simulation 拒绝 symlink: {rel}")
        if p.is_dir(): target.mkdir(parents=True,exist_ok=True)
        elif p.is_file():
            target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,target)

def main():
    ap=argparse.ArgumentParser(description="Clean-room 真实环境近似模拟")
    ap.add_argument("--keep",action="store_true"); a=ap.parse_args()
    root=Path(__file__).resolve().parents[1]
    profile=json.loads((root/".ai/PROJECT-PROFILE.json").read_text(encoding="utf-8"))
    commands=profile["quality"]["commands"].get("simulation",[])
    if not profile["quality"].get("simulation_configured"):
        print("simulation_configured=false，必须先配置项目模拟。",file=sys.stderr); return 1
    if not commands:
        print("没有配置 simulation 命令。",file=sys.stderr); return 1

    tmp=Path(tempfile.mkdtemp(prefix="ai-project-sim-"))
    try:
        copy_clean(root,tmp); env=os.environ.copy(); env["AI_SIMULATION"]="1"
        print(f"[SIMULATION] clean workspace: {tmp}")
        for i,cmd in enumerate(commands,1):
            print(f"[SIMULATION {i}/{len(commands)}] {cmd}")
            rc=subprocess.run(cmd,cwd=tmp,shell=True,executable="/bin/bash",env=env).returncode
            if rc: print(f"Simulation failed: {cmd} -> {rc}",file=sys.stderr); return rc
        print("Clean-room simulation: OK"); return 0
    finally:
        if a.keep: print("Preserved:",tmp)
        else: shutil.rmtree(tmp,ignore_errors=True)
if __name__=="__main__": raise SystemExit(main())
