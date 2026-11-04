#!/usr/bin/env python3
from __future__ import annotations
import argparse,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path

def setm(t,k,v):
    out,n=re.subn(rf"(<!--\s*{re.escape(k)}:\s*)[^>]+?(\s*-->)",rf"\g<1>{v}\g<2>",t,count=1)
    if not n: out=t+f"\n<!-- {k}: {v} -->\n"
    return out
def field(t,k,v):
    out,n=re.subn(rf"(?m)^-\s*{re.escape(k)}:\s*.*$",f"- {k}: {v}",t,count=1)
    return out if n else t+f"\n- {k}: {v}\n"
def get(t,k,d=None):
    m=re.search(rf"<!--\s*{re.escape(k)}:\s*([^>]+?)\s*-->",t); return m.group(1).strip() if m else d

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=["revision","force-overwrite"],default="revision")
    ap.add_argument("--reason",required=True); ap.add_argument("--write",action="store_true")
    a=ap.parse_args(); root=Path(__file__).resolve().parents[1]
    v=(root/"VERSION").read_text().strip(); rp=root/"RELEASE_REVISION"
    rev=int(rp.read_text().strip()) if rp.is_file() else 0
    base=root/"docs/releases"/f"v{v}"; check=base/"RELEASE-CHECKLIST.md"
    t=check.read_text(encoding="utf-8")
    if get(t,"RELEASE-ARCHIVE-STATUS","pending")!="complete":
        print("当前版本未 complete，可直接继续开发；无需 prepare-republish。",file=sys.stderr); return 1
    nr=rev+1; tag=f"v{v}-r{nr}" if a.mode=="revision" else f"v{v}"
    print(f"Republish: mode={a.mode}, revision={nr}, tag={tag}")
    if not a.write: return 0

    # Repair/validate the development journal before changing release state.
    # This prevents a failed dev-session start from leaving checklist/revision half-mutated.
    subprocess.check_call(
        [sys.executable,"scripts/dev-session.py","validate"],
        cwd=root
    )

    hist=base/"REPUBLISH-HISTORY.md"
    if not hist.is_file(): hist.write_text("# Republish History\n\n保存每次重新发布前的真实证据。\n",encoding="utf-8")
    with hist.open("a",encoding="utf-8") as f:
        f.write(f"\n## r{nr} · {datetime.now(timezone.utc).isoformat()}\n\n- 模式：{a.mode}\n- 原因：{a.reason}\n- 目标 tag：{tag}\n")
        for k in ["RELEASE-URL","RELEASE-TAG","TAG-COMMIT","ACTIONS-RUN","ASSET-SHA256-VERIFIED","ONLINE-ASSETS-VERIFIED"]:
            m=re.search(rf"(?m)^-\s*{re.escape(k)}:\s*(.*)$",t)
            f.write(f"- 旧 {k}: {m.group(1).strip() if m else 'unknown'}\n")

    t=setm(t,"RELEASE-ARCHIVE-STATUS","pending"); t=setm(t,"RELEASE-REVISION",str(nr)); t=setm(t,"REPUBLISH-MODE",a.mode)
    for k,val in {
        "REPUBLISH-REASON":a.reason,"RELEASE-URL":"pending","RELEASE-TAG":tag,"TAG-COMMIT":"pending",
        "ACTIONS-RUN":"pending","ASSET-SHA256-VERIFIED":"no","ONLINE-ASSETS-VERIFIED":"no"
    }.items(): t=field(t,k,val)
    check.write_text(t,encoding="utf-8"); rp.write_text(str(nr)+"\n",encoding="utf-8")
    subprocess.check_call([sys.executable,"scripts/dev-session.py","start","--goal",f"{a.mode}: {a.reason}"],cwd=root)
    subprocess.check_call([sys.executable,"scripts/update-repository-structure.py","--write"],cwd=root)
    subprocess.check_call([sys.executable,"scripts/build-source-manifest.py","--write"],cwd=root)
    return 0
if __name__=="__main__": raise SystemExit(main())
