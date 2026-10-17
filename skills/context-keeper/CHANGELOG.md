# Changelog

## v2.0.0 — 2026-10-15

- 在初版 summarize/sync/cleanup/handoff 基础上，增加主动上下文触发与 P0–P4 分级保留。
- 明确“宿主原生压缩”与“项目知识持久化”的边界。
- 新增 INDEX/ACTIVE/HANDOFF 分层与完整性复核流程。
- 增加标准库 CLI 的只读 scan、显式 init、静态 validate 和 Hook 适配。
- 新增 Codex、Claude Code、Gemini CLI 可选 Hooks 配置示例（需手动合并与启用）。
- 增加基础单元测试及真实压缩后的验收测试清单。
