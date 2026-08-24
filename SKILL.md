---
name: chan-yan-methodology
description: >-
  HKU 产研五阶段方法论：澄清原始诉求 → 产品需求(PRD) → 界面原型图 → 技术方案 → 编写代码。
  支持路径 A 最小 Loop：state 落盘、规则 PLAN、单 tick 续跑、阶段 Gate。
  每阶段使用 prompts/ 目录中的固定 prompt，不得改写。
  Use when the user mentions 产研、澄清诉求、出 PRD、界面原型、技术方案、检查点实现、loop tick,
  or when working under Test/HKU/ on product prototyping or agent projects.
---

# 产研方法论

按顺序推进五个阶段。每次只执行用户指定的阶段；未指定时从阶段一开始。

**硬性规则**

1. 进入某阶段前，先完整读取 [prompts/](prompts/) 中对应文件，并**原样遵循**其中的 prompt，不得改写、删减或合并步骤。
2. 前一阶段产出经用户确认后，再进入下一阶段。
3. 阶段产出写入当前项目目录（默认 `Test/HKU/` 或其子目录），文件名由用户指定或按阶段默认命名。

## 工作流总览

```
任务进度：
- [ ] 阶段一：澄清原始诉求
- [ ] 阶段二：出产品需求（PRD）
- [ ] 阶段三：出界面原型图
- [ ] 阶段四：出技术方案
- [ ] 阶段五：编写代码（Checkpoint 模式）
```

| 阶段 | 目标 | Prompt 文件 | 典型产出 |
|------|------|-------------|----------|
| 一 | 澄清原始诉求 | [prompts/01-澄清原始诉求.md](prompts/01-澄清原始诉求.md) | 《业务诉求澄清报告》 |
| 二 | 出产品需求 | [prompts/02-出产品需求.md](prompts/02-出产品需求.md) | PRD |
| 三 | 出界面原型图 | [prompts/03-出界面原型图.md](prompts/03-出界面原型图.md) | ≥3 种落地页方案 + 设计说明 |
| 四 | 出技术方案 | [prompts/04-出技术方案.md](prompts/04-出技术方案.md) | 技术方案与实现计划 |
| 五 | 编写代码 | [prompts/05-编写代码.md](prompts/05-编写代码.md) | 按检查点实现的代码与测试 |

## 阶段衔接

| 本阶段输入 | 来源 |
|------------|------|
| 阶段一 | 用户提供的原始材料（任务说明、聊天记录、客户原话等） |
| 阶段二 | 阶段一《业务诉求澄清报告》或等效确认结论 |
| 阶段三 | 阶段二 PRD |
| 阶段四 | PRD + 已选 UI 设计稿 + 测试材料 |
| 阶段五 | PRD + UI 设计 + 技术方案 + 实现计划 + `test_samples/` |

## 执行步骤

1. 确认当前阶段与用户提供的材料路径。
2. **读取**对应 `prompts/*.md` 全文。
3. 以该 prompt 中的角色与规则开展对话或产出，不额外覆盖 prompt 里的交流方式（如「每次只问一个问题」）。
4. 阶段结束按 prompt 要求停下，等待用户确认后再进入下一阶段。

## 项目目录约定

- `docs/`：各阶段文档（见 [references/artifact-paths.md](references/artifact-paths.md)）
- `design/`：UI 方案与设计说明
- `data/state/<taskId>.json`：Loop 任务状态（示例：`hku-agent-test`）
- `data/logs/`：每 tick 日志
- `memory.md`：长期约束（阶段五 checkpoint 后更新）
- `test_samples/`：测试输入与标准答案（阶段四起）

---

## Loop（路径 A · 最小投入）

用规则引擎驱动五阶段，**每次只跑一个 tick**，状态落盘可续跑。详见 [references/loop-strategy.md](references/loop-strategy.md)。

### 快速开始

```
@Test/HKU/prompts/00-loop-tick.md taskId=hku-agent-test
```

或：`跑 loop tick，taskId=hku-agent-test`

初始状态：[data/state/hku-agent-test.json](data/state/hku-agent-test.json)（已指向 HKU 笔试原始诉求）

### 四步

| 步 | 动作 |
|----|------|
| PERCEIVE | 读 `data/state/<taskId>.json` + 已有 artifacts |
| PLAN | 按 loop-strategy 规则表选**一个**动作 |
| ACT | 原样遵循 `prompts/01–05` 对应文件 |
| REFLECT | 更新 state、`tick+=1`、写 `data/logs/`、跑 `scripts/check-gate.sh` |

### 人工确认

阶段 1–4 产出就绪后 `phaseStatus → awaiting_human`。用户说 `确认 clarify` / `确认 prd` / `确认 ui` / `确认 tech` 后下一 tick 才进下一阶段。

阶段 5 按 checkpoint 与测试通过推进（每 checkpoint 仍等人确认，同 `prompts/05`）。

### 参考文件

| 文件 | 用途 |
|------|------|
| [references/loop-strategy.md](references/loop-strategy.md) | PLAN 规则、触发方式、日志格式 |
| [references/phase-gates.md](references/phase-gates.md) | 各阶段完成判定 |
| [references/skill-map.md](references/skill-map.md) | 阶段 → prompt → 输入输出 |
| [references/artifact-paths.md](references/artifact-paths.md) | 默认产物路径 |
| [config/task-state.example.json](config/task-state.example.json) | 状态字段模板 |
| [prompts/00-loop-tick.md](prompts/00-loop-tick.md) | 单 tick 执行 prompt |
| [scripts/check-gate.sh](scripts/check-gate.sh) | 文件级 Gate 检查 |
