# Context Keeper v2 — 软件开发 Agent 主动上下文管理 Skill

适合 Codex、Claude Code、Gemini CLI 和其他兼容 `SKILL.md` 的编程 Agent。实现**主动检查 → 保真记忆 → 持久检查点 → 原生压缩（宿主提供时）→ 恢复与验真**，而非仅做聊天总结。

## 快速安装

解压后保留完整 `context-keeper/` 文件夹：

| Agent | 项目级安装位置 | 常见调用方式 |
|---|---|---|
| Codex | `.agents/skills/context-keeper/` | `$context-keeper` |
| Claude Code | `.claude/skills/context-keeper/` | `/context-keeper` |
| Gemini CLI | `.gemini/skills/context-keeper/` 或 `.agents/skills/context-keeper/` | 通过技能发现/激活 |

可以共享一份源代码并按各平台支持方式做链接，但先验证目标系统的路径和文件访问权限。**只安装 Skill 就能手动运行；不会自动注册任何 Hook。**

## 第一次使用（在项目根执行）

```bash
# Windows 可把 python3 改为 py -3 或 python
python3 .agents/skills/context-keeper/scripts/context_keeper.py scan .
python3 .agents/skills/context-keeper/scripts/context_keeper.py init .
```

然后把下面的请求交给 Agent（不是直接执行脚本即可完成语义总结）：

> 使用 context-keeper maintain；读取项目入口、当前任务与 Git 状态，填完 `.ai-context/ACTIVE.md` 和 `.ai-context/HANDOFF.md` 的真实业务信息。标记已验证、设计目标和待验证项；不得修改业务代码或删除任何文件。最后运行静态校验。

```bash
python3 .agents/skills/context-keeper/scripts/context_keeper.py validate .
```

`init` 只创建缺失的 `.ai-context` 文件，不覆盖现有内容。`scan`、`validate` 只读。检查点里的 `[待填写]` 需要 Agent 根据真实上下文补全。

## 常用调用

- **主动压缩**：`使用 context-keeper compact，在安全边界保存 P0/P1、验证检查点，再按宿主能力压缩并恢复核对。`
- **日常维护**：`使用 context-keeper maintain，增量更新当前进度与决策，不生成重复长文档。`
- **交接**：`使用 context-keeper handoff，生成新会话可独立恢复的上下文。`
- **清理预览**：`使用 context-keeper cleanup，仅列清理候选；不删除。`

## “主动”的实现条件

Agent 在当前会话中能根据 Skill 主动选择里程碑检查点；**真正不需要用户反复提醒**，通常还需要你在项目顶层 AGENTS.md / CLAUDE.md / GEMINI.md 增加简短规则（见 `examples/project-rule-snippet.md`），或接入平台 Hooks。压缩前的 Hook 可能太晚，无法安全重新总结复杂对话，所以日常增量维护不可省略。

`references/platform-integration.md` 有详细的平台差异，`examples/` 有可审查但**需手动合并和改路径**的可选 Hook 配置。不要直接覆盖用户现有配置。

## 文件和脚本

- `SKILL.md`：实际执行策略。
- `references/`：触发、信息保留、证据、清理与平台适配。
- `assets/`：项目交接文件模板与恢复 Prompt。
- `scripts/context_keeper.py`：标准库 CLI，涵盖 `scan / init / validate / hook`，默认无网络访问。
- `references/acceptance-tests.md`：原生压缩后的业务语义与安全验收。
- `tests/`：基础单元测试，可用 `python3 -m unittest discover -s tests -v`。

## 重要边界

- 不会直接删除模型内部上下文，也无法保证平台摘要绝对无损。
- 不会把聊天历史或原始日志上传到外部服务。
- Hooks 可记录**事件元数据**，但不会自动理解整个对话；关键业务事实必须由 Agent 在安全的工作边界提炼保存。
- 所有破坏性清理均需要明确的候选清单与确认。
- Windows/macOS/Linux 需要本机可调用 Python 3.10 或更新版本；平台 Hook 路径要按安装位置调整。
