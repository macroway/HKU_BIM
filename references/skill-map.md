# 阶段 → Skill 映射

ACT 步根据 `currentPhase` 调用对应 prompt；**不得改写** `prompts/01–05` 正文。

| phase | Prompt | 主要输入 | 主要输出 |
|-------|--------|----------|----------|
| `clarify` | [prompts/01-澄清原始诉求.md](../prompts/01-澄清原始诉求.md) | `artifacts.rawInput` | `artifacts.clarifyReport` |
| `prd` | [prompts/02-出产品需求.md](../prompts/02-出产品需求.md) | `artifacts.clarifyReport` | `artifacts.prd` |
| `ui` | [prompts/03-出界面原型图.md](../prompts/03-出界面原型图.md) | `artifacts.prd` | `uiDesignBrief` + `uiOptions`（≥3） |
| `tech` | [prompts/04-出技术方案.md](../prompts/04-出技术方案.md) | `prd` + `uiSelected` + `test_samples/` | `artifacts.techPlan` |
| `code` | [prompts/05-编写代码.md](../prompts/05-编写代码.md) | PRD + UI + 技术方案 + `codeCheckpoint.current` | 代码 + 测试 + `memory.md` |

## 每 tick 允许的动作（单步）

| phase | 典型单 tick 动作 |
|-------|------------------|
| `clarify` | 读材料并小结；或问 1–2 个问题；或写出澄清报告草稿 |
| `prd` | 问 1 个问题；或总结需求待确认；或生成 PRD |
| `ui` | 问 1 个设计问题；或写设计说明；或生成 1 个 UI 方案 |
| `tech` | 问 1 个问题；或总结理解待确认；或输出技术方案 |
| `code` | 复述当前 checkpoint；或实现并验证**一个** checkpoint |

一个 tick **只做上表一行**中的一种动作。
