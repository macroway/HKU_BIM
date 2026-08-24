# CheckBIM Agent — 项目记忆

## 已确认约定

- 栈：Python 3 + FastAPI + ifcopenshell + P1 受控 ReAct Agent
- UI：深色 CAD 工作台（`design/ui-option-1.html`）
- macOS 安装依赖用 `python3 -m pip`，不用裸 `pip`（系统无此命令）
- 本地开发用 `.venv` 虚拟环境
- 离线路由：意图不明（如纯数字）不跑工具，需澄清；禁止「默认两项都查」

## 检查点进度

- CP0：脚手架 ✓
- CP1：JSON 碰撞引擎 + 金标 ✓
- CP2：属性完整性 + 金标 ✓
- CP3：IFC 载入 + demo-collision.ifc ✓
- CP4：P1 Agent loop + 工具编排 + 防编造 ✓
- CP5：API 上传/选样例/chat ✓
- CP6：前端方案1 对接 API ✓（含 demo 样例路径修复）
- CP7：README / 演示脚本 / prompts 归档 ✓

## 阶段收口

文档（澄清→PRD→UI→技术方案）与代码检查点 CP0–CP7 均已人工确认完毕。

## 环境备忘

- macOS Homebrew Python：无 `pip` 命令，用 `python3 -m pip` 或激活 `.venv` 后用 `pip`
