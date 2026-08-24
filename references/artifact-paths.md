# 默认产物路径

Loop 读写 artifacts 时优先使用以下路径（相对 `Test/HKU/`）。

| 键 | 路径 | 说明 |
|----|------|------|
| `rawInput` | `docs/原始诉求-*.md` | 用户提供的原始任务材料 |
| `clarifyReport` | `docs/01-业务诉求澄清报告.md` | 阶段一产出 |
| `prd` | `docs/02-PRD.md` | 阶段二产出 |
| `uiDesignBrief` | `design/设计说明.md` | 阶段三设计说明 |
| `uiOptions` | `design/ui-option-{1,2,3}.html` | 阶段三三个方案 |
| `uiSelected` | `design/ui-selected.html` 或选定方案路径 | 用户确认的方案 |
| `techPlan` | `docs/04-技术方案.md` | 阶段四产出（含实现计划） |
| `memory` | `memory.md` | 阶段五长期约束 |
| `testSamples` | `test_samples/` | 测试输入与标准答案 |
| `state` | `data/state/<taskId>.json` | 任务状态 |
| `logs` | `data/logs/<taskId>-tick-<n>.md` | 每 tick 日志 |

`artifacts` 中存**目标路径**；文件尚未生成时内容可为 `null`（`uiOptions` 为空数组）。
