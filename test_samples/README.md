# test_samples 样例目录

## 推荐演示：`building_l1`（接近真实的一层简化模型）

| 项 | 说明 |
|----|------|
| 文件 | `building_l1.json` |
| 规模 | 10 构件：外墙、隔墙、主梁、风管、防火门 |
| 已知碰撞 | **4 对**（梁×隔墙、风管×隔墙、梁×风管、隔墙×隔墙） |
| 已知缺属性 | **3 条** FireRating（主梁 B1、防火门 D1、门 D3） |
| 生成 | `python scripts/create_building_l1.py` |

### 演示拍摄参考（口播终稿请对着录屏生成，见 `docs/prompt-口播稿生成.md`）

1. 载入 **building_l1.json**
2. 「交付前帮我过一遍」→ 碰撞 4 对 + 属性缺失 3 条
3. 或分步：「有没有硬碰」「防火等级齐全吗」

## 金标样例（CI）

| 样例 | 用途 |
|------|------|
| `collision_positive` / `negative` | 碰撞引擎回归 |
| `attrs_missing` / `attrs_ok` | 属性引擎回归 |
| `building_l1` | 综合 E2E + 演示 |

## IFC

| 文件 | 说明 |
|------|------|
| `building_l1.json` | 一层综合 JSON（CI 金标 + 演示） |
| `demo/building-l1.ifc` | **与 JSON 同几何的 IFC**（真实模型路径演示） |
| `demo/demo-collision.ifc` | 最小墙-墙碰撞 IFC |

生成 JSON + IFC：

```bash
python scripts/create_building_l1.py
```
