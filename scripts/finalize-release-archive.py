#!/usr/bin/env python3
from __future__ import annotations
import argparse,os,re,sys
from pathlib import Path
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--release-url",required=True); ap.add_argument("--release-tag",required=True)
    ap.add_argument("--tag-commit",required=True); ap.add_argument("--actions-run",required=True)
    ap.add_argument("--asset-sha256-verified",action="store_true"); ap.add_argument("--online-assets-verified",action="store_true")
    ap.add_argument("--write",action="store_true"); a=ap.parse_args()
    root=Path(__file__).resolve().parents[1]; v=(root/"VERSION").read_text().strip()
    rev=int((root/"RELEASE_REVISION").read_text().strip()) if (root/"RELEASE_REVISION").is_file() else 0
    p=root/"docs/releases"/f"v{v}"/"RELEASE-CHECKLIST.md"; t=p.read_text(encoding="utf-8")
    m=re.search(r"REPUBLISH-MODE:\s*([^ >]+)",t); mode=m.group(1) if m else "none"
    expected=f"v{v}-r{rev}" if mode=="revision" and rev>0 else f"v{v}"
    if a.release_tag!=expected or not (a.asset_sha256_verified and a.online_assets_verified): return 2
    t=re.sub(r"RELEASE-ARCHIVE-STATUS:\s*[^ >]+","RELEASE-ARCHIVE-STATUS: complete",t,count=1)
    for k,val in {"RELEASE-URL":a.release_url,"RELEASE-TAG":a.release_tag,"TAG-COMMIT":a.tag_commit,
                  "ACTIONS-RUN":a.actions_run,"ASSET-SHA256-VERIFIED":"yes","ONLINE-ASSETS-VERIFIED":"yes"}.items():
        t=re.sub(rf"(?m)^-\s*{re.escape(k)}:\s*.*$",f"- {k}: {val}",t,count=1)
    if a.write:
        tmp=p.with_suffix(".tmp"); tmp.write_text(t,encoding="utf-8"); os.replace(tmp,p)
    return 0
if __name__=="__main__": raise SystemExit(main())
