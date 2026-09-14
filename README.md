# AI 项目开发基础框架 · v1.4.0

适用：个人或小团队由 AI 辅助开发的网页、小程序、后端项目。
这是一套可复制的工程工作模板，包含文档、任务、验证脚本和独立示例；尚未选定你的业务技术栈，也不包含已经完成的业务应用。

## 方法总结

1. PRD 同时明确用户、范围、关键业务规则与可判断的验收场景。
2. 对关键交互、平台能力和第三方依赖先做小验证，再细化技术方案。
3. 为当前完整业务链路明确数据模型、接口、权限、状态和异常。
4. 对复杂规则和重要状态先列场景，逐个测试失败、实现、通过、重构；简单局部修改按风险验证，不提前写完整个项目的测试代码。
5. 界面行为用浏览器或开发者工具验证；涉及平台能力和真实依赖时补真机与集成证据。
6. 项目知识分层读取，代码、约定、测试、任务记录一起更新。
7. 用真实执行记录判断完成，未配置、未执行、模拟通过不得写成业务通过。

## v1.4 的项目生命周期

项目通过 `template → discovery → application → release` 四个阶段从模板转为正式产品。每个阶段在 `project.config.json` 声明当前必须通过的自动门禁，`current` 只验证当前承诺，`full` 仍严格检查全部五层。
任务 ID 与状态改为项目配置，默认同时支持 `FEAT-001`、`FEAT-ID-001` 和 `M0-001`。项目自检会核对配置、当前门禁、任务文件和文档链接；模板发行清单只在 template 阶段严格验证，不跟踪后续业务文件。

## v1.3 的指令精简

入口只保留项目事实、授权边界、按需路由、命令与完成条件。初始化、业务功能、简单局部修改分别选择流程；验证充分后停止无依据的重复检查，既有必需门禁保留。
任务模板采用最小记录，风险分析、审查和协作按条件追加。审查提示共用一份标准，接续任务不默认重审全项目。
暂不新增通用 Skills；选择与维护方式见 [指令维护](docs/instruction-maintenance.md)。本次为文档调整，尚无模型效率对照结论。

## v1.2 的可选子 Agent 协作

按可独立完成的任务与预期收益选择协作；没有合适分工时单 Agent 完成。并行实现需满足接口稳定和工作区隔离条件。
主 Agent 统一维护任务、整合结果与最终验收。工具不支持子 Agent 时可采用独立会话或人工，并如实记录审查方式。
这次新增协作说明和提示模板，不包含自动调度器，也不新增模型、技术栈或运行依赖。

## v1.1 的原则与审查

六项原则：第一性原理、对抗性审查、简单设计、契约与不变量、证伪与最小实验、小批量与可回退变更。
低风险保持轻量；普通业务做一次实现审查；高风险在方案和实现阶段分别审查。
入口只放简短规则，详细方法按需读取，结论直接写入任务与决策。业务技术栈和 Python 辅助脚本要求不变。

## 5 分钟开始

需要 Python 3.10 或更高版本，只使用标准库。Windows 如果没有 python3，使用 `py -3` 替换命令前缀。所有命令从本目录运行。

```bash
python3 scripts/doctor.py --strict-manifest
python3 scripts/verify.py --profile current
python3 scripts/new_task.py FEAT-ID-001 "第一条完整业务链路"
```

第一条检查模板发行内容、配置、任务与文档；第二条按当前阶段运行检查，template 阶段只运行独立示例；第三条按项目配置创建任务且不覆盖已有文件。

若修改框架工具本身，可运行 `python3 scripts/test_framework.py` 检查错误传播、配置校验与任务文件保护；所有回归在临时副本执行。

然后把整个解压目录作为新项目起点，交给 AI 读取 [AGENTS.md](AGENTS.md)，使用 [启动任务说明](prompts/start-project.md)。
先填写 [产品定义](docs/product.md)、[技术方案](docs/architecture.md)、[当前状态](docs/status.md)，确定网页或小程序路径。
在 `src/`、`tests/` 中加入真正的业务代码和测试，按 [检查接入指南](docs/verification-setup.md) 配置 `project.config.json`。
只详细展开当前和下一里程碑，更远阶段先保留结果、依赖和待决问题，避免尚未验证的细节造成持续联动修改。

当前阶段的必需门禁配置完成后，先 dry-run 再推进生命周期：

```bash
python3 scripts/promote_project.py --to discovery --dry-run
python3 scripts/promote_project.py --to discovery
```

推进只修改 `project.config.json`，不会删除文件或替项目选择技术栈。随后按提示更新项目身份与状态；CI 会自动跳过模板框架回归，转而运行当前业务阶段门禁。`TEMPLATE-VALIDATION.md` 和清单更新器在离开 template 后不再是项目结构必需项，可在清理其文档引用后归档。

```bash
python3 scripts/verify.py --profile quick
python3 scripts/verify.py --profile current
python3 scripts/verify.py --profile full
```

quick 固定运行 quality/unit，current 运行当前阶段声明的必需门禁，full 检查全部五层。未配置的必需门禁会失败。
template 阶段的 current/demo 通过只表示示例规则测试通过；任何自动检查都不能替代真机、体验与发布验收。

## 从哪里阅读

- [项目知识目录](docs/index.md)：按任务选择资料。
- [开发流程](docs/workflow.md)：从启动到交付。
- [六项开发原则](docs/principles.md)：适用时机、边界和取舍。
- [对抗性审查](docs/review.md)：证据、分级和停止条件。
- [独立审查提示](prompts/review-task.md)：与任务接续分开使用。
- [子 Agent 协作](docs/agents.md)：触发条件、分工、版本交接与结果整合。
- [子 Agent 审查提示](prompts/subagent-review.md)：可以直接填写的委派模板。
- [测试策略](docs/testing.md)：如何分层、如何防止假通过。
- [已填写示例任务](examples/registration/FEAT-DEMO.md)：看一条规则怎样连接验收与测试。
- [发布清单](docs/release.md)：交付、部署与回退。
- [模板验证记录](TEMPLATE-VALIDATION.md)：本版本实际检查范围。

## 跨 AI 使用

公共说明只维护在 AGENTS.md 与 docs/。不同工具是否自动读取入口需要按实际客户端确认；没有自动读取能力时，手动要求先阅读 AGENTS.md。
CLAUDE.md 是轻量指引，其他工具可参照 adapters/README.md 接入。不保证所有工具自动识别相同文件名。

## 版本与使用

创建日期：2026-09-12；当前模板版本：v1.4.0。可自由复制、修改这些原创模板用于个人或商业项目；外部引用内容遵循各自来源条款。
建议初始化你自己的 Git 仓库，并随业务版本维护文档。不要把真实密钥、生产数据和含敏感信息的截图提交到仓库。
