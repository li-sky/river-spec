# 分离移动牌桌座位与公共牌区域

## 元信息

```json
{
  "id": "spacious-mobile-table",
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

手机 8 人桌仍使用椭圆座位坐标，右下角相邻玩家、摊牌和公共牌结算文字重叠。将手机座位改成独立分行布局，保留中央公共牌区域并精简重复信息。

## 预期行为与范围

600px 以下的 2–9 人桌按上、两侧、下方分行布局，座位内容与中央底池、五张公共牌、结算文字分离。按用户补充要求，手机公共牌上排三张、下排两张居中，缩窄中央牌区。空座只显示加号与简短编号；自己的牌型保留在操作底栏，手机座位不重复显示。摊牌仍只使用服务端已公开底牌，座位顺序、入座、互动和固定底栏行为不变。桌面布局与后端规则不变。

## 验收场景

- [x] AC-01: 320/390px 的 6/8/9 人桌满桌摊牌时，公共牌按 3+2 居中分两行，公共牌及结算与玩家头像、名字、筹码、公开底牌、牌型互不重叠，内容无横向溢出。
- [x] AC-02: 2–9 人桌座位顺序一致，自己的座位在下方中央；空座简短编号仍可点击入座，头像互动按钮至少 48px。
- [x] AC-03: 桌面牌桌、真实发牌和行动、左右抽屉及固定四按钮底栏通过回归验证；手机自己的牌型仍可在底栏查看。

## 任务

- [x] T-01: 实现手机分行座位、独立中央牌区和精简标签。
- [x] T-02: 用真实本地服务完成手机布局和现有交互回归，查看截图并记录证据。
- [x] T-03: 同步牌桌规格、审阅差异、完成必需检查及本地预览更新。

## 审阅结论

差异审阅通过：手机 2–9 人座位顺序保持一致，分行布局将公共牌与座位内容分离；公共牌按用户补充要求改成 3+2，两张下排居中。手机本人牌型集中在底栏，空座编号、公开摊牌和结束手牌状态精简。头像、倒计时、Emoji、皇冠与庄家角标均保留可读交互。桌面继续使用椭圆座位，服务器规则与私牌边界未改。

实际验收：隔离本机内存服务、Chromium Chrome 真实会话执行 scripts/mobile_table_check.cjs，2–9 人桌检查空座入座与本人下方位置；6/8/9 人桌完成真实全下至五张公共牌摊牌，320/390/600px 检查玩家所有内容及角标不与邻座或中央区域相交、3+2 排列和居中、48px 头像、无横向溢出，以及滚动后本人筹码不被底栏遮挡。另从第二名玩家视角核查旋转。包含真实头像 Emoji、长名字；长多赢家结算文本为局部合成，仅用于有界区域检查，不作为真实分池证据。

现有 scripts/compact_ui_check.cjs 最终版本回归通过，覆盖 1440/768/390/320px 顶栏、固定四动作底栏、聊天与菜单互斥手势、焦点、暂离、金额输入／滑块／预设、跟注／过牌／弃牌／普通与短全下、过期动作及九人座位。查看 .scratch/spacious-table-review 的两人入座与6/8/9人摊牌截图，确认公共牌3+2、筹码与结果可读。认证限流曾阻止并行运行测试，改为隔离服务逐次运行后通过。公网语音、真实移动设备与系统屏幕阅读器本次未重新验收。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T13:24:27.375786Z",
      "codeCommit": "be24d7fad3fcb16a7d483c5900cc60a75dff4c9a",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "table": "8eb989df6a49a2ed9bf75f418926c0ce30e24d4ffcbf9de824052217ee26cc62"
      },
      "planFingerprint": "782a5d60be8ed9beacd07a92a205a41a25818ea3083a5661879c71fc84b3ddde"
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
      "at": "2026-10-01T13:24:27.906219Z",
      "codeCommit": "be24d7fad3fcb16a7d483c5900cc60a75dff4c9a",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "table": "8eb989df6a49a2ed9bf75f418926c0ce30e24d4ffcbf9de824052217ee26cc62"
      },
      "planFingerprint": "782a5d60be8ed9beacd07a92a205a41a25818ea3083a5661879c71fc84b3ddde"
    }
  ],
  "codeCommit": "be24d7fad3fcb16a7d483c5900cc60a75dff4c9a",
  "delivery": {
    "status": "not_released",
    "notes": "已构建并更新本机 Docker app 预览 http://localhost:8080，保留原 PostgreSQL 数据库；healthz 200，HTML 指向当前 index-CQbQOIsm.js / index-COVckJzu.css。未发布公网。"
  }
}
```
