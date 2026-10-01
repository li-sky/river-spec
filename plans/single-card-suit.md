# 每张牌面只显示一个花色

## 元信息

```json
{
  "id": "single-card-suit",
  "status": "done",
  "specs": [
    "table"
  ],
  "risk": "ui",
  "checks": [
    "links",
    "frontend"
  ]
}
```

## 问题与目标

用户确认每张牌面只需一个花色。当前共享 Card 组件绘制三处花色，再按不同屏幕尺寸隐藏其中一部分，牌面存在重复标记。

## 预期行为与范围

共享 Card 的明牌统一只绘制一个点数和一个花色；适用于入口装饰、大厅缩略牌、公共牌、底牌与摊牌。保留红黑颜色和完整可读名称，手机紧凑摊牌横排展示点数与唯一花色。仅修改牌面结构和相关样式，不改变牌背、规则、接口或结算。清理不再使用的角标花色和底部角标样式。

## 验收场景

- [x] AC-01: 每张明牌只有一个花色标记，点数、颜色和可读名称正确，牌背及空位保持原有显示。
- [x] AC-02: 桌面和 390px、320px 手机的普通牌、小牌、底牌与紧凑摊牌样式清楚可读，唯一花色不被隐藏。
- [x] AC-03: 前端构建和双仓链接通过，长期牌桌规格及本次证据同步。

## 任务

- [x] T-01: 修改共享 Card 和相关样式，检查全部使用位置及响应式覆盖。
- [x] T-02: 观察桌面/手机渲染并核查唯一花色，同步规格、提交代码、执行 SDD 检查并完成计划。

## 审阅结论

目标达成，代码提交 f177020d21477b8253506b1a7a4cdaeb8787387d。共享 Card 删除两个角落花色与底部角标，只保留点数和一个 card-suit；清理废弃 CSS。手机紧凑摊牌保留唯一花色并横排对齐，使用与原小牌偏移同等优先级的选择器清除 margin，避免花色错位。差异审阅确认牌背、空位、红黑颜色和 aria-label 保留，服务端及接口没有改动。

从实际 App.tsx 提取共享 Card，用真实 React、lucide 与完整产品 CSS 在隔离浏览器样例中渲染四花色、A/10/J/Q/K、普通牌、小牌、底牌、紧凑摊牌以及牌背/空位。在 1440px、390px、320px 均核查每张可见明牌只有一个可见花色；执行代理查看桌面与 320px 截图，确认普通牌和紧凑摊牌的点数与花色清楚，修正一次小牌样式覆盖后重验通过。样例仅调整展示容器的位置与层级，没有覆盖牌面规则。截图保存 .scratch/single-card-1440.png、single-card-390.png、single-card-320.png，不提交生成物。此次是局部牌面渲染验收，没有声称重跑完整多人牌局、媒体或数据库场景；无需为样式变化新增产品测试。固定提交的前端构建及 links 证据见下方。规格同步，未推送或部署。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T11:53:00.106164Z",
      "codeCommit": "f177020d21477b8253506b1a7a4cdaeb8787387d",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "table": "e5f77c4064a60622396dcd9ae7f4265387d454da897e08f709bd92c2f57c7766"
      },
      "planFingerprint": "9cb9683bee0c8edaaaf5512401ccabf2ff4c936260647f3cd2ca1910857507f9"
    },
    {
      "check": "frontend",
      "commands": [
        {
          "argv": [
            "npm",
            "run",
            "build"
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\river-code\\frontend",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T11:53:00.631903Z",
      "codeCommit": "f177020d21477b8253506b1a7a4cdaeb8787387d",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "table": "e5f77c4064a60622396dcd9ae7f4265387d454da897e08f709bd92c2f57c7766"
      },
      "planFingerprint": "9cb9683bee0c8edaaaf5512401ccabf2ff4c936260647f3cd2ca1910857507f9"
    }
  ],
  "codeCommit": "f177020d21477b8253506b1a7a4cdaeb8787387d",
  "delivery": {
    "status": "not_released",
    "notes": ""
  }
}
```
