# project-reorganizer v2（Sub-agents 版）

让主 Agent 自动评估是否适合并行审查项目，必要时委派 Sub-agents 分别检查架构、业务流程、数据库和代码风险，再由主 Agent 交叉验证并汇总。默认 `audit` 只读分析；支持 `plan` 和用户批准范围内的 `implement`。

## 文件结构

```text
project-reorganizer-v2/
├── SKILL.md                                # 必需，主工作流程
├── references/
│   ├── subagent-orchestration.md           # 分工与委派合同
│   ├── model-selection.md                  # 模型询问、可用性与回退
│   └── review-checklist.md                 # 工程审查
├── assets/
│   └── report-template.md                  # 汇总报告
└── examples/
    ├── codex/.codex/agents/                # 可选 Codex agent TOML 示例
    └── claude/.claude/agents/              # 可选 Claude Code agent MD 示例
```

## 安装

1. Codex：把 **整个文件夹**（可自行重命名为 `project-reorganizer`）放到仓库 `.agents/skills/` 目录。
2. Claude Code：放到 `.claude/skills/` 目录。
3. **可选**：若要有专用的子智能体角色，将 `examples/codex/.codex/agents/*.toml` 分别复制到仓库 `.codex/agents/`，或将 `examples/claude/.claude/agents/*.md` 复制到 `.claude/agents/`。这一步是可选的；宿主内置的泛用子智能体也可被 Skill 调用。
4. 文件复制与模型/并发配置是用户自行安装或明确允许的设置操作，Skill 的 audit 模式**不能自动修改**工作区设置。
5. 示例子 Agent 未绑定固定付费型号，Codex 模板省略 `model`，Claude 模板采用 `model: inherit`。需要分配具体模型时，在宿主支持的委派配置中指定或由用户编辑配置。

## 使用

**自动委派**：

> 使用 project-reorganizer 以 audit 模式梳理当前仓库。请在能提高效率的情况下自主调用 Sub-agents，按架构、业务和质量分工。所有任务只读，并在最终报告中说明实际使用的子智能体和模型。

**明确选择模型策略**：

> 使用 project-reorganizer 梳理 WMS；先问我本次要采取 auto / economy / balanced / quality / manual 中哪一种模型策略，再根据可用模型并行委派，不要修改业务代码。

**自定义分配**：

> 使用 project-reorganizer；模型策略为 manual。主 Agent 使用当前模型；Explorer 用我运行环境中最便宜的可用模型；业务/数据库审查优先较强推理模型。若无法选模型，回退继承并记录原因。

## 原则

- Skill 仅表达任务策略，不保证运行器真正支持创建 Sub-agents 或切换模型。
- 不为了“多智能体”而多开模型，控制上下文冗余、并发与开销。
- 安全与业务授权不可被子 Agent 绕过；重要结论必须能回溯至代码证据。

官方说明：
- https://developers.openai.com/codex/subagents
- https://code.claude.com/docs/en/sub-agents
