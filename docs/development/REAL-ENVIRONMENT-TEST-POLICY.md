# Real-Environment Simulation Policy

AI 验证尽量接近真实用户环境，但不能把沙箱模拟冒充成用户实机。

## T0 静态门禁

语法、配置、治理、secret 路径检查。

## T1 单元测试

验证纯逻辑、错误分支和边界。

## T2 集成 / Smoke

真实组件组合运行，验证接口、文件、数据库、进程或网络边界。

## T3 Clean-Room 模拟

`scripts/run-simulated-environment.py` 会把仓库复制到没有 `.git`、`.dev-state`、`dist`、缓存和 secret 的临时目录，再运行 `PROJECT-PROFILE` 中的 simulation 命令。

用于发现：

- 暗中依赖本机文件；
- 依赖 Git 历史；
- 依赖旧 build 目录；
- 初始化缺失；
- 打包漏文件；
- 升级/回滚不完整。

## T4 故障注入

L2/L3 按项目覆盖网络失败、权限拒绝、无效配置、中途终止、旧版升级、回滚、重复执行幂等性等。

## T5 用户实机 / GitHub Runner

AI 沙箱不能代替真实 OS、浏览器、硬件、系统服务和 GitHub hosted runner。

## 强制配置

`quality.project_tests_configured` 与 `quality.simulation_configured` 在新项目 bootstrap 后会被置为 `false`。最终 AI 交付前必须按真实技术栈配置并改为 `true`，否则 candidate/release 门禁失败。
