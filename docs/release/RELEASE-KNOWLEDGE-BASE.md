# Release Knowledge Base

## Release Lesson

`docs/release-lessons/vX.Y.Z.md` 记录风险、根因、修复决策、防回归规则、验证与遗留边界。

## Release Experience Report

`docs/releases/vX.Y.Z/RELEASE-EXPERIENCE-REPORT.md` 记录“开发 → 本地测试 → GitHub CI → Release → 线上复核”的真实操作经验。

## 收敛

事故 → 根因 → 自动测试/门禁/脚本 → 判断是否通用 → 通用则更新模板并提升 `TEMPLATE_VERSION`。

经验库的价值是下一次同类错误能否被自动阻止。
