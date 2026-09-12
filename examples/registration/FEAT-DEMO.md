# FEAT-DEMO · 活动报名资格判断示例

状态：独立规则示例已实现；真实报名功能未实现。

## 规则与验收

输入假定来自内部已读取的计数，仍执行基本数据校验。
数据合法后，判断顺序为身份、是否重复报名、剩余容量。

| 场景 | 预期 | 对应测试 |
|---|---|---|
| AC001 有名额且登录 | ACCEPT | test_AC001_available_seat |
| AC002 仅余一个名额 | ACCEPT | test_AC002_last_seat |
| AC003 已满 | FULL | test_AC003_full |
| AC004 已报名且已满 | ALREADY_REGISTERED | test_AC004_duplicate_takes_precedence_over_full |
| AC005 未登录 | UNAUTHENTICATED | test_AC005_unauthenticated |
| AC006 容量为零 | FULL | test_AC006_zero_capacity |
| AC007 非法计数 | ValueError | test_AC007_invalid_counts |
| AC008 非布尔标志 | ValueError | test_AC008_invalid_flags |

代码：[registration.py](registration.py)；用例：[test_registration.py](test_registration.py)。

## 运行与缺陷演示

从项目根目录运行 `python3 scripts/verify.py --profile demo`，正常应为 8 个测试通过。
Linux/macOS 可执行下列命令，故意允许满员时报名；应返回非零状态，AC003、AC006 失败。

```bash
DEMO_MUTATION=allow_full python3 scripts/verify.py --profile demo
```

Windows PowerShell：

```powershell
$env:DEMO_MUTATION = 'allow_full'
py -3 scripts/verify.py --profile demo
Remove-Item Env:DEMO_MUTATION
```

这个故障注入证明用例可以捕获一种错误，不是业务代码真实开发历史的红灯证据。

## 实际项目还需要

真实鉴权、资源权限、持久化、唯一约束、事务、并发抢位、接口和界面均未实现。
该纯函数不能阻止两个请求同时抢到最后一席；数据库并发集成测试必须另做。
不要把 ACCEPT 返回值直接当作真实报名成功。

## v1.1：已填写的目标拆解与不变量

真实目标：依据输入快照返回可解释的报名资格决定；本示例不完成报名交易。
事实/约束：函数只接收计数与标志，返回字符串，不连接数据库；依据为 registration.py 的函数实现。
假设：业务层已取得可信的登录信息、是否重复报名与报名计数；这些输入在真实项目中可能过期或不可信。
最小方案：单个纯函数和表驱动的场景测试，不增加数据库、锁或通用报名平台。
优先实验：让满员也返回 ACCEPT，检查规则测试是否拒绝；已有 DEMO_MUTATION 演示为此实验。
判定标准：故障注入时测试退出非零并指出满员边界；正常实现的 8 个测试通过。实际执行结果见 [验证记录](../../TEMPLATE-VALIDATION.md)。

不变量（仅针对合法输入快照与函数返回时刻）：未登录不得 ACCEPT；已报名不得 ACCEPT；满员不得 ACCEPT。
真实系统“不超卖”的不变量应在报名事务提交后的持久化状态验证；它不属于这个纯函数已实现的保证。
风险：纯函数教学示例为低风险；用于真实多人报名时涉及并发，必须按高风险重新建任务。

## v1.1：针对性实现审查示例

方式：本次维护者自审，非独立模型/人员审查。范围：现有函数、8 个规则测试及本例说明；原始实现基于提交 190afee1b94de96432cb31988d86cc6552c58029。
此节示范如何记录证据，不构成真实报名系统已通过验收的声明。

| ID | 类型 | 严重程度 | 位置/规则 | 触发条件与影响 | 证据/验证方法 | 处置与复查 |
|---|---|---|---|---|---|---|
| R-DEMO-01 | 待验证风险 | 若用于真实交易则严重 | registration_decision 的输入计数 | 两个请求持有相同的最后一席快照，均可收到 ACCEPT | 代码按各自快照判断，没有事务；尚未执行真实数据库并发验证 | 明确纯函数范围；真实项目需数据库约束/事务及并发集成测试，未验证前不能宣称交易完成 |
| R-DEMO-02 | 非阻塞建议 | 次要 | 测试输入范围 | 少量手写例子未穷尽合法计数 | 可用参数化或属性测试检验不变量；本次未增加工具 | 业务复杂度增长时再考虑，无需为当前示例提前扩展 |

结论：在已审查的纯函数教学范围内未发现阻塞缺陷；真实鉴权、事务、设备与端到端均未覆盖。
范围、限制与相关测试已明确后结束本次自审，不把扩展建议升级成必做功能。
