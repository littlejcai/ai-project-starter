# 项目知识索引

只查缺少或已变化的资料，链接不递归展开。长文先列标题，再按标题提取；章节链接本身不会自动限制模型读取范围。提示文件用于发起任务，不是对应文档的附加必读项。

| 当前需要 | 查阅入口 |
|---|---|
| 首次全局理解 / 恢复进度 | 首次查 [README](../README.md)；接续查 [状态](status.md) 与当前任务的定位/交接，核对实际 Git 变更 |
| 需求、验收与业务含义 | [产品](product.md) |
| 架构、接口与数据变更 | [架构](architecture.md) 中登记的实际目录与接口事实源、[决策](decisions/README.md) |
| 初始化 / 业务实施 | 流程的 [新项目初始化](workflow.md#新项目初始化) / [业务功能与重要修复](workflow.md#业务功能与重要修复)；新任务用 [任务模板](tasks/TEMPLATE.md) |
| 重要取舍 / 风险不明 | [原则](principles.md) |
| 测试选择 / 验收证据 | 测试策略的 [范围与停止条件](testing.md#范围与停止条件) / [报告与证据管理](testing.md#报告与证据管理) |
| 接入检查 / 阶段推进 / 排障读取 | 配置指南的 [配置](verification-setup.md#配置) / [生命周期与转正](verification-setup.md#生命周期与转正) / [按需读取](verification-setup.md#按需读取) |
| 审查 / 委派与整合 | 审查的 [触发与输入](review.md#触发与输入)、[结果格式](review.md#结果格式)；协作的 [最小交接包](agents.md#最小交接包) |
| 平台验收 | [Web](profiles/web.md)、[小程序](profiles/miniprogram.md) |
| 发布 / 回退 | [发布清单](release.md) |
| 维护指令 / 评估 Skill | [指令维护](instruction-maintenance.md) |

读取示例：`python3 scripts/read_doc.py docs/testing.md --section "报告与证据管理"`。省略 --section 只列标题，遇到截断按提示续读；完整标准仍按任务需要查阅。

简单局部修改直接检查相关文件、测试或预览。业务规则、接口格式、架构决策各在上述位置维护一份；任务仅引用并记录本次变更和证据。

需要启动提示时选择：[新项目](../prompts/start-project.md)、[实施](../prompts/implement-task.md)、[接续](../prompts/review-and-resume.md)、[独立审查](../prompts/review-task.md)、[审查委派](../prompts/subagent-review.md)。

外部方法参考：[TDD](https://martinfowler.com/bliki/TestDrivenDevelopment.html)、[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Playwright 测试](https://playwright.dev/docs/best-practices)。选型时核对实际版本，不要求每次阅读。
