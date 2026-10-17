# 新会话恢复指令（复制到新会话）

使用 context-keeper 的 `handoff/restore` 规则接续当前项目：

1. 先读取 `.ai-context/INDEX.md`、`.ai-context/ACTIVE.md`、`.ai-context/HANDOFF.md`，以及当前项目适用的 AGENTS.md / CLAUDE.md / GEMINI.md；不要一次全文加载无关 docs。
2. 执行 `git status --short --branch` 并读取当前 commit。识别所有未提交与未跟踪的文件，不执行清理命令。
3. 将 HANDOFF 的用户目标、P0 约束、改动文件和验证状态逐项对照最新源码与测试；冲突项标记 `conflict`，不要自行假设已实现。
4. 输出不超过 15 行的恢复摘要和关键风险，然后立即从“下一步”第一项继续执行。
5. 不得因为看到旧日志或历史摘要就覆盖用户的最新指令。
