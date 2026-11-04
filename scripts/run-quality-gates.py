#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path
ORDER=["static","unit","integration","smoke","security"]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--scope",choices=["development","candidate","release"],required=True)
    ap.add_argument("--override-governance",action="store_true")
    ap.add_argument("--override-quality-config",action="store_true")
    ap.add_argument("--override-reason",default="")
    a=ap.parse_args(); root=Path(__file__).resolve().parents[1]
    if (a.override_governance or a.override_quality_config) and not a.override_reason.strip():
        print("override 必须填写 --override-reason",file=sys.stderr); return 2

    gov=[sys.executable,"scripts/check-governance.py","--scope",a.scope]
    if a.override_governance: gov += ["--override-governance","--override-reason",a.override_reason]
    if subprocess.run(gov,cwd=root).returncode: return 1

    p=json.loads((root/".ai/PROJECT-PROFILE.json").read_text(encoding="utf-8"))
    q=p["quality"]
    if a.scope in {"candidate","release"}:
        missing=[]
        if not q.get("project_tests_configured"): missing.append("项目真实测试")
        if not q.get("simulation_configured"): missing.append("simulation")
        if missing and not a.override_quality_config:
            print("未配置: "+", ".join(missing)+"；默认阻止。用户确认后可 --override-quality-config --override-reason。",file=sys.stderr); return 1
        if missing:
            print("WARNING: 用户显式 override 未配置项："+", ".join(missing)+f"；原因：{a.override_reason}",file=sys.stderr)

    ran=0
    for kind in ORDER:
        for cmd in q.get("commands",{}).get(kind,[]):
            ran+=1; print(f"[GATE:{kind}] {cmd}")
            rc=subprocess.run(cmd,cwd=root,shell=True,executable="/bin/bash").returncode
            if rc:
                print(f"REAL TEST FAILURE: {kind}: {cmd}",file=sys.stderr); return rc

    if a.scope in {"candidate","release"} and q.get("simulation_configured"):
        rc=subprocess.run([sys.executable,"scripts/run-simulated-environment.py"],cwd=root).returncode
        if rc: return rc
    if a.scope in {"candidate","release"} and ran==0 and not a.override_quality_config:
        print("没有任何真实质量命令，拒绝把空测试当通过。",file=sys.stderr); return 1
    print(f"Quality gates ({a.scope}): OK"); return 0
if __name__=="__main__": raise SystemExit(main())
