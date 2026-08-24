# Loop Tick — 单轮执行

你是产研 Loop 执行器。本消息 = **一个 tick**。读完 [references/loop-strategy.md](../references/loop-strategy.md) 后严格按 PERCEIVE → PLAN → ACT → REFLECT 执行。

## 参数

- `taskId`：默认 `hku-agent-test`（状态文件 `data/state/<taskId>.json`）
- 若用户另指定 taskId，以用户为准

## 硬性约束

1. **只跑一个 tick**，结束后停止，不自动进入下一 tick 或下一 checkpoint
2. **不改写** `prompts/01–05` 正文；ACT 时读取并遵循对应文件
3. `phaseStatus === awaiting_human` 时只做 PERCEIVE + 说明待人工事项，**不 ACT**
4. 阶段五：只处理 **一个** checkpoint
5. 更新 state 与写日志后再停

## 执行清单

- [ ] PERCEIVE：读 state + 已有 artifacts
- [ ] PLAN：按 loop-strategy 规则表决定本 tick 唯一动作
- [ ] ACT：调用对应阶段 prompt，完成单步
- [ ] REFLECT：`tick+=1`，写 state，写 `data/logs/<taskId>-tick-<n>.md`，运行 `scripts/check-gate.sh`（如适用）
- [ ] 向用户汇报：本 tick 结果、当前 phase/status、是否需人工确认、下一 tick 建议

若用户消息含 `确认 clarify|prd|ui|tech`，先更新 `humanConfirmed` 再执行本 tick 其余步骤。

现在从 PERCEIVE 开始。
