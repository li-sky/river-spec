# 修复牌桌中部滑动与抽屉手势冲突

## 元信息

```json
{
  "id": "drawer-gesture-conflicts",
  "status": "done",
  "specs": [
    "table",
    "shared"
  ],
  "risk": "ui",
  "checks": [
    "links",
    "frontend"
  ]
}
```

## 问题与目标

用户反馈页面中部左右滑动没有反应，并担心两个方向互相触发。上一版仅识别屏幕 32px 边缘的 TouchEvent，没有鼠标拖动入口，也用两个独立布尔值保存抽屉状态。

## 预期行为与范围

从房间页非控件区域向右滑打开左菜单、向左滑打开右聊天；触摸与鼠标拖动统一使用 Pointer Events，水平触控板滚动也可触发。抽屉互斥保存，打开后反向滑动只关闭当前抽屉，不自动打开另一侧；同一手势只处理一次。纵向滚动、短划、取消、多指及按钮/输入/滑块操作不切换抽屉。聊天关闭时不打开聊天抽屉；点击、遮罩、Escape 和焦点恢复仍可用。只改前端交互与相关规格，本机更新，不改牌局和服务端协议。

## 验收场景

- [x] AC-01: 390px、320px 的牌桌中部触摸左右滑及桌面鼠标左右拖可打开相应抽屉，边缘仍可触发。
- [x] AC-02: 打开菜单后左滑仅关闭菜单，打开聊天后右滑仅关闭聊天；每次最多一个抽屉，事件冒泡和触控板惯性不触发另一侧。
- [x] AC-03: 纵向滑动、短划、PointerCancel、多指与按钮/输入/滑块不触发；关闭聊天时左滑无效果；点击/Escape 正常。
- [x] AC-04: 前端构建、links 和真实浏览器手势验证通过，更新本机并同步规格与证据。

## 任务

- [x] T-01: 统一抽屉状态、全页方向判定及指针/触控板手势，阻止跨抽屉冒泡和重复触发。
- [x] T-02: 更新浏览器验收，实际验证方向、取消、控件和惯性边界，完成 SDD 与本机更新。

## 审阅结论

审阅通过：牌局动作、WebSocket、筹码及服务端协议不变。抽屉以一个 left/right/null 状态互斥；每次水平指针手势在抬起时消费一次，当前抽屉只接受关闭方向，Portal 内事件阻断冒泡，触控板连续事件消费后抑制惯性。原生触摸的子元素隐式捕获转移不会被误认为取消，取消与多指仍会清理手势。

- AC-01/02：localhost:8092 隔离内存服务上，真实 Chrome 的 CDP Input.dispatchTouchEvent 原生触摸在 390、320px 中部与边缘左右滑均打开正确抽屉；抽屉反方向仅关闭当前侧，错误方向保持当前侧，始终最多一个可见抽屉。1440px 使用 Playwright mouse 原生拖动验证左右打开／关闭。
- AC-03：原生触摸验证短划、纵向滚动、先纵后横轴向锁定、touchCancel、双指，原生 mouse 验证从菜单按钮及聊天输入开始的拖动；均未切换抽屉，纵向触摸实际改变 scrollY。CDP mouseWheel 验证水平打开、惯性反向尾事件不关闭刚打开的抽屉、新手势关闭只当前侧、纵向 wheel 无切换。关闭文字聊天后左滑不打开，右滑仍打开菜单，点击与 Escape 保留。完整真实双人／九人浏览器验收脚本同时通过，新增金额滑块实际鼠标拖动改变数值且未打开抽屉。
- AC-04：前端构建通过；最终提交 HEAD 的 links/frontend 证据见下方。本机 Docker 已重建更新，健康检查及所提供静态 bundle 确认最新版本；原数据库卷保留。

原生浏览器输入通过 Chrome CDP／Playwright 生成，不宣称实体手机或不同操作系统触控板专项通过。持久验收入口 scripts/compact_ui_check.cjs 已从合成 TouchEvent 改用原生输入并覆盖中部与互斥；补充边界检查脚本在源码仓库外 .scratch/drawer-gesture-check.cjs，截图在 .scratch/gesture-review，未提交生成物或会话资料。开发目标达成；本机更新，未推送或发布生产。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T13:03:53.997605Z",
      "codeCommit": "f91654cc41b4d590e7b25e82097a93fd5e3e98b3",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "table": "0b6d8efa113b50a0845cf95987188b5f5153bbb5ef2e29425d620e4ba41ee740",
        "shared": "cf60fa55e5dc19508aa4c6991ece35277cef18af43ee6bf0cd19d66e332204a4"
      },
      "planFingerprint": "4fce8c7b30a0a84af0f7de75a0ba4f79165b6cda31c268606a0442934e7766e5"
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
      "at": "2026-10-01T13:03:54.505742Z",
      "codeCommit": "f91654cc41b4d590e7b25e82097a93fd5e3e98b3",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "table": "0b6d8efa113b50a0845cf95987188b5f5153bbb5ef2e29425d620e4ba41ee740",
        "shared": "cf60fa55e5dc19508aa4c6991ece35277cef18af43ee6bf0cd19d66e332204a4"
      },
      "planFingerprint": "4fce8c7b30a0a84af0f7de75a0ba4f79165b6cda31c268606a0442934e7766e5"
    }
  ],
  "codeCommit": "f91654cc41b4d590e7b25e82097a93fd5e3e98b3",
  "delivery": {
    "status": "not_released",
    "notes": "本机 localhost:8080 已更新；原数据库保留。未推送或发布生产。"
  }
}
```
