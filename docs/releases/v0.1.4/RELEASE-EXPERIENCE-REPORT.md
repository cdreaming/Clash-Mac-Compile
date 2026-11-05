# Clash_Mac_Compile v0.1.4 Release Experience Report

## 故障

GitHub Actions 在 `Build and verify native macOS app` 的 shell 第 5 行报：
`.../Clash-Mac-Compile: is a directory`，exit code 126。

## 根因

YAML literal block 中的 `printf` 多行命令使用两个反斜杠结尾。Bash 不会将双反斜杠 + 换行解释为续行，因此后续目录路径被作为命令执行。构建脚本尚未启动。

## 修复

- 恢复 v0.1.3 原始 workflow，再按 step 名精确替换构建 step，避免误改 Release state / Weekly version preparation。
- 移除 printf 命令中的所有续行。
- 使用 `printf '%s\n'` 多参数一次写入多行文本。
- 对 Build / Release / Weekly 实际 YAML run block 执行 `bash -n`。
- 成功和失败模拟验证 workflow EXIT trap。

## 防回归

- 不在 YAML `run: |` 中对短小状态写入命令使用行尾反斜杠续行。
- 必须从 YAML 解析出实际 shell block 后执行 `bash -n`。
- Release 和 Weekly workflow 修改必须按 step 名定位，不能使用跨 step 的宽泛正则替换。
