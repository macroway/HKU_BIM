# Loop 2 — 可视化与 Agent 交互增强

> 2026-08-24 · 用户方向：不做 JSON 堆砌；可视化直观；Agent 交互感强

## 目标

| 维度 | Loop2 增强 |
|------|------------|
| 可视化 | 平面俯视图 Canvas；碰撞/属性卡片；点击碰撞联动高亮 |
| Agent 感 | 执行轨迹时间线、快捷指令芯片、对话气泡、工具标签、规划中状态 |

## 实现（L2-CP1）

- `GET /api/models/{model_id}/preview` — 构件 AABB 供前端绘图
- `app/static/` — 三栏布局：入口 | 视口 | Agent
- 移除 JSON `<pre>` 结果展示

## 后续可选

- 3D 轻量预览（Three.js）
- 在线 LLM 模式下流式时间线
- 导出 PDF 检查报告
