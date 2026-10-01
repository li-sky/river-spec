# 显示当前可见手牌的最佳牌型

## 元信息

```json
{
  "id": "current-hand-rank",
  "status": "done",
  "specs": [
    "poker",
    "table"
  ],
  "risk": "service",
  "checks": [
    "links",
    "backend",
    "frontend"
  ]
}
```

## 问题与目标

用户要求根据当前公开牌面自动计算玩家手牌组合结果，在玩家旁边显示，并使用 worktree 避开并行修改。当前仅结算后显示赢家牌型，进行中缺少本人当前最佳牌型提示。

## 预期行为与范围

服务端沿用 Evaluate，以观看者可见的两张底牌和已经发出的 3～5 张公共牌计算最佳五张的中文牌型。HandPlayer 新增可选 currentHand 字符串；翻牌前、隐藏底牌、已弃牌或无有效组合时省略。自己从翻牌开始可见，未弃牌对手只在摊牌公开后可见，旁观者不获得未公开的牌型。每次快照重新计算，不使用牌堆或未来公共牌，不改变胜负和结算。座位筹码下方显示“当前：牌型”；手机底牌区同步显示。换手和弃牌自动清除，不增加胜率、听牌预测或翻牌前两张牌的特殊评估。代码和规格各用独立 worktree，本次本地提交，不合并并行工作或部署。

## 验收场景

- [x] AC-01: 固定合成牌局从翻牌前推进至翻牌、转牌和河牌，本人提示依次为空、一对、三条和葫芦；仅使用已发出的公共牌。
- [x] AC-02: 两名玩家及旁观者视图和 JSON 中无隐藏对手 currentHand；改变隐藏底牌不改变另一观看者的投影；摊牌后公开未弃牌牌型，弃牌及弃牌获胜不公开对手牌型。
- [x] AC-03: 最佳组合可完全取自五张公共牌；A2345 顺子正确；下一手翻牌前及弃牌后清除提示，非法输入省略提示。
- [x] AC-04: 浏览器核查桌面和手机显示、公共牌变化时更新、摊牌公开及新手清除；座位旁提示与手机底牌区结果一致。
- [x] AC-05: 后端测试、vet、前端构建及 SDD links 通过，相关契约和长期规格同步，原工作区并行改动保留。

## 任务

- [x] T-01: 在服务端个性化 HandView 中计算 currentHand，增加阶段和私牌隔离回归验证。
- [x] T-02: 更新 TypeScript 契约、座位与手机底牌显示及独立样式。
- [x] T-03: 审阅差异，进行浏览器验收，同步规格和验证证据，提交代码并完成 SDD 门禁。

## 审阅结论

差异已审阅，目标达成。后端 current_hand_test.go 通过实际行动验证翻牌前→翻牌→转牌→河牌及摊牌，双玩家/旁观者 JSON 无隐藏牌型，隐藏底牌变更不影响他人视图；公共牌最佳五张、A2345、无效输入和投影不修改状态均通过。独立内存服务 127.0.0.1:8093 的真实双人 HTTP/WebSocket 浏览器验收观察到本人提示、各街同步、摊牌公开对手；下一手和弃牌后 DOM 牌型标签数量均为 0。1440×1000 桌面、390×844 和 320×740 手机已观察，字号 14px、手机/座位一致且无横向溢出；320px 短屏原有 sticky 操作区在页面未滚动到下方时仍可能覆盖牌桌底部，滚动后标签底边位于操作区上边之上，手机底牌区同步显示始终可见。本次只为新增标签预留 28px 间距，不改造并行任务负责的整体布局。截图保存在同一隔离目录 tools/current-hand-desktop.jpg 和 tools/current-hand-mobile.jpg，不提交实际牌面。原工作区 App.tsx、style.css、browser_check.py 并行改动保留；本次未合并、未部署。最终固定检查由以下真实 SDD run 记录保存。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T11:33:48.412830Z",
      "codeCommit": "8a2be43d24690b0884749d483d50c9f63a36697e",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "b4d5772649036f685f3f70c7a1bf2789d50dfd47af67f06a952a39a810d8def6",
      "specSha256": {
        "poker": "715b97dc171c5739d8142aabefb62c8571a03306f98d01876e65397eda3953e1",
        "table": "00cd185675dc6a7f58d3e9197cd8cd45524e1a1725d1447f7834754bf0da9b08"
      },
      "planFingerprint": "5e80891aeaab00ac44cf15e29c517f74578ad3ba276a1bfc82a168727d566efc"
    },
    {
      "check": "backend",
      "commands": [
        {
          "argv": [
            "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\current-hand-rank\\tools\\go\\bin\\go.exe",
            "version"
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\current-hand-rank\\river-code\\backend",
          "exitCode": 0
        },
        {
          "argv": [
            "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\current-hand-rank\\tools\\go\\bin\\go.exe",
            "test",
            "./..."
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\current-hand-rank\\river-code\\backend",
          "exitCode": 0
        },
        {
          "argv": [
            "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\current-hand-rank\\tools\\go\\bin\\go.exe",
            "vet",
            "./..."
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\current-hand-rank\\river-code\\backend",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T11:33:49.045796Z",
      "codeCommit": "8a2be43d24690b0884749d483d50c9f63a36697e",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "b4d5772649036f685f3f70c7a1bf2789d50dfd47af67f06a952a39a810d8def6",
      "specSha256": {
        "poker": "715b97dc171c5739d8142aabefb62c8571a03306f98d01876e65397eda3953e1",
        "table": "00cd185675dc6a7f58d3e9197cd8cd45524e1a1725d1447f7834754bf0da9b08"
      },
      "planFingerprint": "5e80891aeaab00ac44cf15e29c517f74578ad3ba276a1bfc82a168727d566efc"
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
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\current-hand-rank\\river-code\\frontend",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T11:33:51.165724Z",
      "codeCommit": "8a2be43d24690b0884749d483d50c9f63a36697e",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "b4d5772649036f685f3f70c7a1bf2789d50dfd47af67f06a952a39a810d8def6",
      "specSha256": {
        "poker": "715b97dc171c5739d8142aabefb62c8571a03306f98d01876e65397eda3953e1",
        "table": "00cd185675dc6a7f58d3e9197cd8cd45524e1a1725d1447f7834754bf0da9b08"
      },
      "planFingerprint": "5e80891aeaab00ac44cf15e29c517f74578ad3ba276a1bfc82a168727d566efc"
    }
  ],
  "codeCommit": "8a2be43d24690b0884749d483d50c9f63a36697e",
  "delivery": {
    "status": "not_released",
    "notes": "独立 worktree 本地开发，不合并或部署。"
  }
}
```
