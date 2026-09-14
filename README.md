# AI 项目开发基础框架 · v1.4.1

供个人或小团队用 AI 开发 Web、小程序和后端项目的工作模板，包含分层文档、任务、检查工具及独立示例。业务技术栈和真实应用尚未接入。

## 开始使用

工具需要 Python 3.10+，仅用标准库；业务语言不限。命令在仓库根目录运行，Windows 可将 `python3` 替换为 `py -3`。
先在尚未修改的模板副本中检查发行完整性与示例：

```bash
python3 scripts/doctor.py --strict-manifest
python3 scripts/verify.py --profile current
```

`doctor` 检查配置、任务与链接，不执行业务测试；template 阶段的 `current` 只运行独立示例，不表示业务通过。

将 [AGENTS.md](AGENTS.md) 交给 AI，填写 [启动提示](prompts/start-project.md) 中的需求与交付范围。按 [开发流程](docs/workflow.md) 完成产品定义、关键实验、最小架构和第一条业务链路；只详细规划当前及下一里程碑。
在 `src/`、`tests/` 接入真实代码，按 [配置指南](docs/verification-setup.md) 设置项目身份、运行命令和阶段检查，再推进生命周期。日常使用 `doctor.py` 与按任务选择的检查；严格清单不用于跟踪业务开发改动。

## 核心用法

| 需要做什么 | 入口 |
|---|---|
| 定位项目资料、接续工作 | [知识索引](docs/index.md)、[当前状态](docs/status.md) |
| 新建业务任务 | `python3 scripts/new_task.py FEAT-001 "任务标题"`；ID 和状态可配置，不覆盖已有文件 |
| 选择检查、接入 CI、推进阶段 | [配置指南](docs/verification-setup.md) |
| 查看完整任务示例 | [报名规则示例](examples/registration/FEAT-DEMO.md)；只含纯函数规则验证 |
| 验证本版本改动 | [验证记录](TEMPLATE-VALIDATION.md) |

业务规则与接口共同约束实现；复杂规则先做行为测试，两端及真实依赖按影响范围验收。第一性原理、风险审查、子 Agent 与可选 Skills 均通过知识索引按需使用。

## 从模板进入业务项目

`template → discovery → application → release` 表示自动检查配置阶段，定义在 project.config.json。`current` 执行当前阶段声明的检查，`quick` 固定执行 quality/unit，`full` 检查全部五层。必需检查未配置会失败。
`promote_project.py` 只检查配置并更新阶段，不执行测试或发布；具体步骤和限制见配置指南。发布仍需 [发布验收](docs/release.md)。
CI 在 template 阶段检查发行清单、示例与框架回归，进入业务阶段后检查项目状态并执行 current。业务接入时配置所需依赖、服务与构建环境。

## 模板维护与跨 AI 使用

本版精简重复入口和版本介绍，澄清阶段推进与清单边界；保留 v1.4 的生命周期工具、任务配置和全部检查行为。历史变更见 Git 记录。
修改模板发行内容后运行 `python3 scripts/update_manifest.py`，再运行严格自检；模板/任务生成变更执行 `python3 scripts/test_framework.py`。不要靠刷新清单掩盖非预期改动。
公共规则只维护在 AGENTS.md 与 docs/；[CLAUDE.md](CLAUDE.md) 是薄入口，其他工具参照 [适配说明](adapters/README.md)。客户端不自动读取时，显式要求先读 AGENTS.md。

创建日期：2026-09-12。原创模板可自由复制修改用于个人或商业项目，外部资料遵守其来源条款。密钥、生产数据和敏感日志不提交。
