# AI 项目开发基础框架 · v1.8.0

供个人或小团队用 AI 开发 Web、小程序和后端项目的工作模板，包含分层文档、任务和检查工具，不附带业务代码或语言示例。业务技术栈由具体项目选择。

## 开始使用

scripts/ 中的辅助工具使用 Python 3.10+ 标准库，仅负责项目检查和记录；不代表业务后端或测试必须使用 Python。命令在仓库根目录运行，Windows 可将 `python3` 替换为 `py -3`。
先在尚未修改的模板副本中检查发行完整性与模板结构：

```bash
python3 scripts/verify.py --profile current --readiness --strict-manifest
```

该命令一次完成配置、任务、结构、链接与发行哈希检查；template 默认不执行业务测试，业务阶段必须配置并运行真实检查。doctor 仍可单独做静态自检。

将 [AGENTS.md](AGENTS.md) 交给 AI，填写 [启动提示](prompts/start-project.md) 中的需求、交付范围、界面形态与已有品牌/设计资产。按 [开发流程](docs/workflow.md) 完成产品定义、关键实验、最小架构和第一条业务链路；只详细规划当前及下一里程碑。
后端、CLI 和无用户界面的项目不创建体验文档；有界面的项目在进入实际界面实现前，按需物化一份 `docs/experience.md`，记录品牌表达、用户旅程、信息架构、页面状态、视觉原则和验收方式。已有成熟规范时只记录其地址、版本与适用边界，不复制整套资产；仅在多端协作、独立品牌治理或内容明显膨胀时再拆分品牌与 UX/UI 文档。
技术方案确定后再创建真实源码、测试、契约和外部适配目录，并在 [技术方案](docs/architecture.md) 登记；模板不预建可能与实际技术栈冲突的占位目录。按 [配置指南](docs/verification-setup.md) 设置项目身份、运行命令和阶段检查，再推进生命周期。日常使用 `verify.py --profile current --readiness` 合并自检，或按任务单独选择检查；严格清单不用于跟踪业务开发改动。

## 核心用法

| 需要做什么 | 入口 |
|---|---|
| 定位项目资料、接续工作 | [知识索引](docs/index.md)、[当前状态](docs/status.md) |
| 新建业务任务 | `python3 scripts/new_task.py FEAT-001 "任务标题"`；ID 和状态可配置，不覆盖已有文件 |
| 选择检查、接入 CI、推进阶段 | [配置指南](docs/verification-setup.md) |
| 保存测试结论与证据 | [测试策略](docs/testing.md)：任务存结论，自动摘要关联执行记录，原始日志按需归档 |
| 验证本版本改动 | [验证记录](TEMPLATE-VALIDATION.md) |

业务规则与接口共同约束实现；复杂规则先做行为测试，两端及真实依赖按影响范围验收。第一性原理、风险审查、子 Agent 与可选 Skills 均通过知识索引按需使用。

## 从模板进入业务项目

`template → discovery → application → release` 表示自动检查配置阶段，定义在 project.config.json。`current` 执行当前阶段声明的检查，`quick` 固定执行 quality/unit，`full` 检查全部五层。必需检查未配置会失败。
`promote_project.py` 只检查配置并更新阶段，不执行测试或发布；具体步骤和限制见配置指南。发布仍需 [发布验收](docs/release.md)。
CI 在 template 阶段检查发行清单、结构与框架工具回归，进入业务阶段后检查项目状态并执行 current。业务接入时配置所需依赖、服务与构建环境。

## 模板维护与跨 AI 使用

本版沿用按需物化：技术方案确定后创建源码、测试、契约和适配目录；确认存在实际界面交付后再创建单一体验基线。模板不携带这些说明型占位目录，规则仍保留在 docs/，不会因为目录精简丢失契约、测试、体验约束或跨 AI 边界。按需命令见 [配置指南](docs/verification-setup.md#按需读取)。不引入目录生成器、测试缓存或调度层，历史改动见 Git 记录。
修改模板发行内容后运行 `python3 scripts/update_manifest.py`，再运行严格自检；模板/任务生成变更执行 `python3 scripts/test_framework.py`。不要靠刷新清单掩盖非预期改动。
公共规则只维护在 AGENTS.md 与 docs/；[CLAUDE.md](CLAUDE.md) 是薄入口。其他客户端如需专有入口，在确认其官方格式后新增一个只指向 AGENTS.md 的薄文件，不复制整套业务说明；客户端不自动读取时，显式要求先读 AGENTS.md。

创建日期：2026-09-12。原创模板可自由复制修改用于个人或商业项目，外部资料遵守其来源条款。密钥、生产数据和敏感日志不提交。
