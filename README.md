# CheckBIM Agent

面向 BIM / 建筑工程师的**对话式交付前自查助手**。在模型交模前，用自然语言触发**几何碰撞**与**属性完整性**检查，并给出可追溯、可验收的结构化结果。

本仓库是 HKU AI Agent 7 日 MVP 交付物：[代码](.) + [产研提示词](prompts/) + [过程文档](docs/)。

> GitHub：https://github.com/macroway/HKU_BIM

---

## 1. 项目一句话

**用 Loop 工程驱动「标准产研 SKILL」自动推进澄清 → PRD → UI → 技术方案 → 按 Checkpoint 编码；人只在关键判断点确认；最终落地可运行的 CheckBIM Agent（检查结论必须来自真实工具，禁止编造）。**

---

## 2. 怎么做出来的：Loop 工程 + 标准产品落地 SKILL

本项目不是「直接堆代码」，而是把产研五阶段固化成可重复执行的 Agent Skill，再用最小 Loop 壳按 tick 推进。

### 2.1 标准产品落地 SKILL（五阶段）

Skill 入口：[SKILL.md](SKILL.md)。每阶段 **原样遵循** 固定 prompt，不改写：

| 阶段 | Prompt | 产出 |
|------|--------|------|
| 澄清原始诉求 | [prompts/01-…](prompts/01-澄清原始诉求.md) | [docs/01-业务诉求澄清报告.md](docs/01-业务诉求澄清报告.md) |
| 产品需求 PRD | [prompts/02-…](prompts/02-出产品需求.md) | [docs/02-PRD.md](docs/02-PRD.md) |
| 界面原型 | [prompts/03-…](prompts/03-出界面原型图.md) | [design/](design/) ≥3 方案 + 设计说明 |
| 技术方案 | [prompts/04-…](prompts/04-出技术方案.md) | [docs/04-技术方案.md](docs/04-技术方案.md) |
| 编写代码 | [prompts/05-…](prompts/05-编写代码.md) | CP0–CP7 可运行实现 + 测试 |

### 2.2 Loop 工程（路径 A · 最小投入）

执行壳：[prompts/00-loop-tick.md](prompts/00-loop-tick.md) + [references/loop-strategy.md](references/loop-strategy.md)。

每个 tick 固定四步：

```
PERCEIVE → PLAN（规则表选一步）→ ACT（读对应 prompts/01–05）→ REFLECT（写 state / log / gate）
```

| 机制 | 作用 |
|------|------|
| 状态落盘 | `data/state/hku-agent-test.json`，可断点续跑 |
| 单 tick | 每次只做一个动作，避免失控连跑 |
| 阶段 Gate | `scripts/check-gate.sh` 做文件级完成检查 |
| 人工闸门 | 阶段 1–4 与每个代码 Checkpoint 均需人确认后才前进 |
| 过程可审计 | `data/logs/hku-agent-test-tick-*.md` 记录每步决策与改动 |

**结果：** 文档、设计、实现计划与代码沿着同一条可控流水线落地；提示词与过程材料一并进仓库，便于评审「有思考、可复现」。

---

## 3. 人的思考与判断（Machine 推进，Human 定方向）

自动化负责推进与起草；**产品边界与风险取舍由人拍板**。本项目中关键人工判断包括：

### 3.1 问题与范围

| 判断 | 选择 | 为何重要 |
|------|------|----------|
| 规则数量 | **只做 2 条**：碰撞 + 属性 | 对齐笔试「1–2 条、精炼优先」，避免规范库膨胀 |
| 不做的几何规则 | 门净宽、疏散距离等 | 7 天内优先「可演示 + 可测」 |
| 目标用户 | BIM / 建筑工程师（最终用户） | 交互叙事与 UI 气质锚定交付前自查 |
| 主场景 | **交付前自查**（非完整验收平台） | 砍掉协作、权限、写回 IFC 等 |

### 3.2 质量与风险优先级

| 判断 | 选择 |
|------|------|
| 最不能接受的错误 | **漏报碰撞** > Agent 编造结果 > 误报 |
| 防编造策略 | 检查结论**唯一**来自工具输出；未跑工具禁止「检查通过」 |
| 碰撞算法 | 第一版 **AABB**（优先降漏报；精确碰撞以后再做） |
| 模糊意图 | 离线模式：**追问澄清**，禁止「随便输入也默认两项都查」 |

### 3.3 产品与交互形态

| 判断 | 选择 |
|------|------|
| 输入形态 | **双入口**：上传 IFC **或** 选内置样例 |
| 数据策略 | **JSON 金标**（自动化）+ **小 IFC**（演示） |
| UI | 三选一后锁定 **深色 CAD 工作台**（`design/ui-option-1.html`） |
| 设备 | 桌面优先，工程工具感，而非消费级聊天页 |

### 3.4 技术取舍

| 判断 | 选择 |
|------|------|
| 架构 | **Python 单体** FastAPI，不引入微服务 / 重前端框架 |
| Agent 规划 | **P1 受控 ReAct**（白名单工具 + ≤5 步），不做开放长程规划 |
| 无 Key / CI | **规则路由 fallback**，保证本地零成本可跑 |
| IFC 依赖风险 | 引擎统一走 `InternalModel`；JSON 可兜底演示 |

### 3.5 过程闸门（Loop 中的人）

人不是旁观，而是每个阶段的 **Gate Owner**：

- `确认 clarify` / `确认 prd` / `确认 ui` / `确认 tech`
- `选定 UI 方案 1`
- `确认 CP0` … `确认 CP7`

没有确认，Loop 停留在 `awaiting_human`，不擅自跨阶段。

---

## 4. 功能特点

| 能力 | 说明 |
|------|------|
| 对话触发检查 | 「帮我查碰撞」「查属性」「两个都查」「帮我检查一下」等 |
| 双入口 | 上传 `.ifc` / `.json`，或一键载入样例（含已知碰撞 IFC） |
| 规则 1 · 碰撞 | 墙 / 梁 / 管段等 AABB 相交 → 冲突对清单 |
| 规则 2 · 属性 | Name、FireRating 缺失检测 → 缺失清单 |
| 结果可追溯 | 返回 `tool_traces`、`did_run_tools`、`planner`（`rules` / `llm`） |
| 防编造护栏 | 无工具成功输出时，不得给出「通过 / 无碰撞」类结论 |
| 意图不明处理 | 离线：澄清提示，**不执行**检查工具 |
| 双模式 Agent | 离线关键词规划；在线 OpenAI 兼容 tool-calling ReAct |

主流程：

```
选/上传模型 → 自然语言意图 → Agent 选工具 → 本地检查引擎
    → 对话摘要 + 结构化清单 + 简要轨迹
```

---

## 5. 技术特点

| 层 | 技术 | 要点 |
|----|------|------|
| Web | FastAPI + 静态前端 | 按 UI 方案 1 改造；桌面双栏工作台 |
| 模型 | ifcopenshell + JSON loader | 统一 `InternalModel`，测试与演示同引擎 |
| 工具 | `collision` / `attributes` / `get_model_info` | 白名单注册；纯函数、可单测 |
| Agent | P1 ReAct + `router_fallback` | ≤5 步；结论绑定工具 JSON |
| 验收 | pytest + `*.expected.json` | 金标比对结构化字段，不比对话文案 |
| 配置 | `.env` / `CHECKBIM_OFFLINE` | 默认离线演示；有 Key 可升级 LLM 规划 |
| 工程化 | Checkpoint CP0–CP7 | 脚手架 → 引擎 → IFC → Agent → API → UI → 文档 |

**刻意不做（第一版）：** LangChain 全家桶、数据库、多租户、完整 3D BIM 编辑器、写回 IFC、开放式多步自由规划。

---

## 6. 快速开始

```bash
# 仓库根目录
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

cp .env.example .env   # 默认 CHECKBIM_OFFLINE=1

uvicorn app.main:app --reload
```

浏览器打开：http://127.0.0.1:8000/

健康检查：`GET /api/health` → `{"status":"ok"}`

端口占用时：

```bash
lsof -ti :8000 | xargs kill -9
```

### 环境变量

| 变量 | 说明 |
|------|------|
| `CHECKBIM_OFFLINE` | `1` = 规则路由（默认演示 / CI） |
| `OPENAI_API_KEY` | 在线 ReAct 时填写 |
| `OPENAI_BASE_URL` | 可选兼容网关 |
| `OPENAI_MODEL` | 默认 `gpt-4o-mini` |

### 测试

```bash
source .venv/bin/activate
pytest tests/ -q
```

### 3 分钟演示

见 [docs/05-演示脚本.md](docs/05-演示脚本.md)（**在线 Doubao 专版**）。录制前 `.env` 设 `CHECKBIM_OFFLINE=0` 并配置 `ARK_API_KEY`；确认页面显示 **Doubao** 规划器。

最短路径：载入 `building-l1.ifc` →「交付前过一遍」→ 轨迹 2 工具、碰撞 4 / 缺属性 3。

已知碰撞说明：[test_samples/demo/README.md](test_samples/demo/README.md)

---

## 7. 仓库结构

```
app/                 # FastAPI + Agent + 检查工具 + 静态前端
test_samples/        # JSON 金标 + demo IFC
tests/               # pytest
docs/                # 澄清 / PRD / 技术方案 / 演示脚本
design/              # UI 三方案（选用 option-1）
prompts/             # 产研五阶段 + Loop tick 提示词（提交用）
references/          # Loop 策略、Gate、产物路径
data/state|logs/     # Loop 状态与 tick 日志（过程可审计）
SKILL.md             # 产研方法论 Skill 入口
memory.md            # 长期约束与检查点备忘
```

---

## 8. 文档索引

| 文档 | 内容 |
|------|------|
| [01 业务澄清](docs/01-业务诉求澄清报告.md) | 问题、角色、Must/Should |
| [02 PRD](docs/02-PRD.md) | 范围、验收、风险 |
| [04 技术方案](docs/04-技术方案.md) | 栈、模块、CP 计划、防编造 |
| [05 演示脚本](docs/05-演示脚本.md) | ≤3 分钟拍摄动线（口播终稿见录屏后生成） |
| [口播稿 Prompt](docs/prompt-口播稿生成.md) | 对着成片视频生成口播 |
| [设计说明](design/设计说明.md) | UI 选型依据 |
| [prompts/README](prompts/README.md) | 提示词归档说明 |
| [SKILL.md](SKILL.md) | Loop + 五阶段总览 |

---

## 9. 提交说明（笔试）

- **仓库**：本 GitHub（代码 + `prompts/` + `docs/`）
- **视频**：≤3 分钟演示（按演示脚本录制；口播可录完后用 `docs/prompt-口播稿生成.md` 对着成片写稿再配音）
- **邮件**：主题 `【HKU AI Agent 笔试测试】姓名_学校/单位` → `junnaifj@hku.hk`，附简历与两个链接
