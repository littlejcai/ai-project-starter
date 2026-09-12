# 检查命令接入

Python 3.10+，无第三方 Python 依赖。业务依赖由实际工程安装。脚本以项目根目录为工作目录，不执行任意 shell 字符串。

## 配置

project.config.json 中填写真实 project_name。runtime_commands 仅记录安装与启动参数，不由 verify.py 自动执行。
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
至少一个真实 configured 检查必须运行，全部不适用会失败；不能用示例检查伪装业务检查。

## 三种配置范围

| profile | 范围 | 含义 |
|---|---|---|
| demo | 只运行 examples/registration 中测试 | 验证模板示例，不读取业务 gates |
| quick | quality、unit | 开发中的快速反馈 |
| full | 所有五项 | 配置范围内自动回归，不包含人工发布授权或真机结果 |

quick/full 都先检查模板结构与本地链接。命令缺失、配置无效、非零退出、超时均会失败。
退出码：0 已执行范围通过；1 检查失败/未配置；2 配置或参数错误。失败日志在 artifacts/ 的本次目录。
脚本记录 UTC 时间、耗时、退出码、命令、配置快照、Git 提交及工作区状态。无 Git 时记录 null。
日志可能含业务工具输出，默认不提交；分享前脱敏。命令自身必须可靠返回失败码，不能吞掉测试失败。
超时会终止直接进程；命令需负责清理其启动的后台服务，尤其是端到端工具。

## CI

根目录 .github/workflows/template-check.yml 只检查模板和示例，名称明确区别于业务验收。
业务接入后，根据所选技术栈创建真实 workflow：检出代码 → 安装固定版本工具与依赖 → 准备隔离服务/测试数据 → 运行 full → 失败时归档脱敏日志。
不得直接把模板 workflow 的绿灯视为项目交付。仓库合并规则应要求真实业务检查，并把配置变更纳入评审。
