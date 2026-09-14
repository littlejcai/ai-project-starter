# 项目知识索引

依据当前目标按下表定位缺少的资料；已有上下文有效时无需重读。链接不是递归阅读清单，提示模板只在需要发起对应任务时使用。简单局部修改可直接定位相关代码、测试或文档。

| 触发场景 | 按需查阅 | 需要核对的实现 |
|---|---|---|
| 首次建立项目全局理解 | [README](../README.md)、[当前状态](status.md)、[产品](product.md) | 工程配置、现有启动命令 |
| 重要需求/架构选择、反复失败或风险不明 | [开发原则](principles.md) | 当前目标、约束与证据 |
| 子 Agent 委派与整合 | [协作约定](agents.md)、[委派提示](../prompts/subagent-review.md) | 任务目标、版本、文件边界、环境与证据 |
| 审查方案或实现 | [审查流程](review.md)、[审查提示](../prompts/review-task.md) | 需求、约定、真实差异、测试 |
| 澄清需求 | [产品](product.md)、[任务模板](tasks/TEMPLATE.md) | 已有行为与相关测试 |
| 架构或跨模块变更 | [架构](architecture.md)、[决策目录](decisions/README.md) | 模块边界、依赖、数据流 |
| 接口与数据变更 | [接口约定](../contracts/README.md)、[架构](architecture.md) | 运行时校验、迁移、调用方 |
| 业务功能或重要修复 | 当前任务；流程或验证范围不明时查 [流程](workflow.md)、[测试策略](testing.md) | 相关 src 与 tests |
| 简单局部修改 | 相关文件及现有验收，不必新建任务 | 变更位置、调用方或预览 |
| 评估新增 Skill 或优化指令 | [指令维护](instruction-maintenance.md) | 实际失败案例、工具与对照证据 |
| 接入检查 | [配置说明](verification-setup.md) | [验证配置](../project.config.json) |
| 项目从模板转为探索/正式工程 | [配置说明](verification-setup.md)、[流程](workflow.md) | 生命周期阶段、当前必需门禁、项目身份与 CI |
| 网页验收 | [网页路径](profiles/web.md) | 页面、服务、浏览器测试 |
| 小程序验收 | [小程序路径](profiles/miniprogram.md) | 页面、开发者工具、真机 |
| 恢复任务 | [当前状态](status.md)、当前任务的交接段落 | Git 变更、失败检查、相关提交 |
| 发布 | [发布清单](release.md) | 环境配置、迁移、构建、回退 |

## 资料责任

product.md 记录业务含义和验收依据；contracts/ 记录机器可读的数据与接口格式；architecture.md 解释结构和约束；任务记录当前变更与证据；决策记录解释重大取舍。
文档和代码一起版本化。发现冲突时，明确事实、期望与需要确认的问题，不静默覆盖。

## 外部参考

- [TDD：Martin Fowler](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [AGENTS.md：OpenAI 官方文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [网页测试：Playwright 官方建议](https://playwright.dev/docs/best-practices)

上述内容用于方法依据；具体工具版本在实际选型时重新核对官方文档。
