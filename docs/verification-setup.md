# 检查命令接入

Python 3.10+，无第三方 Python 依赖。业务依赖由实际工程安装。脚本以项目根目录为工作目录，不执行任意 shell 字符串。

## 配置

project.config.json 中填写真实 project_name。runtime_commands 仅记录安装与启动参数，不由 verify.py 自动执行。
schema_version 2 增加 lifecycle 与 tasks：前者记录当前阶段及各阶段必需门禁，后者定义任务 ID 正则、允许状态、默认状态和非活动状态。配置仍保持技术栈中立。
模板只提供 docs/、prompts/、scripts/ 和 CI 等治理入口，不预建源码、测试、契约或适配器目录；技术方案确定后按实际工程创建并接入对应门禁。
gates 是自动检查：quality、unit、integration、build、e2e。每项使用以下形式（这是语法示例，须替换为实际存在的命令）：

```json
{
  "status": "configured",
  "command": ["<测试工具>", "<单元测试参数>"],
  "reason": "",
  "timeout_seconds": 300
}
```

command 必须是参数数组；不要写 `cmd1 && cmd2`，用项目自己的单一脚本封装多个步骤。`{python}` 会替换为当前解释器。
status 支持 configured / unconfigured / not_applicable。不适用项必须提供具体 reason；缺少环境、实现未完成不是“不适用”。
某层完全通过人工验证时可说明“没有此层自动化，人工步骤与证据记录在某任务”，但 full 结果不代表这些人工步骤已通过。
业务范围的 current/quick/full 至少执行一个真实 configured 检查，全部不适用会失败。阶段 required_gates 中的每项必须是 configured，not_applicable 也不能满足阶段要求；确实不适用时依据项目事实评审调整阶段声明，不能因检查失败而降级。quick/full 可接受有具体理由的不适用项；不能用模板结构检查伪装业务测试。

## 生命周期与转正

| stage | 含义 | 默认必需门禁 |
|---|---|---|
| template | 尚未接入具体产品 | 默认无；current 仅检查配置/结构；显式声明的工具门禁仍执行 |
| discovery | 产品探索和风险实验 | quality、unit |
| application | 正式业务工程 | quality、unit、integration、build |
| release | 持续满足发布级自动检查 | 全部五层 |

默认值可依据项目事实调整，required_gates 仅声明自动检查范围；必需检查变更须评审，不能为消除失败而删减。阶段不是用户审批节点，也不代表人工、真机、部署或发布验收完成。

推进示例（已填写项目名称，且 discovery 的真实检查命令已配置）：

```bash
python3 scripts/promote_project.py --to discovery --dry-run
python3 scripts/promote_project.py --to discovery
python3 scripts/verify.py --profile current --readiness
```

前两条只验证配置是否允许推进；dry-run 不写文件，正式推进仅更新 project.config.json，二者都不执行测试。最后一条合并静态自检与当前阶段自动检查；失败须处理，不能宣称阶段验收通过。
工具允许向任一更后阶段推进，拒绝同阶段或倒退；目标阶段必需项未 configured 会拒绝。同步 AGENTS.md、README.md 与状态中的真实项目身份。

## 三种配置范围

| profile | 范围 | 含义 |
|---|---|---|
| current | 当前阶段声明的门禁；template 默认仅配置/结构检查 | CI 和日常阶段检查，范围明确写入报告 |
| quick | quality、unit | 开发中的快速反馈 |
| full | 所有五项 | 配置范围内自动回归，不包含人工发布授权或真机结果 |

v1.5 移除了业务示例及 demo profile，旧命令会明确拒绝；不要将替换后的 current 模板结构检查当作原业务测试。
current/quick/full 都先检查模板结构与本地链接。--readiness 同时检查 doctor 的任务/阶段状态；--strict-manifest 隐含 --readiness，并在 template 阶段校验发行哈希。配置加载与校验、文档结构扫描在组合调用中各执行一次，清单另做必要哈希检查；没有跨运行缓存，不跳过业务门禁。命令缺失、配置无效、非零退出、超时均会失败。
退出码：0 已执行范围通过；1 检查失败/未配置；2 配置或参数错误。失败日志在 artifacts/ 的本次目录。
脚本在独立运行目录写入 report.json 和 summary.md，记录 UTC 时间、耗时、退出码、范围、Git 提交及工作区状态。可附加 `--task FEAT-001` 关联已有任务，无 Git 时记录 null；证据留存见 [测试策略](testing.md)。
日志可能含业务工具输出，默认不提交；分享前脱敏。命令自身必须可靠返回失败码，不能吞掉测试失败。
超时会终止直接进程；命令需负责清理其启动的后台服务，尤其是端到端工具。

## 自检、任务与模板清单

| 场景 | 命令 |
|---|---|
| 日常自检＋阶段检查 | `python3 scripts/verify.py --profile current --readiness` |
| 仅静态自检 | `python3 scripts/doctor.py` |
| 仅检查必需结构与本地链接 | `python3 scripts/check_template.py` |
| 创建任务；ID/状态来自配置 | `python3 scripts/new_task.py FEAT-001 "任务标题"` |
| 检查未修改的模板发行副本 | `python3 scripts/doctor.py --strict-manifest` |
| 模板维护者更新预期发行内容 | `python3 scripts/update_manifest.py`，随后严格自检 |
| 框架工具或任务生成变更 | `python3 scripts/test_framework.py`（即使已进入业务阶段） |

默认任务 ID 支持 FEAT-001、FEAT-ID-001、M0-001；创建器拒绝覆盖和路径穿越，状态须使用配置中的精确值。
在 template 阶段新增任务或修改文件后，旧发行清单出现差异是预期行为。业务开发使用普通 doctor；模板发行维护才更新清单。此阶段 CI 仍严格校验清单，因此开始业务前按实际就绪状态完成阶段接入；尚未具备条件时不能把失败写成通过，也不能仅为绿灯跳过门禁。
离开 template 后，严格清单参数不再校验发行哈希；可清理引用后归档 TEMPLATE-VALIDATION.md 和清单更新器，清单不跟踪业务文件。

## 按需读取

```bash
python3 scripts/read_doc.py docs/testing.md
python3 scripts/read_doc.py docs/testing.md --section "报告与证据管理"
python3 scripts/verify.py --report RUN_ID
python3 scripts/verify.py --report RUN_ID --check unit
python3 scripts/verify.py --report RUN_ID --check unit --tail 40
```

RUN_ID 使用执行输出中 artifacts/ 下的实际目录名。报告读取不运行测试、不修改报告或任务：默认只列失败/警告摘要，不读入整份配置；--check 展开一个检查的诊断，--tail 才输出日志末尾（最多 200 行、12000 字符）。配置错误可用 --check configuration 查看。读取成功退出 0，原测试结论以输出中的 result/exit_code 为准；读取失败退出 2。
文档工具支持本项目 Markdown 的 # 标题，忽略代码围栏内的伪标题。默认仅列标题；--section 精确匹配唯一标题并包含其子节，默认最多 80 行/12000 字符，可用 --start-line 续读，--max-lines 上限 200。超长单行按提示另行读取。工具不递归跟随链接，也不读取项目外路径。
这些入口只限制返回内容；内部读取文件不等于全部内容进入模型上下文。未有模型耗时或 token 对照结果。

## CI

根目录 workflow 用 `verify.py --profile current --readiness --strict-manifest` 一次完成严格静态自检与 current，再运行带 --if-template 的框架回归；离开 template 后仅跳过发行哈希和框架回归，任务/配置/链接及当前阶段检查仍执行。业务接入后补充固定版本工具、依赖与隔离服务准备。verify 运行后无论成功失败都尝试归档 summary.md，保留 14 天；原始报告、配置与日志不默认上传，不能用摘要代替整个 workflow 状态。
不得把 current 绿灯解释为 current 未声明的范围已通过。发布门禁、人工验收与正式发布分别举证，并把配置变更纳入评审。
