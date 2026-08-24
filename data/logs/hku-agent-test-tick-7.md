# Tick 7 — 2026-08-24T09:37:00+08:00

## PERCEIVE

- `tick`: 6 → 7
- 用户未直接选 A/B/C，改为询问：最终用户最可能使用的工作场景是什么

## PLAN

```json
{
  "action": "prd_q2_advise",
  "reason": "按 prompts/02：说不清时给选项与区别，可建议但不替用户决定",
  "recommendation": "A（模型交付前自查）为主场景，B 为次要；C 暂不作为 MVP 主场景",
  "next_subStep": "prd_q2_await_confirm"
}
```

## ACT

- 输出场景权衡与推荐
- 请用户确认 A/B/C
- 未写 PRD

## REFLECT

- Gate prd: FAIL（预期）
- 下一 tick：确认场景后问输入输出或最不能接受的错误
