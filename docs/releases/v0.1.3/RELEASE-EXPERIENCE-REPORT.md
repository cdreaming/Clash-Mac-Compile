# Clash_Mac_Compile v0.1.3 Release Experience Report

## 故障证据

v0.1.2 GitHub Actions 在 `verify-build-outputs.py` 报告五个必需文件全部缺失。未提供前一构建 step 的 outcome 和完整日志。

## 诊断原则

- 五个输出同时缺失说明应优先检查构建脚本是否实际运行、是否成功退出、是否写入预期目录。
- 不应在没有 Xcode log 的情况下断言是 Linker 失败。
- verify 不应作为与 build 分离的 step，否则容易掩盖前一步是否 skipped / failed 或路径是否一致。
- 产物目录应记录 build workflow 与 script 的独立状态。

## 修复

- Build / Release / Weekly build + verify 合并为一个 step。
- 绝对输出目录统一由 `GITHUB_WORKSPACE` 构造。
- workflow / script 双层 EXIT trap 写入 status、exit code 和 context。
- always-run report step 打印 step outcome 和目录文件。
- Release attachment 检查 script status。

## 防回归

- workflow 必须存在 `id: build_app` 并输出 `steps.build_app.outcome`。
- 构建与 verify 必须同一个 step。
- workflow/script status 与 context 必须 always-upload。
- Release 不得附加 exit code 非零或状态未知的 APP。
