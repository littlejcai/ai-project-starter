# 模板验证记录 · v1.4.0

验证日期：2026-09-14。
起始基线：GitHub main 提交 `adc5cf7f5552943071e1246866c3142d2feb4213`；结果精确提交见 Git 历史。
环境：macOS，Python 3.9.6；CI 配置目标为 Python 3.12，远端结果以提交后的 workflow 为准。

## 变更范围

增加 template、discovery、application、release 生命周期和阶段感知 current 门禁；任务 ID、默认状态与非活动状态改为项目配置；增加项目 doctor、只向前的转正工具与模板清单更新器；CI 在业务阶段自动跳过模板框架回归。
保留 v1.3 的按需读取、风险审查、真实集成和诚实证据边界。阶段配置只表达自动门禁，不替代人工、真机、部署或发布验收，也不预设业务技术栈。

## 实际验证

| 检查 | 结果 | 范围 |
|---|---|---|
| `python3 scripts/doctor.py --strict-manifest` | 通过 | 配置、阶段必需门禁、任务文件、本地链接及模板发行文件/哈希 |
| `python3 scripts/verify.py --profile current` | 通过 | template 阶段只运行 8 项独立示例测试，不代表业务通过 |
| `python3 scripts/test_framework.py` | 21 项通过 | 临时副本中的框架回归，含阶段门禁、必需门禁反例、语义任务 ID、doctor、转正和 schema v1 升级 |
| `git diff --check` | 通过 | 差异空白检查 |

故障注入、缺少阶段必需门禁、生命周期倒退和未配置 quick/full 的失败是回归中的预期结果。任务创建覆盖语义 ID、自定义状态、替换参数、不覆盖已有文件与拒绝路径穿越。
文档和实现由本次主 Agent 自审：核对旧 schema 兼容、阶段边界、业务技术栈中立性、失败传播和模板/业务证据分离；不是独立人员或第二模型审查。

## 限制与下一步

- 未执行模型行为 A/B 对照，不宣称耗时、token 或正确率已经改善；评估方法见 [指令维护](docs/instruction-maintenance.md)。
- 未安装或测试第三方 Skills，未执行真实子 Agent 调度与跨工作区整合。
- 未执行真实业务、数据库、浏览器、小程序真机或 Windows 验证；模板仍未接入业务命令。
- 远程 CI 不在本地验证中预先声明通过，结果以包含本文件的提交所对应 GitHub Actions 记录为准。

关联提交：本文件所在的 v1.4.0 更新提交（精确 SHA 由 Git 历史定位，避免自引用提交号）。
下一步：在更多真实项目中验证默认阶段门禁是否需要调整，并比较转正前后的人工改写、错误状态和上下文开销。
MANIFEST.sha256 只记录 template 发行内容；用 `python3 scripts/update_manifest.py` 更新。项目离开 template 阶段后不再用清单跟踪业务文件。
