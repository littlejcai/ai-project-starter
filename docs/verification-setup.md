# 检查命令接入

Python 3.10+，无第三方 Python 依赖。业务依赖由实际工程安装。脚本以项目根目录为工作目录，不执行任意 shell 字符串。

## 配置

project.config.json 中填写真实 project_name。runtime_commands 仅记录安装与启动参数，不由 verify.py 自动执行。
schema_version 2 增加 lifecycle 与 tasks：前者记录当前阶段及各阶段必需门禁，后者定义任务 ID 正则、允许状态、默认状态和非活动状态。配置仍保持技术栈中立。
gates 是自动检查：quality、unit、integration、build、e2e。每项使用以下形式（这是语法示例，须替换为实际存在的命令）：

```json
{
  "status": "configured",
  "command": ["npm", "run", "test:unit"],
  "reason": "",
  "timeout_seconds": 300
}
```

command 必须是参数数组；不要写 `cmd1 && cmd2`，用项目自己的单一脚本封装多个步骤。`{python}` 会替换为当前解释器。
status 支持 configured / unconfigured / not_applicable。不适用项必须提供具体 reason；缺少环境、实现未完成不是“不适用”。
某层完全通过人工验证时可说明“没有此层自动化，人工步骤与证据记录在某任务”，但 full 结果不代表这些人工步骤已通过。
除 template 阶段外，current/quick/full 至少一个真实 configured 检查必须运行，全部不适用会失败；不能用示例检查伪装业务检查。

## 生命周期与转正

| stage | 含义 | 默认必需门禁 |
|---|---|---|
| template | 尚未接入具体产品 | 无；current 只跑独立 demo |
| discovery | 产品探索和风险实验 | quality、unit |
| application | 正式业务工程 | quality、unit、integration、build |
| release | 持续满足发布级自动检查 | 全部五层 |

默认值可以按项目真实结构调整，但 required_gates 只表示该阶段自动门禁，不包含人工、真机、部署或发布授权。推进前运行 `python3 scripts/promote_project.py --to <stage> --dry-run`；目标阶段的必需门禁未配置时拒绝推进，生命周期不能倒退。

## 四种配置范围

| profile | 范围 | 含义 |
|---|---|---|
| demo | 只运行 examples/registration 中测试 | 验证模板示例，不读取业务 gates |
| current | 当前生命周期阶段声明的门禁；template 时运行 demo | CI 和日常阶段验收 |
| quick | quality、unit | 开发中的快速反馈 |
| full | 所有五项 | 配置范围内自动回归，不包含人工发布授权或真机结果 |

current/quick/full 都先检查模板结构与本地链接。命令缺失、配置无效、非零退出、超时均会失败。
退出码：0 已执行范围通过；1 检查失败/未配置；2 配置或参数错误。失败日志在 artifacts/ 的本次目录。
脚本记录 UTC 时间、耗时、退出码、命令、配置快照、Git 提交及工作区状态。无 Git 时记录 null。
日志可能含业务工具输出，默认不提交；分享前脱敏。命令自身必须可靠返回失败码，不能吞掉测试失败。
超时会终止直接进程；命令需负责清理其启动的后台服务，尤其是端到端工具。

## CI

根目录 workflow 始终执行 doctor 与 current；只有 template 阶段运行框架回归和严格发行清单。离开 template 后，模板验证记录和清单更新器不再是项目结构必需项，框架回归脚本由 workflow 保留但会立即跳过；业务接入后补充固定版本工具、依赖与隔离服务准备，必要时归档脱敏日志。
不得把 current 绿灯解释为 current 未声明的范围已通过。发布门禁、人工验收与正式发布分别举证，并把配置变更纳入评审。
