# Tick 34 — 2026-08-24T14:23:00+08:00

## PERCEIVE

- 用户：`确认 CP6`（此前曾报「载入样例失败」）

## PLAN

```json
{
  "action": "fix_demo_select_then_cp7",
  "completed": ["CP0", "CP1", "CP2", "CP3", "CP4", "CP5", "CP6"],
  "current": "CP7"
}
```

## ACT

- 修复 select 路由 `{sample_id:path}` + 前端不 encode `/`
- CP7：README、docs/05-演示脚本、prompts/README、demo README 补强
- pytest 含 demo IFC select

## REFLECT

- 待用户确认 CP7；重启/刷新后 demo-collision 应可载入
