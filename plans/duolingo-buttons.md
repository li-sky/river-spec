# 主要交互按钮采用 Duolingo 风格

## 元信息

```json
{
  "id": "duolingo-buttons",
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

用户要求在独立 worktree 中将大部分重要交互按钮改成 Duolingo 风格。现有按钮以平面深色或金色为主，按压反馈不统一；本次目标是形成圆润、厚底边、清楚下压的游戏按钮系统。

## 预期行为与范围

覆盖入口登录/注册/访客、GitHub 链接、大厅创建与房间卡片、入座、开局、Call/Raise/Check/Fold、加注快捷金额、设置保存、常用图标、抽屉菜单、语音及聊天发送。主操作采用鲜绿色，Raise 保留金色，Call 使用蓝色，Check 使用绿色，Fold 使用珊瑚红；深色次级按钮保留界面层级。统一圆角、实色底边、加粗文字、悬停和向下按压反馈，禁用按钮不可按压，键盘焦点清晰，减少动态效果偏好继续有效。仅修改样式及动作按钮颜色类，不修改接口、权限、动作条件、按钮文案或牌局规则；不合入主线、不更新现有运行服务。

## 验收场景

- [x] AC-01: 在桌面及 390px、320px 手机查看入口、大厅、创建/设置弹窗及牌桌，主要按钮具备统一圆角和立体底边，无横向溢出，保留至少 44px/48px 的原有触控区域。
- [x] AC-02: 实际悬停、按下、松开按钮，底边随按压收起并恢复；禁用按钮不会位移或触发动作，键盘焦点和减少动态效果模式仍可辨识。
- [x] AC-03: 两个隔离会话通过入座、开局、Raise 快捷金额与确认、跟注/过牌/弃牌及聊天发送验证流程，现有合法动作及等待禁用条件保持有效。

## 任务

- [x] T-01: 在独立代码/规格 worktree 提交开工计划，实现共享按钮样式和明确的四动作颜色。
- [x] T-02: 对隔离预览进行浏览器验收与截图审阅，运行前端构建和双仓链接检查。
- [x] T-03: 同步四份长期页面规格、提交代码并记录当前提交的验证证据及未发布状态。

## 审阅结论

2026-10-01 执行代理差异审阅通过，目标已达成。代码仅修改 style.css 与 App.tsx 中 Call、Raise 及加注确认的样式类；四动作的条件、请求保护、接口、权限、媒体逻辑和规则保持原有实现。共享样式覆盖主要操作、常用图标、模式切换、房间卡片、菜单、语音及聊天发送；次级文字操作与完整 Emoji 内部控件保留既有层级。修正桌面空座按钮编号后缀的定位，使其与编号同行。

AC-01：本机隔离内存服务 http://localhost:8098 使用此次前端构建及现有 river-wins-preview 后端，独立于 8080 服务及真实数据库。Playwright/Chrome 在 1440、390、320px 检查入口、大厅、房间卡片、创建弹窗；牌桌另检查 768px，个人设置/菜单/加注/聊天在手机检查。所有页面无横向溢出，主按钮至少 48px，顶栏保持原有 44px。截图实际审阅通过，未将动画中间帧用于最终结论。

AC-02：实际鼠标悬停、按下、移出并松开验证抬起/下压/恢复与底边收起；禁用四动作在按下时 transform 保持 none。Tab 键进入模式按钮验证 focus-visible 实线描边；模拟 reducedMotion=reduce 验证 transition-duration 为 0.01ms。还检查圆形空座、12px 图标圆角、20px 房间卡片圆角与各动作背景色。

AC-03：两个真实独立浏览器会话通过 UI 访客进入/创建/坐下/开局，Raise 选择 50% 快捷金额并确认，另一端 Call，双方 Check 后 Fold，个人设置保存及聊天发送均成功；等待阶段四动作均禁用，无浏览器运行时错误。没有改动等待保护逻辑，本次没有重复执行历史延迟响应专项验收。

浏览器脚本与截图保存于工作区 .scratch/duolingo-buttons-check.cjs 和 .scratch/duolingo-buttons-review/，属于本次一次性验收产物，未提交生成文件。前端构建通过，既有 Emoji 分块大小提示仍存在。本次未验证真实 GitHub OAuth、麦克风/公网 TURN；不扩大为身份或媒体能力的新验收。SDD 在 Windows 通过临时适配器仅将 npm 解析为 npm.cmd，规格工具及固定检查命令不修改。保留独立分支，未合并、推送或更新 8080 服务。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T13:50:55.904379Z",
      "codeCommit": "dd28cdb7afc49626006b075655ef6028cbe28ff6",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "entry": "22ee86f1db4735241b62f7162cf4cd77aeb674fb2585082acda9d2652f2b8878",
        "lobby": "7d8df62a4042282f9e8f6d74b60bbd5607ccec04db5258794b5fdb944a145234",
        "table": "39edb82ea0263b6cbc752d10b96809e6bd633e5e451ccdfa62766be84ff65c27",
        "shared": "95546e30df2e707a52404cafada0d6b7dbf78020d490bb9849dad7c990341244"
      },
      "planFingerprint": "509bc30864957e1a05dd980bd69154443bf15893754a3f622c99d3d531a1109f"
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
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\duolingo-buttons\\river-code\\frontend",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T13:50:56.698980Z",
      "codeCommit": "dd28cdb7afc49626006b075655ef6028cbe28ff6",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "entry": "22ee86f1db4735241b62f7162cf4cd77aeb674fb2585082acda9d2652f2b8878",
        "lobby": "7d8df62a4042282f9e8f6d74b60bbd5607ccec04db5258794b5fdb944a145234",
        "table": "39edb82ea0263b6cbc752d10b96809e6bd633e5e451ccdfa62766be84ff65c27",
        "shared": "95546e30df2e707a52404cafada0d6b7dbf78020d490bb9849dad7c990341244"
      },
      "planFingerprint": "509bc30864957e1a05dd980bd69154443bf15893754a3f622c99d3d531a1109f"
    }
  ],
  "codeCommit": "dd28cdb7afc49626006b075655ef6028cbe28ff6",
  "delivery": {
    "status": "not_released",
    "notes": ""
  }
}
```
