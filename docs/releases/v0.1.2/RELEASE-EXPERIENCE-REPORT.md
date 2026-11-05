# Clash_Mac_Compile v0.1.2 Release Experience Report

## 故障

GitHub Actions 的 Upload macOS app 步骤提示找不到 `build/ci/Clash_Mac_Compile-v0.1.1-macos-arm64-unsigned.zip`、BUILD-METADATA、VPN report 和 SHA256SUMS。

## 判断边界

该错误只说明上传器没有找到路径；不能据此断定 Xcode 编译是否成功。需要在上传前打印真实输出目录并验证文件。

## 修复

- 将 `OUTPUT_DIR` 规范化为绝对路径。
- Build script 在最后验证必需文件并写入 `BUILD-OUTPUT-MANIFEST.json`。
- 使用 `verify-build-outputs.py` 作为 Build / Release / Weekly 上传前置门。
- Build workflow 上传单一 `build/ci/` 目录。
- 显式强制 GitHub 构建使用 unsigned，固定预期 ZIP 命名。
- Release attachment 也校验输出 manifest。

## 防回归

- 上传前必须验证 APP ZIP、BUILD-METADATA、VPN report、SHA256SUMS 均存在且非空。
- ZIP 文件名必须与 VERSION 和 unsigned 模式一致。
- `BUILD-OUTPUT-MANIFEST.json` 必须与真实文件一致。
- 上传步骤不再依赖多条精确路径的共同根目录计算。
