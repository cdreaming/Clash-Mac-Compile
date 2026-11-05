# Clash_Mac_Compile v0.1.5 Release Experience Report

## 故障

GitHub Actions 报：
`SYSTEM_EXTENSION_PROJECT: unbound variable`

随后输出的 `BUILD-SCRIPT-STATUS.txt` 将 status、exit_code、version 和 output_directory 写成一行字面 `\n`，导致验证器不能识别成功状态。

## 根因

- 变量声明名为 `SYSTEM_EXTENSION_PROJECT_SPEC`，使用时却引用 `SYSTEM_EXTENSION_PROJECT`。
- `printf` 格式中的双反斜杠输出字面 `\n`，不是换行。
- EXIT trap 状态传递需明确保留最初退出码。

## 修复

- 统一 project spec 变量名并增加非空断言。
- 状态写入使用 `printf '%s\n'`。
- EXIT trap 改为显式参数传递原始 `$?`。
- 新增真实执行 cleanup function 的失败退出码测试。

## 防回归

- 变量声明和引用由单元测试检查。
- 状态文件必须逐行可解析。
- 强制模拟非零退出码并验证状态为 failed。
- 真实 Xcode 构建仍需在 macOS Runner 验证。
