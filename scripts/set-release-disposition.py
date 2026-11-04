#!/usr/bin/env python3
from __future__ import annotations
import argparse,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--version",required=True); ap.add_argument("--status",choices=["superseded","abandoned","failed"],required=True)
    ap.add_argument("--reason",required=True); ap.add_argument("--write",action="store_true")
    a=ap.parse_args(); root=Path(__file__).resolve().parents[1]
    p=root/"docs/releases"/f"v{a.version}"/"RELEASE-CHECKLIST.md"
    if not p.is_file(): print("找不到版本检查表",file=sys.stderr); return 1
    t=p.read_text(encoding="utf-8")
    if "RELEASE-ARCHIVE-STATUS: complete" in t:
        print("真实 complete 版本不能改成未发布 disposition；请 prepare-republish。",file=sys.stderr); return 1
    print(f"v{a.version} -> {a.status}: {a.reason}")
    if not a.write: return 0
    t=re.sub(r"RELEASE-ARCHIVE-STATUS:\s*[^ >]+",f"RELEASE-ARCHIVE-STATUS: {a.status}",t,count=1)
    t+=f"\n## Lifecycle Disposition\n\n- 状态：`{a.status}`\n- 原因：{a.reason}\n- 时间：{datetime.now(timezone.utc).isoformat()}\n"
    p.write_text(t,encoding="utf-8")
    subprocess.check_call([sys.executable,"scripts/build-source-manifest.py","--write"],cwd=root)
    return 0
if __name__=="__main__": raise SystemExit(main())
