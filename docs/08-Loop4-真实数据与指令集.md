# Loop 4 — 真实样例数据 + 丰富指令集

> 2026-08-24

## 1. 真实样例：`building_l1`

一层简化 BIM 模型（JSON），用于 **E2E 演示 + 金标测试**。

| 构件 | 数量 | 说明 |
|------|------|------|
| IfcWall | 4 | 东西外墙 + 2 道内隔墙 |
| IfcBeam | 1 | 主梁 B1（缺 FireRating） |
| IfcPipeSegment | 2 | 送风 / 回风风管 |
| IfcDoor | 3 | 2 扇防火门 + 1 扇普通门 |

**人工标注结果：**

- 碰撞：**4 对**（梁×隔墙、风管×隔墙、梁×风管、隔墙×隔墙）
- 属性缺失：**3 条** FireRating

生成命令：

```bash
python scripts/create_building_l1.py
```

产物：

- `test_samples/building_l1.json`
- `test_samples/building_l1.collision.expected.json`
- `test_samples/building_l1.attrs.expected.json`

## 2. 丰富指令集

离线 / 在线预检共用 `router_fallback.py`，新增口语化说法，例如：

| 意图 | 示例说法 |
|------|----------|
| 碰撞 | 有没有硬碰、空间冲突、风管撞墙了吗 |
| 属性 | 防火等级齐全吗、FireRating 缺不缺 |
| 两项 | 交付前过一遍、全面自查 |
| 概况 | 统计模型情况、有多少构件 |

完整用例见 `tests/test_intents.py`。

**仍拒绝**：纯数字、闲聊等无检查语义输入（如 `111`）。

## 3. 演示路径（推荐）

1. 载入 **building_l1.json**
2. 点快捷指令 **「交付前过一遍」** 或输入「有没有硬碰」
3. 平面视口应出现多处冲突高亮；属性卡片 3 条缺失

## 4. IFC 演示样例

与 `building_l1.json` 同几何的 IFC：

| 文件 | 样例 ID | 生成 |
|------|---------|------|
| `demo/building-l1.ifc` | `demo/building-l1` | `python scripts/create_building_l1.py` |
| `demo/demo-collision.ifc` | `demo/demo-collision` | `python scripts/create_demo_ifc.py` |

IFC 路径下预期与 JSON 一致：**4 对碰撞、3 条缺属性**。详见 `test_samples/demo/README.md`。
