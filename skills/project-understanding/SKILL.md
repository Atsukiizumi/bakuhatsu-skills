---
name: project-understanding
description: >
  从代码入口理解整个软件项目：拆出功能点并写清每个功能做什么，画出有证据的 UML 与 ER 图，
  再按 4+1 视图做 As-Is 分析。没有项目文档也能完成；已有文档只作交叉验证。
  适用于理解项目、项目全景、画 UML、画 ER、功能拆分、功能点、软件工程分析、
  给 Agent 建立项目模型，或用户运行 /project-understanding。
  默认只读，并把模型写入目标仓库 docs/project-model/。
---

# Project Understanding — 项目模型

为目标仓库建立一套人和后续 Agent 都能读的 As-Is 模型。功能点从代码入口得到。模型回答「项目现在是什么」，不回答「下一步怎么改」。

## 先决定模式

未指定时：`docs/project-model/` 已存在用 `refresh`，否则用 `build`。

| 模式 | 做到哪 | 写入 |
| --- | --- | --- |
| `inventory` | 只做第一遍 | `00-index.md` 和 `01-features.md` 的候选表 |
| `build` | 三遍都做；第一遍清单先落盘，再补卡片、图和分析 | `references/model.md` 里适用的全部文件 |
| `refresh` | 用当前代码重核有变化的入口 | 只改对不上的段落，保留仍然对得上的内容 |

用户说「只在对话里输出」时不写文件，仍按同一顺序在回复里给清单和模型。

## 每次执行

1. 确认目标仓库、模式和输出语言。语言跟随用户这次的用语；用户没指定时用中文。
2. 按 `references/reading.md` 做阅读。`inventory` 在第一遍结束。`build` 把候选清单写出后再进入第二遍。
3. 从第二遍开始，按 `references/model.md` 决定写哪些文件、画哪些图。骨架用 `assets/templates.md`。
4. 不修改、不格式化、不重命名业务代码，不安装依赖，不提交。跳过的搜索范围以 `reading.md` 为准。
5. 用户要风险、重构或改代码时，停止扩展本模型，改用 `project-reorganizer`。

## 回复里始终给的摘要

模式、功能候选数量、已写成卡片的数量、画出的图、文档对照是否做过、模型路径或「未落盘」、未读区域。不要把子 Agent 的原始输出贴进回复。
