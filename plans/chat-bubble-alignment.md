# 修正聊天气泡、头像与按需时间

## 元信息

```json
{
  "id": "chat-bubble-alignment",
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

用户截图反馈气泡形状异常，气泡三角未对准头像；自己的消息无需显示“我”，发送时间应只在触摸单击或鼠标悬浮时在气泡另一侧快速渐入。用户要求修正后 push。

## 预期行为与范围

保留 Chatscope 的消息、头像与纯文本组件以及 Radix 右键/长按菜单。修正主题覆盖优先级、圆角、三角和头像定位；三角在头像侧对准头像中心，昵称仅在其他成员消息上方显示且不影响三角定位。原发送时间在远离头像的一侧显示，本人左侧、他人右侧；默认隐藏，鼠标悬浮气泡或键盘聚焦时以约 120ms 渐入，触摸短按切换、点其他区域或滚动隐藏；长按、滑动、取消和多指不误触时间切换。时间绝对定位，出现不引起消息位移；窄屏长文本仍换行。保留置顶、复制与撤回行为，不修改协议与服务端。按用户要求推送两仓，发布结果单独记录。

## 验收场景

- [x] AC-01: 真实浏览器检查左右短/长消息、头像、三角、圆角；自己的消息无昵称，其他成员仍显示昵称；320/390px 无消息横向溢出。
- [x] AC-02: 鼠标悬浮时仅当前气泡时间在另一侧渐入，离开隐藏；触摸短按切换时间，点其他区域/滚动隐藏；时间显示不改变气泡尺寸和位置。
- [x] AC-03: 右键/键盘与触摸长按菜单仍打开；触摸滑动、长按、取消、多指不误触时间切换；前端构建与链接检查通过。

## 任务

- [x] T-01: root 修正 ChatBubble、ChatMessages 与样式，保留成熟组件和现有消息操作。
- [x] T-02: root 实际浏览器验收，同步长期规格，提交代码并完成 SDD 检查和结果记录；推送属于后续交付动作。

## 审阅结论

目标达成。代码基线 `570cdf039a8e029e72ab3662e4001751ad7a1ca8`，开工计划固定为规格提交 `647dec098fa693e866527eaaae1e172c3cd2c901`。差异审阅确认继续复用 Chatscope 与 Radix，变更仅涉及三个聊天前端文件。修正库样式更高优先级导致的缺角圆角、头像 min-height=42px 和头部位移；头像最终 34px，三角使用明确尺寸的 clip-path，左右三角中心与头像中心实际测量一致。自己的消息没有 chat-sender-name，其他成员昵称保留且长昵称截断。

AC-01/02：在本地 Vite 页加载真实 ChatMessages/ChatBubble 和生产 CSS 的临时样本，使用 Codex in-app Chromium 实际查看短消息、多行正文、长无空格字符串、纯文本 HTML 与置顶标签。面板宽度 320/390px 及桌面 1440px 下的 420px 面板，消息行均无横向溢出，四角计算样式均为 9px。头像高度均为 34px，左右三角与头像中心坐标完全一致。桌面指针落在本人气泡时仅本人时间 opacity=1，其他为 0；他人气泡的时间位于右侧，本人为左侧，过渡计算样式为 0.12s。出现/收起前后的本人短气泡矩形保持 x=179、y=287.265625、width=84、height=44（320px 样本）。点击输入区后隐藏。截图保存在根工作区 `.scratch/chat-bubble-alignment/390px.png`，不提交生成物。

AC-02/03 的触摸条件：临时样本通过真实组件 DOM 派发 touch 类型 PointerEvent，在浏览器中实际观察处理结果；80ms 短按显示，再次短按隐藏，滚动隐藏，移动 45px、pointercancel、多指和 850ms 长按均不切换时间。长按使用 Radix 原有 700ms 触发菜单并在松手后保留。桌面实际右键与 Shift+F10 打开消息菜单，复制结果读取为“那我问你”，置顶标签移动到本人消息，撤回显示提示。写操作回归采用样本 send 回调，不宣称重测服务端权限或跨会话同步。本次没有物理手机／iOS Safari 验收；浏览器视口临时覆盖已恢复，临时测试入口已移出代码仓库。

最终 HEAD 的前端构建及 links 结果见验证记录。初次 SDD frontend 由于 Windows subprocess 无法直接解析 npm 而未执行；沿用工作区现有 run-sdd-windows.py，仅将 npm 解析为 D:/npm.CMD，重跑相同检查，不修改 SDD 源码。Vite 的既有 EmojiPicker 大块提示仍存在，不影响构建。用户已授权 push，完成后记录推送结果，发布状态独立于开发完成。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T15:31:23.454331Z",
      "codeCommit": "570cdf039a8e029e72ab3662e4001751ad7a1ca8",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "013f3b18c676758251819fe3df99fb7cbd20a50c3a3dbff60870713ead1dded0",
      "specSha256": {
        "table": "7f04ae0c3d561ff9f551b431dccbe7e2c6a8c74470f2827609fc74f4893563f3",
        "shared": "0863884180d637317985386d54a8a22e35183a448499b6eeb48979267b91b9c1"
      },
      "planFingerprint": "bbbe69c31e2e871a5b0ce9eeece725fc9295c9163cb848928058c773395bb7aa"
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
          "exitCode": 127
        }
      ],
      "exitCode": 127,
      "at": "2026-10-01T15:31:24.070963Z",
      "codeCommit": "570cdf039a8e029e72ab3662e4001751ad7a1ca8",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "013f3b18c676758251819fe3df99fb7cbd20a50c3a3dbff60870713ead1dded0",
      "specSha256": {
        "table": "7f04ae0c3d561ff9f551b431dccbe7e2c6a8c74470f2827609fc74f4893563f3",
        "shared": "0863884180d637317985386d54a8a22e35183a448499b6eeb48979267b91b9c1"
      },
      "planFingerprint": "bbbe69c31e2e871a5b0ce9eeece725fc9295c9163cb848928058c773395bb7aa"
    },
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T15:32:15.817493Z",
      "codeCommit": "570cdf039a8e029e72ab3662e4001751ad7a1ca8",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "013f3b18c676758251819fe3df99fb7cbd20a50c3a3dbff60870713ead1dded0",
      "specSha256": {
        "table": "7f04ae0c3d561ff9f551b431dccbe7e2c6a8c74470f2827609fc74f4893563f3",
        "shared": "0863884180d637317985386d54a8a22e35183a448499b6eeb48979267b91b9c1"
      },
      "planFingerprint": "cf5cf500977b59c3483372b63fd4954195b0243e8a1b0659e53253f886499efc"
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
      "at": "2026-10-01T15:32:16.526982Z",
      "codeCommit": "570cdf039a8e029e72ab3662e4001751ad7a1ca8",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "013f3b18c676758251819fe3df99fb7cbd20a50c3a3dbff60870713ead1dded0",
      "specSha256": {
        "table": "7f04ae0c3d561ff9f551b431dccbe7e2c6a8c74470f2827609fc74f4893563f3",
        "shared": "0863884180d637317985386d54a8a22e35183a448499b6eeb48979267b91b9c1"
      },
      "planFingerprint": "cf5cf500977b59c3483372b63fd4954195b0243e8a1b0659e53253f886499efc"
    }
  ],
  "codeCommit": "570cdf039a8e029e72ab3662e4001751ad7a1ca8",
  "delivery": {
    "status": "pushed",
    "notes": "2026-10-01 已将代码 570cdf039a8e029e72ab3662e4001751ad7a1ca8 与完成规格 8f849a5 推送至各自 origin/main。CI/CD 发布结果尚未确认，pushed 不代表已上线。"
  }
}
```
