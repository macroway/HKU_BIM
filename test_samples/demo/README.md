# demo-collision.ifc — 已知碰撞说明

生成方式：`python scripts/create_demo_ifc.py`（需已安装 ifcopenshell）

UI / API 样例 ID：`demo/demo-collision`

## 模型内容

- **外墙 A**（IfcWall）：原点放置，长 10m
- **内隔墙 B**（IfcWall）：x=5m 放置，长 6m，与外墙 A 在 x=5~10 区间重叠

## 人工抽检（演示视频用）

对 `demo-collision.ifc` 跑碰撞检查后，**至少应出现 1 对墙-墙碰撞**（外墙 A 与 内隔墙 B）。

属性：两面墙均有 Name 与 FireRating（2h），属性检查应为空缺失列表。

若 IFC 载入失败，演示改用 `test_samples/collision_positive.json`（金标正例）。
