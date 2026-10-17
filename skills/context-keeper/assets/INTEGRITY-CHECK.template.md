# Compaction Integrity Check

> 执行时间：`[待填写]`；平台：`[待填写]`；原生压缩状态：`not-run | reported | verified`

| 检查项 | 结果（pass/fail/unknown） | 证据 |
| --- | --- | --- |
| 用户当前目标与验收条件没有丢失 | unknown | |
| P0 约束完整（字段、数值、边界） | unknown | |
| 当前任务/修改文件与 git 一致 | unknown | |
| 未提交/未跟踪工作完整记录 | unknown | |
| 已验证与未验证严格区分 | unknown | |
| 已否决方案/失败原因没有被忘记 | unknown | |
| 下一步可以直接执行 | unknown | |
| 重要结论有可回溯代码/文档证据 | unknown | |

如果有 `fail`：暂停依赖错误摘要的后续操作，先读取源码/原始决策恢复，再更正 ACTIVE/HANDOFF。
