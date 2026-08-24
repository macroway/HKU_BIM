# demo/building-l1.ifc — 一层综合演示模型

与 `building_l1.json` **同几何、同标注**，IFC 格式用于真实模型路径演示。

生成：

```bash
python scripts/create_building_l1.py   # 同时生成 JSON + IFC
# 或单独
python scripts/create_building_l1_ifc.py
```

## 模型内容（10 构件）

- 4 × IfcWall（东西外墙 + 2 道隔墙）
- 1 × IfcBeam（主梁 B1，缺 FireRating）
- 2 × IfcPipeSegment（送风 / 回风）
- 3 × IfcDoor（D1/D2/D3，D1/D3 缺 FireRating）

## 人工抽检

| 检查 | 预期 |
|------|------|
| 碰撞 | **4 对**（与 JSON 金标一致） |
| 属性 | **3 条** FireRating 缺失 |

UI 样例 ID：`demo/building-l1`

## 与 demo-collision.ifc 区别

| 文件 | 用途 |
|------|------|
| `demo-collision.ifc` | 最小墙-墙碰撞（2 墙） |
| `building-l1.ifc` | **主演示**：多专业 + 多碰撞 + 缺属性 |
