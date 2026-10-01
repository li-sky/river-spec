# 合入聊天气泡与消息菜单 worktree

## 元信息

```json
{
  "id": "merge-chat-bubbles",
  "status": "done",
  "specs": [
    "server",
    "store",
    "table",
    "shared"
  ],
  "risk": "storage",
  "checks": [
    "links",
    "backend",
    "frontend"
  ]
}
```

## 问题与目标

用户确认将已完成的聊天气泡 worktree 合入 main。代码功能提交 215a1fd3a20f596e96d52533c7c2b839a8187c27，规格分支 b071e87878d5844df45c6f00152450a1ccd955d0；当前代码 main f38e725、规格 main 98f8357，均无未提交改动。

## 预期行为与范围

将两仓 feat/chat-bubbles 合入各自本地 main，保留 main 的房间胜场持久化与单一皇冠、手机座位和公共牌布局。复用 Chatscope 气泡与 Radix 右键/长按菜单的行为、复制/置顶/本人两分钟撤回和服务端权限不变。解决冲突时组合两侧行为与规格，不覆盖主线新能力。安装锁定依赖，以合并 HEAD 验证 test/vet、前端 build、双仓 links 和隔离服务上的双浏览器聊天/置顶验收。仅本地合并，不推送或部署；保留原功能计划的分支验收记录。

## 验收场景

- [x] AC-01: 两仓 main 包含聊天分支提交，合并无未解决冲突；差异审阅确认聊天菜单/撤回与胜场/单皇冠共存，主线手机布局保留。
- [x] AC-02: 合并 HEAD 的后端 test/vet、前端 build 与 links 通过；隔离服务双会话验证右键/长按、复制/置顶/撤回及手机布局，置顶回归通过。

## 任务

- [x] T-01: root 提交集成计划并合并两仓，解决冲突并审阅主线兼容性。
- [x] T-02: root 安装锁定依赖、以合并代码运行必要检查与双浏览器验收，记录最终合并 SHA 和开发完成/未部署状态。
- [x] T-03: root 完成 SDD 计划并提交规格，确认两仓 main 工作区清洁。

## 审阅结论

已达成目标。代码 main 合并提交 f740f5c3ea4c073aefc9e7487296b553439cc41e，包含主线 f38e725 与聊天功能 215a1fd；合并提交以 SDD footer 引用开工计划 8e6cc7c2cb30828b6a8b64d83f54f1d8fdf5043f。规格 main 合并提交 18db6f8ea69931c85582893f8e5ae48122d854d6，包含聊天规格 b071e87。

代码无冲突。规格的 server/store/table 三处冲突仅为末尾新增胜场验收与聊天说明，解决时保留两侧段落，其余规格和原功能计划自动合并。差异审阅确认公开 Player.wins、私有 winCounts/lastCountedHand、同一结算保存事务、单一胜场皇冠与房主文字标识均保留；聊天 TextContent、Radix 菜单、撤回和源消息头像清除逻辑同时存在。手机座位与公共牌分区没有被本次差异修改。

以最终代码合并 HEAD 实际运行 npm ci（锁定依赖，无漏洞）、SDD links/backend/frontend，通过后端全部 test/vet 与前端构建，包含 wins_test.go 和 recall_test.go。已有 Emoji 大块仍有 Vite 提示，不影响构建。

实际从 main 编译隔离服务 localhost:8094，内存存储且不读取正式数据库，在两份 Chrome 会话运行 scripts/chat_check.cjs 与 scripts/pin_check.cjs，均通过：桌面右键/键盘/复制、原生触摸长按/短按/移动/取消/多指、外部点击和 Escape 焦点、房主置顶/替换/取消、本人撤回双端与头像/置顶清除、刷新持久提示、纯文本渲染、受控断线禁用管理、1440/390/320px 布局。断线场景为显式关闭测试 WebSocket 并 offline 阻断重试；服务内存恢复/持久化边界由后端测试覆盖，本次未重验真实 PostgreSQL、iOS/Safari 或公网语音。截图保存在 .scratch/chat-merge-review，未提交生成物。

两仓仅本地 main 集成，未推送、部署或替换 localhost:8080 正式服务；原 worktree 与功能分支保留用于后续参考。原功能计划的分支证据保留为历史，当前集成证据固定于本计划。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T13:58:36.418611Z",
      "codeCommit": "f740f5c3ea4c073aefc9e7487296b553439cc41e",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "72805cef01bced5b1e63dc364d1cda03518e178dbbe81e8d63307ffc177a0946",
      "specSha256": {
        "server": "cf1c9b82295250a25e40194b59383841b074ddff4d2d63223883f6c32d77f0dc",
        "store": "fc4321f7a7288c789b0b0620a4da280a66da082e3f60852700e828d1421ee390",
        "table": "7f44395eb667933658bbe661580146d0d9e3f17f55bbba2a143b3d215bb4a63a",
        "shared": "829a533cb8f1ff1f2c7e8f291dc447f2a15fd579cf98b1677cc97b210dcd6f85"
      },
      "planFingerprint": "787a8ae538df42866f11872ea5393f688498129a1ae43876fe3dd02602e1aeff"
    },
    {
      "check": "backend",
      "commands": [
        {
          "argv": [
            "C:/Users/s-k-y/AppData/Local/Temp/river-go-tools/go/bin\\go.EXE",
            "version"
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\river-code\\backend",
          "exitCode": 0
        },
        {
          "argv": [
            "C:/Users/s-k-y/AppData/Local/Temp/river-go-tools/go/bin\\go.EXE",
            "test",
            "./..."
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\river-code\\backend",
          "exitCode": 0
        },
        {
          "argv": [
            "C:/Users/s-k-y/AppData/Local/Temp/river-go-tools/go/bin\\go.EXE",
            "vet",
            "./..."
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\river-code\\backend",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T13:58:37.019265Z",
      "codeCommit": "f740f5c3ea4c073aefc9e7487296b553439cc41e",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "72805cef01bced5b1e63dc364d1cda03518e178dbbe81e8d63307ffc177a0946",
      "specSha256": {
        "server": "cf1c9b82295250a25e40194b59383841b074ddff4d2d63223883f6c32d77f0dc",
        "store": "fc4321f7a7288c789b0b0620a4da280a66da082e3f60852700e828d1421ee390",
        "table": "7f44395eb667933658bbe661580146d0d9e3f17f55bbba2a143b3d215bb4a63a",
        "shared": "829a533cb8f1ff1f2c7e8f291dc447f2a15fd579cf98b1677cc97b210dcd6f85"
      },
      "planFingerprint": "787a8ae538df42866f11872ea5393f688498129a1ae43876fe3dd02602e1aeff"
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
      "at": "2026-10-01T13:58:39.371940Z",
      "codeCommit": "f740f5c3ea4c073aefc9e7487296b553439cc41e",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "72805cef01bced5b1e63dc364d1cda03518e178dbbe81e8d63307ffc177a0946",
      "specSha256": {
        "server": "cf1c9b82295250a25e40194b59383841b074ddff4d2d63223883f6c32d77f0dc",
        "store": "fc4321f7a7288c789b0b0620a4da280a66da082e3f60852700e828d1421ee390",
        "table": "7f44395eb667933658bbe661580146d0d9e3f17f55bbba2a143b3d215bb4a63a",
        "shared": "829a533cb8f1ff1f2c7e8f291dc447f2a15fd579cf98b1677cc97b210dcd6f85"
      },
      "planFingerprint": "787a8ae538df42866f11872ea5393f688498129a1ae43876fe3dd02602e1aeff"
    },
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T14:00:08.383572Z",
      "codeCommit": "f740f5c3ea4c073aefc9e7487296b553439cc41e",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "72805cef01bced5b1e63dc364d1cda03518e178dbbe81e8d63307ffc177a0946",
      "specSha256": {
        "server": "cf1c9b82295250a25e40194b59383841b074ddff4d2d63223883f6c32d77f0dc",
        "store": "fc4321f7a7288c789b0b0620a4da280a66da082e3f60852700e828d1421ee390",
        "table": "7f44395eb667933658bbe661580146d0d9e3f17f55bbba2a143b3d215bb4a63a",
        "shared": "829a533cb8f1ff1f2c7e8f291dc447f2a15fd579cf98b1677cc97b210dcd6f85"
      },
      "planFingerprint": "787a8ae538df42866f11872ea5393f688498129a1ae43876fe3dd02602e1aeff"
    }
  ],
  "codeCommit": "f740f5c3ea4c073aefc9e7487296b553439cc41e",
  "delivery": {
    "status": "not_released",
    "notes": ""
  }
}
```
