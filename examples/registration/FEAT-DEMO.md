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
