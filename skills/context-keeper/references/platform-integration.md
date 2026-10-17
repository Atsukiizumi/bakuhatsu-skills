# 平台适配与自动化边界（2026-10，使用时以宿主版本为准）

## 共同原则

1. Skill 可以指示 Agent 在关键阶段更新 `.ai-context`，并可提供脚本；**本身不是常驻进程**。
2. Hooks 是事件通知；“压缩前 Hook”不意味着 Hook 本身可以要求宿主立即压缩。
3. 触发原生压缩依赖宿主 API、配置或用户命令；平台压缩结果不等于自动更新项目知识。
4. Hook 运行环境可能与代理的文件访问边界不同。默认事件脚本不读取/保存会话全文，不外发数据。
5. 修改宿主 `settings.json`、`config.toml` 应按现有配置合并，不覆盖整个文件。项目钩子/执行脚本必须由用户明确启用并审查。

## Codex

- Skills：项目根 `.agents/skills/context-keeper/`，可用 `$context-keeper`；可用的其他目录以当时文档为准。
- 宿主配置存在 `model_auto_compact_token_limit` 以及 `compact_prompt` 字段；压缩实现路径可能使某些提示覆写失效，故不能将其当成唯一保障。
- `PreCompact`/`PostCompact` hooks 存在并可用于审计；命令 Hook 信任/运行策略可能因环境不同。
- 建议先用 Skill 在里程碑维护检查点，再按宿主实际功能进行原生压缩；不要从普通 Python 脚本直接调用未经文档确认的 Codex 内部命令。
- Hook 示例为 `examples/codex-hooks.json.example`，需按平台支持路径、解释器及受信任配置手动合并。

## Claude Code

- Skills：`.claude/skills/context-keeper/`，命令 `/context-keeper`；默认可由模型基于描述激活。
- 有自动压缩与 `/compact`，以及 `PreCompact` / `PostCompact` / `SessionStart` hooks。`PostCompact` 提供压缩摘要以供审计，但不等于无损证明。
- `PreCompact` 不是稳定的“让模型现在再做一轮长推理”的位置；更可靠的做法是平时更新 ACTIVE/HANDOFF。
- `SessionStart`（包括 compact 来源）可以注入极短索引/恢复指令；不要每次注入整份 HANDOFF。
- Hook 示例在 `examples/claude-settings.json.example`；根据项目情况配置解释器与 Skill 安装位置。

## Gemini CLI

- Skills：`.gemini/skills/context-keeper/` 或 `.agents/skills/context-keeper/`。
- 配置 `contextManagement.historyWindow.maxTokens` 与 `retainedTokens`；它们是历史窗口策略，不是模型最大上下文窗口的直接百分比。
- 有 `PreCompress`（异步、advisory only），无法阻断或改写压缩；可用 `SessionStart` / `BeforeAgent` 维护恢复入口。
- Hooks stdout 必须为合法 JSON（无日志噪声）。Hook 示例在 `examples/gemini-settings.json.example`。

## 建议的用户接入顺序

先安装 Skill → 在项目根通过 `init` 创建 `.ai-context` → 让 Agent 完成第一次真实语义 checkpoint → 运行 `validate` → 经用户明确启用 Hooks → 模拟测试 Hook 输入 → 实测原生压缩后的恢复流程。

## 官方来源

- Codex: https://developers.openai.com/codex/skills
- Codex hooks: https://developers.openai.com/codex/hooks
- Codex config: https://developers.openai.com/codex/config-reference
- Claude Code: https://code.claude.com/docs/en/skills
- Claude hooks: https://code.claude.com/docs/en/hooks
- Gemini skills: https://geminicli.com/docs/cli/skills/
- Gemini hooks: https://geminicli.com/docs/hooks/reference/
- Gemini config: https://geminicli.com/docs/reference/configuration/
