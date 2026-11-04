# 运行速度与流畅度优先的性能策略

## 构建配置

本项目 Release 构建默认使用：

- `SWIFT_OPTIMIZATION_LEVEL=-O`：以运行时速度为优先。
- `ARCHS=arm64`：先支持 Apple Silicon。
- `CLASH_BUILD_JOBS=2`：限制 Xcode 并行任务，降低 Hosted Runner 峰值资源压力。
- Go 工具链由固定的上游 Client / Kernel 要求决定；不随意注入可能改变运行行为的 Go flags。

`-O` 是编译器优化策略，不是性能提升保证。它可能增加编译时间或二进制体积；必须在相同设备、相同配置和相同测试负载下与 `-Osize` 基准比较。

## 优先级

1. UI 主线程：避免阻塞、长时间同步工作和重复刷新。
2. 网络转发：用 Go pprof / CPU profile 检查真实热点。
3. 内存：检查配置缓存、Geo 数据和连接状态对象的生命周期。
4. 节点测速：控制并发、复用连接、避免 UI 线程等待。
5. 磁盘：避免频繁同步写日志和重复解析大 YAML。
6. 启动：测量冷启动与热启动，减少启动路径上的同步工作。

本构建包装仓库不直接修改上游 Swift / Go 业务逻辑。若性能分析确认热点位于上游源码，应在经过审查的上游 fork / patch 中修复，而不是在构建脚本中猜测性地注入行为变更。

## 基准测试

至少记录：

| 指标 | 场景 |
|---|---|
| 冷启动 / 热启动 | 各 10 次，记录中位数和 P95 |
| UI 响应 | 打开配置页、切换策略组、滚动长列表 |
| CPU | 空闲 5 分钟、持续代理 10 分钟 |
| 内存 | 空闲、导入大配置、长时间运行 |
| 网络 | 固定测试端点下的 TCP / UDP / DNS |
| 能耗 | 电池供电下相同流量与时长 |

工具：
- Xcode Instruments: Time Profiler、Allocations、Points of Interest、Energy Log。
- Go pprof: CPU、heap、goroutine profile。
- `xcrun xctrace`: 录制和导出 Instruments trace。

## 性能报告原则

每次对比必须记录：
- Client / Kernel / Adapter commit。
- Xcode / Swift / Go 版本。
- 构建优化级别。
- Mac 型号、macOS 版本、电源状态。
- 测试配置、节点数、流量和时长。

没有可重复的基准数据时，不得声称某版本“快了 X%”或“减少 Y MB 内存”。
