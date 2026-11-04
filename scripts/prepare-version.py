#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,subprocess,sys
from pathlib import Path

SEMVER=re.compile(r"^\d+\.\d+\.\d+$")
def vt(v): return tuple(map(int,v.split(".")))
def render(text,project,version,risk):
    return text.replace("__PROJECT_NAME__",project).replace("__VERSION__",version).replace("__RISK__",risk)

def main():
    ap=argparse.ArgumentParser(description="创建新项目版本的完整治理骨架")
    ap.add_argument("--version",required=True); ap.add_argument("--risk",choices=["L1","L2","L3"],required=True)
    ap.add_argument("--deep-upgrade",action="store_true"); ap.add_argument("--write",action="store_true")
    a=ap.parse_args(); root=Path(__file__).resolve().parents[1]
    if not SEMVER.fullmatch(a.version): print("版本必须是 X.Y.Z",file=sys.stderr); return 2
    old=(root/"VERSION").read_text(encoding="utf-8").strip()
    if vt(a.version)<=vt(old): print(f"新版本必须大于当前 {old}",file=sys.stderr); return 2
    prev_check=root/"docs/releases"/f"v{old}"/"RELEASE-CHECKLIST.md"
    if prev_check.is_file():
        prev_text=prev_check.read_text(encoding="utf-8")
        m=re.search(r"RELEASE-ARCHIVE-STATUS:\s*([^ >]+)",prev_text)
        prev_status=m.group(1) if m else "unknown"
        if prev_status!="complete":
            print(f"WARNING: 上一版本 v{old} 状态为 {prev_status}；允许继续开 v{a.version}，不会阻塞。",file=sys.stderr)
    profile=json.loads((root/".ai/PROJECT-PROFILE.json").read_text(encoding="utf-8"))
    project=profile["project_name"]
    if not a.write:
        print(f"Would prepare v{a.version}, risk={a.risk}, deep_upgrade={a.deep_upgrade}"); return 0

    (root/"VERSION").write_text(a.version+"\n",encoding="utf-8")
    (root/"RELEASE_REVISION").write_text("0\n",encoding="utf-8")
    out=root/"docs/releases"/f"v{a.version}"; out.mkdir(parents=True,exist_ok=True)
    mapping={
        "DEVELOPMENT-JOURNAL.template.md":"DEVELOPMENT-JOURNAL.md",
        "RELEASE-CHECKLIST.template.md":"RELEASE-CHECKLIST.md",
        "RELEASE-NOTES.template.md":"RELEASE-NOTES.md",
        "VALIDATION-REPORT.template.md":"VALIDATION-REPORT.md",
        "RELEASE-EXPERIENCE-REPORT.template.md":"RELEASE-EXPERIENCE-REPORT.md",
    }
    for src,dst in mapping.items():
        text=(root/"docs/templates"/src).read_text(encoding="utf-8")
        (out/dst).write_text(render(text,project,a.version,a.risk),encoding="utf-8")
    lesson=(root/"docs/templates/RELEASE-LESSON.template.md").read_text(encoding="utf-8")
    (root/"docs/release-lessons"/f"v{a.version}.md").write_text(render(lesson,project,a.version,a.risk),encoding="utf-8")

    if a.deep_upgrade or vt(a.version)[0]>vt(old)[0]:
        text=(root/"docs/templates/DEEP-UPGRADE-PLAN.template.md").read_text(encoding="utf-8")
        (out/"UPGRADE-PLAN.md").write_text(render(text,project,a.version,a.risk),encoding="utf-8")

    ch=(root/"CHANGELOG.md").read_text(encoding="utf-8")
    ch=ch.replace("# Version Changelog\n",f"# Version Changelog\n\n## v{a.version}\n\n- 待记录本版真实变化。\n",1)
    (root/"CHANGELOG.md").write_text(ch,encoding="utf-8")

    catp=root/".ai/REPOSITORY-CATALOG.json"; cat=json.loads(catp.read_text(encoding="utf-8"))
    folder=f"docs/releases/v{a.version}/"
    cat.setdefault("folders",{})[folder]="当前项目版本归档目录；保存开发、验证、发布、经验与可选深度升级记录。"
    desc={
        "DEVELOPMENT-JOURNAL.md":"当前版本开发日志；保存 active/complete 状态、检查点和恢复入口。",
        "RELEASE-CHECKLIST.md":"当前版本发布检查表；保存风险、ready/archive 状态和真实发布证据。",
        "RELEASE-NOTES.md":"当前版本面向用户的中文发布说明，GitHub Release 直接使用。",
        "VALIDATION-REPORT.md":"当前版本真实验证报告；记录环境、命令、结果、故障注入和边界。",
        "RELEASE-EXPERIENCE-REPORT.md":"当前版本发布经验报告；记录流程问题并决定是否升级通用模板。",
    }
    for n,d in desc.items(): cat.setdefault("files",{})[folder+n]=d
    if (out/"UPGRADE-PLAN.md").is_file():
        cat["files"][folder+"UPGRADE-PLAN.md"]="当前深度升级计划；记录兼容、迁移、回滚、故障注入和发布影响。"
    cat["files"][f"docs/release-lessons/v{a.version}.md"]="当前版本发布经验；把事故根因转成可执行防回归规则。"
    catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    subprocess.check_call([sys.executable,"scripts/update-repository-structure.py","--write"],cwd=root)
    subprocess.check_call([sys.executable,"scripts/build-source-manifest.py","--write"],cwd=root)
    print(f"Prepared v{a.version}. 填完占位内容后才能进入 candidate gate。")
    return 0
if __name__=="__main__": raise SystemExit(main())
