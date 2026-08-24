# 路径 A：最小 Loop 策略

规则引擎 PLAN，无独立 Planner LLM。每次 tick 只跑一轮，状态落盘。

## 触发方式

在 Cursor 中任选其一：

1. **手动**：`@Test/HKU/SKILL.md 跑 loop tick，taskId=hku-agent-test`
2. **循环**：`/loop 30m @Test/HKU/prompts/00-loop-tick.md taskId=hku-agent-test`（仅当 `phaseStatus !== awaiting_human` 时才有意义；待人确认时应停止 loop）

## 四步映射

### PERCEIVE

1. 读取 `data/state/<taskId>.json`
2. 读取 [artifact-paths.md](artifact-paths.md) 中当前阶段相关文件（若已存在）
3. 若 `phaseStatus === awaiting_human`：**不再 ACT**，提示用户确认或回答问题

### PLAN（规则表，按顺序匹配第一条）

```
1. phaseStatus === "awaiting_human"
   → 动作：stop；提示人工事项

2. phaseStatus === "failed" && lastError.retryable
   → 动作：retry 上一 subStep（同一 tick 只重试一次）

3. currentPhase === "clarify"
   → 若 clarifyReport 文件不存在：subStep = 对话/问答 或 写报告草稿（遵循 prompts/01）
   → 若文件存在且 Gate 通过且 !humanConfirmed.clarify：subStep = set_awaiting_human（等人确认澄清报告）
   → 若 humanConfirmed.clarify：currentPhase = prd；phaseStatus = in_progress

4. currentPhase === "prd"（同理，产出 prd，Gate，humanConfirmed.prd → ui）

5. currentPhase === "ui"
   → 需 uiDesignBrief + 3 options + uiSelected + humanConfirmed.ui → tech

6. currentPhase === "tech"
   → techPlan + humanConfirmed.tech → code；并将实现计划第一步写入 codeCheckpoint.current

7. currentPhase === "code"
   → 若 !codeCheckpoint.current：从技术方案解析第一步
   → 否则：执行 prompts/05 的**一个** checkpoint
   → checkpoint 通过：移入 completed，更新 current 为下一步；若无下一步 → phaseStatus = done
```

将决策写入 `lastPlan`（简短 JSON 或一句话）。

### ACT

1. 读取 [skill-map.md](skill-map.md) 对应 prompt **全文**
2. 仅执行 PLAN 选定的**单步**动作
3. 写入 artifacts（按 [artifact-paths.md](artifact-paths.md)）

### REFLECT

1. 运行 `scripts/check-gate.sh <phase> <taskId>`（若适用）
2. 更新 `data/state/<taskId>.json`：
   - `tick += 1`
   - `phaseStatus` / `currentPhase` / `subStep` / `lastError` / `updatedAt`
3. 写入 `data/logs/<taskId>-tick-<n>.md`：

```markdown
# Tick <n> — <ISO8601>

## PERCEIVE
- phase / status / checkpoint

## PLAN
<lastPlan>

## ACT
- 做了什么；改了哪些文件

## REFLECT
- gate 结果；下一 tick 建议
```

4. **停止**，等待下一 tick 或人工确认（不自动连跑）

## 人工确认协议

用户确认某阶段时，在对话中说：`确认 clarify` / `确认 prd` / `确认 ui` / `确认 tech`

下一 tick 将 `humanConfirmed.<phase> = true` 写入 state，再按 PLAN 推进。

选定 UI：`选定 UI 方案 2` → 更新 `artifacts.uiSelected` 为对应路径。

## 与产研 SKILL 的关系

- `prompts/01–05`：ACT 时原样遵循，不改写
- [SKILL.md](../SKILL.md)：总览；Loop 本节为执行壳
- `memory.md`：仅阶段五 checkpoint 通过后按 `prompts/05` 更新
