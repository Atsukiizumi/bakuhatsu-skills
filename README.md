# skill-workspace

个人 Agent Skills 仓库。在这里编写自己用的 skill，再用 [skills CLI](https://github.com/vercel-labs/skills) 安装到本机 Grok。

每个 skill 是 `skills/<name>/` 下的一个目录，入口是 `SKILL.md`。frontmatter 里的 `name` 用小写字母、数字和连字符，并且和目录名一致。`description` 写清这个 skill 做什么、在什么说法下应该被用到。

```text
skill-workspace/
├── README.md
└── skills/
    ├── context-keeper/
    ├── project-reorganizer/
    └── project-understanding/
```

## 安装到本机 Grok

在仓库根目录执行。只指定 Grok 时，CLI 会把文件复制到 `~/.grok/skills/`。改完源文件后需要再执行一次，已安装副本才会更新。

```powershell
npx skills add . -g -a grok -y
```

只装其中一个：

```powershell
npx skills add . -g -a grok -s context-keeper -y
npx skills add . -g -a grok -s project-reorganizer -y
npx skills add . -g -a grok -s project-understanding -y
```

装好后，在 Grok 里用 `/context-keeper`、`/project-reorganizer` 和 `/project-understanding`。描述匹配时也会自动调用。

## context-keeper

管理软件开发 Agent 的上下文生命周期：主动检查上下文是否还健康，把必须留下的事实保真写进检查点，准备宿主原生压缩，压缩后核对，以及把工作交接给新会话。目标是留下完成任务所必需的事实，而不是把对话压得越短越好。

源码在 [`skills/context-keeper/`](skills/context-keeper/)。执行策略见 `SKILL.md`，安装与脚本说明见该目录下的 `README.md`。

未指定模式时按 `maintain` 执行。

| 模式 | 做什么 |
| --- | --- |
| `inspect` | 盘点仓库、规则、已有摘要和上下文指标，不改文件 |
| `maintain` | 在里程碑增量更新 `.ai-context/ACTIVE.md` 和 `HANDOFF.md` |
| `compact` | 先保存并校验检查点，再按宿主能力请求原生压缩，压缩后核对 |
| `sync` | 核对仍然有效的事实，更新权威文档或给出 diff |
| `handoff` | 生成新会话可以独立恢复的交接包 |
| `cleanup` | 只列出清理候选；删除前必须逐项确认 |

检查点写在目标项目的 `.ai-context/`：`INDEX.md`、`ACTIVE.md`、`HANDOFF.md`。脚本是 `scripts/context_keeper.py`，提供 `scan`、`init`、`validate`、`hook`。`init` 只创建缺失文件，`scan` 和 `validate` 只读。需要本机 Python 3.10 或更新版本。

可以说：

> 使用 context-keeper maintain。读取项目入口、当前任务和 Git 状态，填完 `.ai-context/ACTIVE.md` 和 `.ai-context/HANDOFF.md`。标出已验证项、设计目标和待验证项。不要改业务代码，最后做静态校验。

> 使用 context-keeper compact。在安全边界保存 P0/P1，校验检查点，再按宿主能力压缩并恢复核对。

> 使用 context-keeper handoff。生成新会话可以独立恢复的上下文。

它不会自行清空模型窗口，也不会把聊天记录上传到外部服务。清理已有文件前会先给出候选清单。

## project-reorganizer

系统梳理一个已有软件项目：架构、模块职责、业务流程、数据库和工程质量。主 Agent 负责范围、分工和交叉验证；宿主支持且确实能省时间时，可以并行调用子 Agent。结论必须能回到代码位置。默认只读。

源码在 [`skills/project-reorganizer/`](skills/project-reorganizer/)。工作流见 `SKILL.md`，分工、模型选择和审查清单在 `references/`，报告模板在 `assets/report-template.md`。

用户只说「梳理项目」时使用 `audit`。

| 模式 | 做什么 | 能否改业务代码 |
| --- | --- | --- |
| `audit` | 审查现状和问题 | 否 |
| `plan` | 写出分阶段方案和任务卡 | 否 |
| `implement` | 实施已经明确批准的任务卡 | 仅限批准范围 |

报告默认写在对话里，包含执行摘要、项目地图、模块与架构、关键业务和数据流、风险清单、分阶段任务卡，以及实际用了哪些子 Agent。只有明确要求落盘时，才写到指定路径或 `docs/project-review/`。

可以说：

> 使用 project-reorganizer，以 audit 模式梳理当前仓库。能提高效率时自主调用子 Agent，按架构、业务和质量分工。全部只读，并在报告里说明实际使用的子 Agent 和模型。

> 使用 project-reorganizer 梳理这个项目。先问我这次用 auto、economy、balanced、quality 还是 manual，再并行委派。不要改业务代码。

Skill 只描述任务策略。宿主没有子 Agent 或不能切换模型时，主 Agent 顺序完成，并在报告里说明。

## project-understanding

从代码入口理解整个项目：列出功能点并写清每个功能做什么，画出有证据的 UML 和 ER 图，再按 4+1 视图做 As-Is 分析。没有 `docs/` 也能做。已有文档只用来和代码对照，不能直接当成事实。

源码在 [`skills/project-understanding/`](skills/project-understanding/)。阅读步骤在 `references/reading.md`，模型里有哪些文件在 `references/model.md`。

默认写到目标仓库的 `docs/project-model/`。不改业务代码。风险和重构交给 `project-reorganizer`。

| 模式 | 做什么 |
| --- | --- |
| `inventory` | 只收集入口，交出功能候选清单 |
| `build` | 先出清单，再写功能卡、图和分析 |
| `refresh` | 模型已存在时，只更新和当前代码对不上的部分 |

阅读分三遍。第一遍只记入口并分组。第二遍每个入口只读处理函数、它直接调用的方法，以及它写入的数据，能写清「触发 → 规则 → 状态变化 → 结果」就停。第三遍才对照 README 和 `docs/`，结果标为 `matches`、`stale`、`unimplemented`、`undocumented` 或 `conflict`。

可以说：

> 使用 project-understanding，先以 inventory 模式列出当前仓库的功能候选。不要读实现，也不要改代码。

> 使用 project-understanding 为当前仓库建立项目模型。功能从代码入口归纳，文档只做交叉验证。画出有证据的 UML 和 ER，写入 docs/project-model/。

## 新写一个 skill

1. 建立 `skills/<name>/SKILL.md`。
2. frontmatter 至少写 `name` 和 `description`。
3. 长说明放 `references/`，可执行辅助放 `scripts/`，模板放 `assets/`。
4. 用上面的安装命令装到 Grok，再跑一次对应的 slash command。
5. 把新 skill 补进本文件的目录树和正文。
