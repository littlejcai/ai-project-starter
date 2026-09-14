# 模板验证记录 · v1.4.1

日期：2026-09-14；环境：Linux，Python 3.12.14。
基线：GitHub main `b0af5402e3cfed10cba7ddda8039e232af47194d`，46 个文件已逐一核对 Git blob SHA。

## 变更与审查

精简 README、AGENTS、索引、原则、协作和状态；将重复任务填写规则集中到流程页，详细命令集中到配置指南。澄清 promote 仅校验配置、不执行测试，以及模板发行清单与业务开发的边界。
生命周期、门禁默认值、任务 ID/状态配置、Python 脚本、示例与 CI 行为保持不变。第一性原理、风险审查、真实验证和授权/隔离要求保留。
主 Agent 自审核对路由、风险与证据要求、实际脚本语义和任务模板兼容性；不是独立人员或第二模型审查。

## 实际验证

| 检查 | 结果 | 范围 |
|---|---|---|
| `python3 scripts/check_template.py` | 通过 | 必需文件与本地 Markdown 链接；不验证外部链接和标题锚点 |
| `python3 scripts/test_framework.py --if-template` | 21 项通过 | 当前仍在 template；包含任务生成、阶段检查、失败传播、转正与 schema v1 兼容 |
| `python3 scripts/verify.py --profile current` | 通过 | template 阶段的 8 项独立示例测试，不是业务通过 |
| `python3 scripts/doctor.py --strict-manifest` | 通过 | 最终发行清单、配置、任务与链接 |
| `git diff --check` | 通过 | 差异空白检查 |

故障注入、未配置必需检查与非法阶段推进的失败属于回归预期结果。清单在核对预期文件差异后使用 update_manifest.py 更新。

## 限制与交接

仅验证模板及文档兼容性，未执行真实业务/数据库/设备测试、子 Agent 调度或模型行为对照；文本减少不等于已测得 token、耗时或正确率改善。
远程 CI 以本提交对应的 GitHub Actions 记录为准，本地不预先声明其通过。历史验证保留在 Git 历史中。
关联提交：本文件所在的 v1.4.1 更新提交。下一步：接入真实项目后按 [指令维护](docs/instruction-maintenance.md) 观察任务行为，再决定是否增删规则。
