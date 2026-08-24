# Loop3：Volcengine Ark / Doubao Responses API

> 模型：`doubao-seed-2-0-lite-260428`

## 配置

复制 `.env.example` 为 `.env`：

```bash
CHECKBIM_OFFLINE=0
LLM_PROVIDER=ark
ARK_API_KEY=你的火山方舟密钥
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL=doubao-seed-2-0-lite-260428
```

## 调用方式

Agent 在线模式走 **Responses API**（与用户提供的 curl 一致）：

```bash
curl https://ark.cn-beijing.volces.com/api/v3/responses \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "doubao-seed-2-0-lite-260428",
    "instructions": "...",
    "input": [{"role":"user","content":[{"type":"input_text","text":"帮我查碰撞"}]}],
    "tools": [...]
  }'
```

实现见 `app/agent/ark_client.py`。

> **注意**：Responses API 的 `tools` 为扁平结构（`type` + `name` + `description` + `parameters`），不同于 Chat Completions 的嵌套 `function` 字段；客户端会自动转换。

## 大模型在链路中的位置

| 环节 | Doubao | 本地 |
|------|--------|------|
| 理解自然语言、选工具 | ✅ Responses + tools | — |
| 组织回复 | ✅（须引用 tool JSON） | — |
| 碰撞 / 属性计算 | — | ✅ |
| LLM 失败 | 自动降级 `rules` | ✅ |

## 方案 A：在线放宽意图预检

| 模式 | 预检 |
|------|------|
| 离线 `CHECKBIM_OFFLINE=1` | 关键词路由；无匹配则不跑工具 |
| 在线 Doubao | 仅拦截 gibberish（如 `111`、纯符号）；其余交给模型 + tool calling |
| 共用护栏 | 未调用工具时，`_guard_reply` 禁止输出检查结论或编造报告 |

`SYSTEM_PROMPT` 要求摘要必须引用工具返回的构件名、对数、缺失字段，不得添加未返回的碰撞对或缺项。

## 状态检查

```bash
curl http://127.0.0.1:8000/api/llm/status
```

返回 `provider: ark`、`planner_label: doubao` 即在线 Doubao 已就绪。

UI 右下角规划器显示 **doubao** 表示当前由豆包规划。
