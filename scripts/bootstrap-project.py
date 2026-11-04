#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,shutil,subprocess,sys
from pathlib import Path

SEMVER=re.compile(r"^\d+\.\d+\.\d+$")
SLUG=re.compile(r"^[a-z0-9][a-z0-9._-]*$")

def main():
    ap=argparse.ArgumentParser(description="把通用模板初始化为新项目")
    ap.add_argument("--name",required=True); ap.add_argument("--slug",required=True)
    ap.add_argument("--repository",required=True,help="OWNER/REPOSITORY"); ap.add_argument("--version",default="0.1.0")
    a=ap.parse_args()
    if not SEMVER.fullmatch(a.version): print("version 必须为 X.Y.Z",file=sys.stderr); return 2
    if not SLUG.fullmatch(a.slug): print("slug 只能使用小写英文、数字、.-_",file=sys.stderr); return 2
    if not re.fullmatch(r"[^/\s]+/[^/\s]+",a.repository): print("repository 必须为 OWNER/REPOSITORY",file=sys.stderr); return 2
    root=Path(__file__).resolve().parents[1]

    pp=root/".ai/PROJECT-PROFILE.json"; profile=json.loads(pp.read_text(encoding="utf-8"))
    profile.update({"project_name":a.name,"project_slug":a.slug,"repository":a.repository,"project_type":"generic-code"})
    profile["quality"]["project_tests_configured"]=False
    profile["quality"]["simulation_configured"]=False
    # Prevent template-governance tests from pretending to be the business project's tests.
    for key in ["static","unit","integration","smoke","security","simulation"]:
        profile["quality"]["commands"][key]=[]
    pp.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (root/"VERSION").write_text(a.version+"\n",encoding="utf-8")
    (root/"RELEASE_REVISION").write_text("0\n",encoding="utf-8")

    releases=root/"docs/releases"
    for p in list(releases.glob("v*")):
        if p.is_dir(): shutil.rmtree(p)
    lessons=root/"docs/release-lessons"
    for p in list(lessons.glob("v*.md")): p.unlink()

    out=releases/f"v{a.version}"; out.mkdir(parents=True,exist_ok=True)
    mapping={
        "DEVELOPMENT-JOURNAL.template.md":"DEVELOPMENT-JOURNAL.md",
        "RELEASE-CHECKLIST.template.md":"RELEASE-CHECKLIST.md",
        "RELEASE-NOTES.template.md":"RELEASE-NOTES.md",
        "VALIDATION-REPORT.template.md":"VALIDATION-REPORT.md",
        "RELEASE-EXPERIENCE-REPORT.template.md":"RELEASE-EXPERIENCE-REPORT.md",
    }
    for src,dst in mapping.items():
        text=(root/"docs/templates"/src).read_text(encoding="utf-8")
        text=text.replace("__PROJECT_NAME__",a.name).replace("__VERSION__",a.version).replace("__RISK__","L1")
        (out/dst).write_text(text,encoding="utf-8")
    lesson=(root/"docs/templates/RELEASE-LESSON.template.md").read_text(encoding="utf-8")
    lesson=lesson.replace("__PROJECT_NAME__",a.name).replace("__VERSION__",a.version)
    (lessons/f"v{a.version}.md").write_text(lesson,encoding="utf-8")

    (root/"CHANGELOG.md").write_text(f"# Version Changelog\n\n## v{a.version}\n\n- 项目初始化，等待记录真实变化。\n",encoding="utf-8")
    tver=(root/"TEMPLATE_VERSION").read_text(encoding="utf-8").strip()
    (root/"BUILD-INFO.md").write_text(
        f"# Build Information\n\n- 项目名称：{a.name}\n- 项目版本：`{a.version}`\n- 治理模板版本：`{tver}`\n"
        f"- 私有仓库：`{a.repository}`\n\n## 构建原则\n\n以 `VERSION` 为项目版本事实源；正式交付前必须配置项目真实测试、simulation 和 Release 资产。\n",
        encoding="utf-8"
    )
    (lessons/"README.md").write_text(
        "# Release Lessons\n\n本目录保存当前项目跨版本经验。\n\n<!-- RELEASE-LESSON-INDEX -->\n"
        f"| 版本 | 核心经验 |\n|---|---|\n| v{a.version} | 项目初始化，等待首版真实经验 |\n\n"
        "AI 开工必须读取当前版本经验；收尾必须把根因转成自动防回归规则。\n",
        encoding="utf-8"
    )

    catp=root/".ai/REPOSITORY-CATALOG.json"; cat=json.loads(catp.read_text(encoding="utf-8"))
    for k in list(cat.get("files",{})):
        if re.fullmatch(r"docs/releases/v\d+\.\d+\.\d+/.+",k) or re.fullmatch(r"docs/release-lessons/v\d+\.\d+\.\d+\.md",k):
            del cat["files"][k]
    for k in list(cat.get("folders",{})):
        if re.fullmatch(r"docs/releases/v\d+\.\d+\.\d+/",k): del cat["folders"][k]
    folder=f"docs/releases/v{a.version}/"; cat["folders"][folder]="当前项目版本归档目录；保存开发、验证、发布和经验记录。"
    desc={
        "DEVELOPMENT-JOURNAL.md":"当前版本开发日志；保存恢复入口、检查点与开发完成状态。",
        "RELEASE-CHECKLIST.md":"当前版本发布检查表；保存风险、生命周期状态和真实发布证据。",
        "RELEASE-NOTES.md":"当前版本中文发布说明。",
        "VALIDATION-REPORT.md":"当前版本真实验证报告。",
        "RELEASE-EXPERIENCE-REPORT.md":"当前版本发布经验报告与模板反馈。",
    }
    for n,d in desc.items(): cat["files"][folder+n]=d
    cat["files"][f"docs/release-lessons/v{a.version}.md"]="当前版本发布经验；记录风险、根因、决策和防回归规则。"
    catp.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    subprocess.check_call([sys.executable,"scripts/update-repository-structure.py","--write"],cwd=root)
    subprocess.check_call([sys.executable,"scripts/build-source-manifest.py","--write"],cwd=root)
    print("Project bootstrap complete.")
    print("IMPORTANT: project_tests_configured=false, simulation_configured=false.")
    print("请先按真实技术栈配置测试命令，否则 candidate/release 会被硬门禁阻止。")
    return 0
if __name__=="__main__": raise SystemExit(main())
