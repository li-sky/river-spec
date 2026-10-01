# 手机下注按钮与筹码滑条触觉反馈

## 元信息

```json
{
  "id": "mobile-action-haptics",
  "status": "done",
  "specs": [
    "table",
    "shared"
  ],
  "risk": "media",
  "checks": [
    "links",
    "frontend",
    "media"
  ]
}
```

## 问题与目标

用户要求在手机上为四个下注按钮与加注滑条加入不同的马达节奏：过牌双敲并带短尾，跟注像筹码碰撞，加注比跟注更密，弃牌轻擦，滑条像拨动筹码。继续使用 Duolingo 按钮独立 worktree。

## 预期行为与范围

使用浏览器 Vibration API 与短脉冲间隔模拟节奏；网页不具备振幅、频率或物理阻尼控制。仅在可用 API、触屏能力、可见页面且非减少动态效果模式下触发；不支持或拒绝振动时静默降级，不影响操作。四动作在原有发送保护通过后触发，Raise 打开弹窗与确认加注提供筹码节奏；不因快照或其他玩家行动振动。滑条按合法金额区间分为约 32 档，仅在跨档时触发并限制频率，端点稍明显；数字输入和快捷金额保留行为，快捷金额提供短筹码反馈。离开页面、取消拖动、切后台清理振动；不新增服务端字段或修改规则/声音/语音。当前主要支持 Android Chromium，iPhone Safari 与桌面降级；真实设备听感/触感不由桌面模拟证明。

## 验收场景

- [x] AC-01: 模拟可用振动 API 的手机浏览器，四动作按不同节奏触发；实际双人流程保持正确，禁用、重复发送和非本人动作不触发振动。
- [x] AC-02: 实际滑条交互跨档触发短脉冲，连续事件受限频、不在同档重复，合法端点有额外反馈；取消/隐藏/离开清理，金额与加注请求语义保持不变。
- [x] AC-03: 在无 API、API 返回 false/抛错、桌面指针及减少动态效果模式下，触觉层无错误且操作正常；构建和边界测试通过。记录真实 Android 马达手感尚待用户设备调优，不声称原生力度控制或 iPhone 振动可用。

## 任务

- [x] T-01: 提交计划，实现独立 haptics 模块、限频滑条与动作入口接线。
- [x] T-02: 补充能发现兼容性/限频/生命周期错误的测试，在隔离手机浏览器模拟 API 验证真实双人动作与滑条。
- [x] T-03: 更新长期规格与源码映射，提交代码并执行 links/frontend 检查，保存证据及支持范围。

## 审阅结论

2026-10-01 执行代理差异审阅通过：在同一独立分支实现手机按钮/滑条触觉层；没有修改动作合法性、金额范围、请求保护、服务器、声音或语音实现。haptics 模块与用户事件接线清晰，所有请求都是有限短节奏，无后台循环；媒体脚本仅增加触觉测试并用 Node pathToFileURL 兼容跨平台临时路径。

AC-01：在隔离内存服务 http://localhost:8098 上，Playwright/Chrome 两个 390px 触屏会话使用实际房间服务入座开局，浏览器振动 API 替换为请求记录器。逐一检查 Raise 打开与确认、Call、双方 Check、Fold 的不同模式；服务器动作链真实执行。禁用按钮和另一端快照不产生非零振动。同一行动重复点击两次、模拟 150ms 网络发送延迟，只有一次 action 请求与一次振动，未绕过既有 turnToken 保护。

AC-02：实际鼠标拖动原生 range，在触屏环境记录 3–9 次档位请求、每次总长不超过 32ms，请求间隔至少约 50ms，金额随原生滑条更新到上界附近。键盘调整仍可用；快捷 50% 产生轻筹码节奏，确认加注通过。单元测试覆盖同档、快速跨档抑制、端点、十亿筹码区间及反向拖动、上下界相等/非法值。浏览器 pointercancel、visibilitychange 隐藏和 UI 退出房间均记录 vibrate(0)；正常关闭加注弹窗未截断确认节奏。

AC-03：12 项触觉测试覆盖 API 缺失/返回 false/抛异常、桌面指针、无用户激活、隐藏页面、减少动态效果以及取消后恢复，全部通过。真实双人浏览器中 API 缺失时 Call 仍成功、抛异常时 Check 仍成功、减少动态效果时 Fold 正常且无振动，无浏览器运行时错误。原有 7 项语音测试通过。必需前端/链接/媒体检查按当前代码提交记录在下方；Windows 临时 SDD 适配器仅解析 npm.cmd 与 Git Bash 路径，固定检查 argv 和工具源码不改。

浏览器脚本为工作区 .scratch/mobile-haptics-check.cjs，未提交临时产物。依据 [W3C Vibration API](https://www.w3.org/TR/vibration/) 和 [Chrome 示例](https://googlechrome.github.io/samples/vibration/index.html) 确认时间模式与支持范围；网页没有原生振幅或频率控制，API 成功返回也不证明硬件实际振动。真实 Android 设备的马达力度/双敲/摩擦/筹码触感仍待用户设备调优，iPhone Safari 及桌面只保证正常降级。本次目标按可实现的 Web API 范围完成，不宣称真实手机手感已验收。8098 隔离预览会更新，未合并、推送或更新 8080 服务。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T14:00:48.545919Z",
      "codeCommit": "356cf3f6f6ca1dd2844f5227094d0c7de6721ef1",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "7e007da4f94afcdd2983878e42a772804c64c90faa478e2b21fb438183beae57",
      "specSha256": {
        "table": "7f5871524e9235525fef1915bf2f1b044d1d80734fb5830e8053b3b74b86bec0",
        "shared": "118e6e9644450ee8f731b442886db5e5042aac00770ec8987b77ee069711a4cc"
      },
      "planFingerprint": "da8e60dcbdb584f61f3e40723380ec4baf5c224638ca92e44b0fddb3a4405bbd"
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
      "at": "2026-10-01T14:00:49.106437Z",
      "codeCommit": "356cf3f6f6ca1dd2844f5227094d0c7de6721ef1",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "7e007da4f94afcdd2983878e42a772804c64c90faa478e2b21fb438183beae57",
      "specSha256": {
        "table": "7f5871524e9235525fef1915bf2f1b044d1d80734fb5830e8053b3b74b86bec0",
        "shared": "118e6e9644450ee8f731b442886db5e5042aac00770ec8987b77ee069711a4cc"
      },
      "planFingerprint": "da8e60dcbdb584f61f3e40723380ec4baf5c224638ca92e44b0fddb3a4405bbd"
    },
    {
      "check": "media",
      "commands": [
        {
          "argv": [
            "bash",
            "scripts/test-media.sh"
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\duolingo-buttons\\river-code",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T14:00:54.491406Z",
      "codeCommit": "356cf3f6f6ca1dd2844f5227094d0c7de6721ef1",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "7e007da4f94afcdd2983878e42a772804c64c90faa478e2b21fb438183beae57",
      "specSha256": {
        "table": "7f5871524e9235525fef1915bf2f1b044d1d80734fb5830e8053b3b74b86bec0",
        "shared": "118e6e9644450ee8f731b442886db5e5042aac00770ec8987b77ee069711a4cc"
      },
      "planFingerprint": "da8e60dcbdb584f61f3e40723380ec4baf5c224638ca92e44b0fddb3a4405bbd"
    },
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T14:01:21.405386Z",
      "codeCommit": "356cf3f6f6ca1dd2844f5227094d0c7de6721ef1",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "7e007da4f94afcdd2983878e42a772804c64c90faa478e2b21fb438183beae57",
      "specSha256": {
        "table": "a019e1105f4308b375e2b4e6f53b5986a1c8c59b23ee70572fc74a1419ce8371",
        "shared": "ffdfc40698f378b7353633e31f7e2fd7210f3297bc2f803b0dcb30648933e7a0"
      },
      "planFingerprint": "da8e60dcbdb584f61f3e40723380ec4baf5c224638ca92e44b0fddb3a4405bbd"
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
      "at": "2026-10-01T14:01:21.915714Z",
      "codeCommit": "356cf3f6f6ca1dd2844f5227094d0c7de6721ef1",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "7e007da4f94afcdd2983878e42a772804c64c90faa478e2b21fb438183beae57",
      "specSha256": {
        "table": "a019e1105f4308b375e2b4e6f53b5986a1c8c59b23ee70572fc74a1419ce8371",
        "shared": "ffdfc40698f378b7353633e31f7e2fd7210f3297bc2f803b0dcb30648933e7a0"
      },
      "planFingerprint": "da8e60dcbdb584f61f3e40723380ec4baf5c224638ca92e44b0fddb3a4405bbd"
    },
    {
      "check": "media",
      "commands": [
        {
          "argv": [
            "bash",
            "scripts/test-media.sh"
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\duolingo-buttons\\river-code",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T14:01:26.934553Z",
      "codeCommit": "356cf3f6f6ca1dd2844f5227094d0c7de6721ef1",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "7e007da4f94afcdd2983878e42a772804c64c90faa478e2b21fb438183beae57",
      "specSha256": {
        "table": "a019e1105f4308b375e2b4e6f53b5986a1c8c59b23ee70572fc74a1419ce8371",
        "shared": "ffdfc40698f378b7353633e31f7e2fd7210f3297bc2f803b0dcb30648933e7a0"
      },
      "planFingerprint": "da8e60dcbdb584f61f3e40723380ec4baf5c224638ca92e44b0fddb3a4405bbd"
    }
  ],
  "codeCommit": "356cf3f6f6ca1dd2844f5227094d0c7de6721ef1",
  "delivery": {
    "status": "not_released",
    "notes": ""
  }
}
```
