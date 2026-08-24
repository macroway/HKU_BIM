# 阶段 Gate（完成判定）

REFLECT 步用本表判断阶段是否可标记 `awaiting_human` 或进入下一阶段。

## 阶段一 `clarify`

| 检查项 | 条件 |
|--------|------|
| 报告文件 | `artifacts.clarifyReport` 路径下文件存在 |
| 结构 | 含 8 节：业务一句话、核心问题与目标、关键角色、主流程、需求优先级、约束与风险、待确认问题、建议下一步 |
| 人工 | `humanConfirmed.clarify === true` 后才可 `currentPhase → prd` |

自动检查：`scripts/check-gate.sh clarify <taskId>`

## 阶段二 `prd`

| 检查项 | 条件 |
|--------|------|
| 文件 | `artifacts.prd` 存在 |
| 结构 | 含 PRD 12 项（见 `prompts/02`） |
| 人工 | `humanConfirmed.prd === true` 后才可 `currentPhase → ui` |

自动检查：`scripts/check-gate.sh prd <taskId>`

## 阶段三 `ui`

| 检查项 | 条件 |
|--------|------|
| 设计说明 | `artifacts.uiDesignBrief` 存在 |
| 方案数 | `uiOptions` 至少 3 个文件均存在 |
| 选定 | `artifacts.uiSelected` 非空（用户指定其一或复制为 selected） |
| 人工 | `humanConfirmed.ui === true` 后才可 `currentPhase → tech` |

自动检查：`scripts/check-gate.sh ui <taskId>`

## 阶段四 `tech`

| 检查项 | 条件 |
|--------|------|
| 文件 | `artifacts.techPlan` 存在 |
| 结构 | 含技术方案 12 项 + **有序实现计划**（步骤列表） |
| 人工 | `humanConfirmed.tech === true` 后才可 `currentPhase → code` |

自动检查：`scripts/check-gate.sh tech <taskId>`

## 阶段五 `code`

| 检查项 | 条件 |
|--------|------|
| Checkpoint | `codeCheckpoint.current` 来自技术方案实现计划 |
| 验证 | 当前 checkpoint 相关测试通过 + `test_samples/` 核对（按 `prompts/05`） |
| 完成 | 实现计划全部 checkpoint 进入 `codeCheckpoint.completed` → `phaseStatus: done` |

**本阶段无需 `humanConfirmed`**：以测试与 checkpoint 通过为准；每 checkpoint 结束仍须等人确认再进下一 checkpoint（与 `prompts/05` 一致）。

## phaseStatus 含义

| 值 | 含义 |
|----|------|
| `in_progress` | 本阶段进行中，可继续 tick |
| `awaiting_human` | 产出已就绪或需人回答/确认，**本 tick 停止** |
| `done` | 全五阶段完成 |
| `failed` | 上一 ACT 失败，见 `lastError` |
