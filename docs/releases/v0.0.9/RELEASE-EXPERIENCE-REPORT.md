# Clash_Mac_Compile v0.0.9 Release Experience Report

## 故障

v0.0.8 GitHub Actions 中 APP 编译成功，但 `attach-release-assets.py` 在读取 `BUILD-METADATA.json` 时失败：
`Extra data: line 40 column 2 (char 1638)`。

## 根因

内嵌 Python metadata writer 把 `json.dumps(...)` 后缀写成字面量 `\\n`，导致 JSON 文档后面跟随额外字符。Xcode 版本字符串也把换行替换写成了字面量转义序列。

## 修复

- metadata JSON 写入真实换行。
- Xcode 版本信息使用真实换行分隔并转换为单行。
- JSON loader 提供路径和位置诊断。
- 新增直接执行内嵌 metadata writer 的回归测试，避免仅靠静态源码检查漏掉输出格式错误。

## 防回归

任何写入 JSON 的构建脚本都必须由测试实际执行生成，并使用 `json.loads` / JSON parser 重新读取；不能只检查源码字符串。Release 附件阶段必须在复制文件前完成元数据校验。

## 遗留边界

本地测试不等于 GitHub macOS Runner 实际运行；v0.0.9 的 Release 上传仍须用户在 GitHub Actions 验证。
