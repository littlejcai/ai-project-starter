# 项目知识索引

只查缺少或已变化的资料，链接不递归展开。提示文件用于发起任务，不是对应文档的附加必读项。

| 当前需要 | 查阅入口 |
|---|---|
| 全局理解 / 恢复进度 | [README](../README.md)、[状态](status.md)、当前任务；核对实际 Git 变更 |
| 需求、验收与业务含义 | [产品](product.md) |
| 架构、接口与数据变更 | [架构](architecture.md)、[接口约定](../contracts/README.md)、[决策](decisions/README.md) |
| 初始化 / 业务实施 | [流程](workflow.md)；新任务使用 [任务模板](tasks/TEMPLATE.md) |
| 重要取舍 / 风险不明 | [原则](principles.md) |
| 测试选择 / 接入检查和阶段推进 | [测试策略](testing.md) / [配置指南](verification-setup.md) |
| 审查 / 委派与整合 | [审查标准](review.md) / [协作约定](agents.md) |
| 平台验收 | [Web](profiles/web.md)、[小程序](profiles/miniprogram.md) |
| 发布 / 回退 | [发布清单](release.md) |
| 维护指令 / 评估 Skill | [指令维护](instruction-maintenance.md) |

简单局部修改直接检查相关文件、测试或预览。业务规则、接口格式、架构决策各在上述位置维护一份；任务仅引用并记录本次变更和证据。

需要启动提示时选择：[新项目](../prompts/start-project.md)、[实施](../prompts/implement-task.md)、[接续](../prompts/review-and-resume.md)、[独立审查](../prompts/review-task.md)、[审查委派](../prompts/subagent-review.md)。

外部方法参考：[TDD](https://martinfowler.com/bliki/TestDrivenDevelopment.html)、[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Playwright 测试](https://playwright.dev/docs/best-practices)。选型时核对实际版本，不要求每次阅读。
