# 优化游戏界面的可读性与多端操作

## 元信息

```json
{
  "id": "game-ui-readability",
  "status": "done",
  "specs": [
    "entry",
    "lobby",
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

用户要求按 game-ui-design skill 优化现有 UI。当前入口、大厅、牌桌及弹窗大量文字为 6–13px，辅助按钮和下注快捷按钮小于 44px；行动者主要依赖颜色与闪动，底池、底牌和金额调整的层级较弱。目标是保持 RIVER 的深色绿毡与金色品牌，在真实多人牌局中提高读数、行动反馈和多端操作的清晰度。

## 预期行为与范围

参考用户提供的 SKILL.md 及 patterns.md、sharp_edges.md、validations.md：关键读数突出，次要文字至少 14px，表单正文 16px，主要触控目标至少 48px，键盘焦点清楚；行动状态兼用文字、边框和倒计时进度，下注后显示服务器响应等待。手机底牌和下注按钮稳定排列，加注总额明确标注；弹窗与操作区考虑 safe-area，减少动态效果时保留静态互动反馈。入口、大厅、牌桌及共享控件采用一致排版与间距。游戏手柄不在当前浏览器产品支持范围；不增加手柄输入或快捷下注，不改规则、权限、接口、结算、媒体连接或登录方式。本次仅本地开发与验证，不发布生产环境。

## 验收场景

- [x] AC-01: 入口、大厅和创建/个人设置弹窗在桌面与 390px、320px 手机宽度无横向溢出，文字清楚，交互目标至少 48px，Tab 焦点可见。
- [x] AC-02: 九人牌桌在桌面、平板和手机上头像触控区域互不相交、公共牌与自身底牌可读；手机操作区不覆盖牌桌内容。
- [x] AC-03: 真实两人牌局中当前行动者显示行动文字及秒数；本人行动区显示倒计时进度、可跟金额、加注总额；点击合法动作后出现提交反馈并随服务器状态更新。
- [x] AC-04: 开关、滑块、聊天与弹窗保持键盘可操作；减少动态效果样式取消持续闪烁且保留定向 Emoji 的静态目标反馈。
- [x] AC-05: 前端构建及 SDD links 检查通过，相关长期规格同步；代码差异只涉及 UI 展示与本地提交反馈。

## 任务

- [x] T-01: 统一字体、对比度、按钮尺寸、间距及桌面/移动布局，清理互相覆盖的小字样式。
- [x] T-02: 增加行动者文字、倒计时进度、金额语义与发送反馈，完善控件名称和焦点。
- [x] T-03: 通过真实服务及浏览器核查关键场景，记录证据，同步四份页面规格并执行 SDD 收尾。

## 审阅结论

已按用户指定的 [game-ui-design skill](https://github.com/omer-metin/skills-for-antigravity/blob/main/skills/game-ui-design/SKILL.md) 完成 UI 优化。差异审阅确认仅涉及 App 展示/本地等待状态、样式和已有 ALL IN 浏览器定位器；未修改服务端规则、权限、持久化、信令或登录协议。普通加注增加整数输入保护，服务端仍为权威校验方。

- AC-01：入口、大厅、创建和个人设置检查桌面、390px 与 320px；无横向溢出，操作区域达到 48px。实际创建并入座成功；个人设置 Tab 到下一字段，焦点描边为 2px，Space 切换音效，Escape 关闭并回到大厅。
- AC-02：真实九会话入座并经过翻牌、转牌、河牌及公开摊牌；1440、1024、768、601、390、320px 的 DOM 几何检查均无头像相交、公共牌与头像/手牌相交、卡牌与筹码/名称标签相交、卡牌横向裁切及页面横向溢出。可见按钮与输入至少 48px。手机与平板本人两张底牌放入操作区（44×66px），宽桌面保留座位旁底牌；手机操作区为正常文档流。最终截图目视核查了点数、花色和金额；九人手机桌增高以保留这些间距。
- AC-03：隔离两人牌局在本机 1500ms 响应延迟代理下点击跟注，四个行动按钮及加注控件全部禁用，`aria-busy=true` 与“已发送，等待牌桌更新…”可见；服务端进入下一阶段后等待状态清除、控件恢复。正常加注由服务端推进；超出上限和小数金额时普通加注按钮禁用。当前行动者、剩余秒数、进度和本轮加注总额均可读。等待状态不添加自动重发协议。
- AC-04：滑块 ArrowRight 增加 1；聊天 Enter 发送后出现真实服务器消息与气泡；开关和弹窗键盘操作通过。减少动态效果 CSS 已审阅：一般动画缩短、持续闪烁移除、定向 Emoji 静态变换到目标并保留不透明度。未声称运行了操作系统偏好切换、屏幕阅读器或移动软键盘专项验收。
- AC-05：四份长期规格已同步到代码基线；构建与 links 的最终 SDD 记录见下方。未把未运行的旧 browser_check.py、语音/后端/OAuth 场景登记为通过。本次 UI 风险按项目最低要求运行 links 与 frontend。

验收环境为本机隔离预览 http://localhost:8081，现有 8080 容器保持运行；本机截图存于工作区外的 `.scratch/ui-review`，未提交生成物或任何会话凭据。Windows 上 SDD 的固定 frontend profile 使用既有 `npm run build` 参数，执行时仅将 npm 名称解析到 PATH 上的 npm.cmd，以适配 Python CreateProcess；未更改固定 profile、门禁或仓库工具源码。结论：本次开发与 UI 验收目标达成，生产发布独立且尚未执行。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T11:44:26.293021Z",
      "codeCommit": "3fb51017e9594191d01d1e372a663c457217a25c",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "b4d5772649036f685f3f70c7a1bf2789d50dfd47af67f06a952a39a810d8def6",
      "specSha256": {
        "entry": "38f1f1ceec49b60238d37299e933bc64206d40822e35395ad4147430d3887ce8",
        "lobby": "6a41f0b468efa8c69ca0ec06cd080ae7a7719884074c2b0576d0d1be09206a35",
        "table": "d8ea1898988c3294a2bda217bf3312202155161fd2c0f257a3b238a6fbf15fb3",
        "shared": "54094571a62ee9b905441a2125315875932fe8864f5b0077526a1c4a05bc883a"
      },
      "planFingerprint": "54f1e5495c1e03aea09a41194f7603139246039bc962927880ae4011e330d702"
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
      "at": "2026-10-01T11:44:26.824618Z",
      "codeCommit": "3fb51017e9594191d01d1e372a663c457217a25c",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "b4d5772649036f685f3f70c7a1bf2789d50dfd47af67f06a952a39a810d8def6",
      "specSha256": {
        "entry": "38f1f1ceec49b60238d37299e933bc64206d40822e35395ad4147430d3887ce8",
        "lobby": "6a41f0b468efa8c69ca0ec06cd080ae7a7719884074c2b0576d0d1be09206a35",
        "table": "d8ea1898988c3294a2bda217bf3312202155161fd2c0f257a3b238a6fbf15fb3",
        "shared": "54094571a62ee9b905441a2125315875932fe8864f5b0077526a1c4a05bc883a"
      },
      "planFingerprint": "54f1e5495c1e03aea09a41194f7603139246039bc962927880ae4011e330d702"
    }
  ],
  "codeCommit": "3fb51017e9594191d01d1e372a663c457217a25c",
  "delivery": {
    "status": "not_released",
    "notes": "仅本机隔离预览 localhost:8081；未发布生产环境。"
  }
}
```
