# CheckBIM Agent

对话式 BIM 交付前自查助手：几何碰撞 + 属性完整性。HKU AI Agent 笔试 / 7 日 MVP。

## 功能

- **双入口**：上传 IFC/JSON，或一键载入内置样例
- **检查规则**：墙/梁/管段 AABB 碰撞；Name / FireRating 完整性
- **Agent**：P1 受控 ReAct（白名单工具 ≤5 步）；无 Key 时关键词 fallback
- **护栏**：未跑工具不得声称「检查通过」

## 快速开始

```bash
cd Test/HKU   # 或本仓库根目录
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

cp .env.example .env   # 默认 CHECKBIM_OFFLINE=1，零成本演示

uvicorn app.main:app --reload
```

浏览器打开：http://127.0.0.1:8000/

健康检查：`GET /api/health` → `{"status":"ok"}`

若提示 `Address already in use`：

```bash
lsof -ti :8000 | xargs kill -9
```

## 测试

```bash
source .venv/bin/activate
pytest tests/ -q
```

## 3 分钟演示脚本

详见 [`docs/05-演示脚本.md`](docs/05-演示脚本.md)。最短路径：

1. 打开 UI → 载入样例 **`demo-collision.ifc`**（或 `collision_positive.json`）
2. 输入：「帮我查碰撞」
3. 右侧应出现 ≥1 对碰撞；底部提示「工具调用」；`planner: rules`（离线）
4. （可选）再问：「查一下属性是否完整」

已知碰撞说明：[`test_samples/demo/README.md`](test_samples/demo/README.md)

## 环境变量

| 变量 | 说明 |
|------|------|
| `CHECKBIM_OFFLINE` | `1` = 规则路由，不调 LLM（默认演示） |
| `OPENAI_API_KEY` | 在线 ReAct 时填写 |
| `OPENAI_BASE_URL` | 可选兼容网关 |
| `OPENAI_MODEL` | 默认 `gpt-4o-mini` |

## 仓库结构（交付相关）

```
app/                 # FastAPI + Agent + 工具 + 静态前端
test_samples/        # JSON 金标 + demo IFC
tests/               # pytest
docs/                # 澄清 / PRD / 技术方案 / 演示脚本
design/              # UI 原型（选用 option-1）
prompts/             # 产研五阶段原始提示词归档
app/agent/prompts.py # Agent 系统提示
```

## 设计文档

- [业务澄清](docs/01-业务诉求澄清报告.md)
- [PRD](docs/02-PRD.md)
- [技术方案](docs/04-技术方案.md)
- [UI 设计说明](design/设计说明.md)
