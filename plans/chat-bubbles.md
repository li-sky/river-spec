# 微信风格聊天气泡与消息菜单

## 元信息

```json
{
  "id": "chat-bubbles",
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

用户要求在 worktree 改进当前聊天为类似微信的气泡风格，手机长按弹出置顶、撤回等操作，并明确桌面端使用右键。现有聊天列表缺少左右分布，置顶按钮常驻每行，且没有撤回能力。

## 预期行为与范围

按用户追加要求复用网上成熟组件：Chatscope Chat UI Kit 的 Message、TextContent、Header/Footer、Avatar 负责消息气泡，Radix Context Menu 负责右键/触摸长按、菜单、焦点与键盘导航。本人消息右侧绿色气泡，其他成员左侧浅色气泡，显示头像、名称、发送时间与置顶标识，长文本换行。桌面右键、手机静止长按 700ms（库默认值）打开消息菜单，键盘 Enter/Space/Shift+F10 也可打开；移动、取消、多指与滚动不触发长按。菜单有复制、房主置顶/取消置顶、本人两分钟内撤回，点击外部或 Escape 关闭，Escape/操作后恢复消息焦点。断线禁用服务端操作；滚动关闭菜单，菜单保持在视口内。聊天组件按需加载。

服务端新增 recall_message(messageId)，仅当前连接的原作者可撤回本桌最近记录或独立保留的置顶消息，按服务端发送时间计算两分钟窗口，限流 12 次/10 秒，两层聊天开关均须开启。成功保留 ID/作者/原时间，清空正文并设置 recalled=true，在两端显示撤回提示，同时清除相同 ID 的置顶；不可置顶或重复撤回已撤回消息。保存成功才广播，失败回滚内容、置顶及版本；旧快照缺 recalled 字段视为 false，无 SQL 迁移。撤回更新时同步清除牌桌头像短时文字气泡。范围不含编辑、跨房间聊天、房主撤回他人消息、合并主目录或部署。

## 验收场景

- [x] AC-01: 真实双会话查看左右消息、头像、时间、长文本和空状态；1440/390/320px 无溢出且输入、置顶区可用。
- [x] AC-02: 真实浏览器验证桌面右键、键盘与手机长按菜单、复制、房主置顶/取消；点击外部/Escape/滚动关闭，滑动/短按/取消/多指不误触，菜单在视口内且断线管理禁用。
- [x] AC-03: 本人撤回两端同步，正文消失，关联置顶和头像文字清除，刷新仍为提示；他人无撤回，已撤回无菜单。服务端验证非作者/旧连接/跨房间/过期/重复、开关/限流、裁剪后的置顶撤回、保存失败回滚与旧快照恢复。

## 任务

- [x] T-01: root 在两仓 worktree 提交开工计划，实现气泡、菜单、服务端撤回与必要边界测试。
- [x] T-02: root 运行隔离双浏览器验收、后端 test/vet 和前端构建，审阅差异，同步长期规格/契约。
- [x] T-03: root 提交引用固定计划的代码，以最终 HEAD 运行 SDD 检查并完成计划，保留原目录改动。

## 审阅结论

目标已达成，按用户追加要求复用成熟的 Chatscope Chat UI Kit 2.1.1（Message、TextContent、Header/Footer、Avatar）与 Radix Context Menu 2.3.7；没有保留自写的气泡布局或长按菜单实现。代码基线 [215a1fd3a20f596e96d52533c7c2b839a8187c27](https://github.com/li-sky/river-code/commit/215a1fd3a20f596e96d52533c7c2b839a8187c27)，SDD footer 指向补记组件复用需求后的开工规格提交 59cccb7125b7ad6c35072cd4fa84c15adabd4e90。

AC-01/02/03 的界面部分：在隔离 localhost:8094 内存服务上实际执行 scripts/chat_check.cjs，两份真实 Chrome 会话（桌面房主、移动访客）通过。使用 CDP 原生触摸验证短按、移动、取消、多指均不弹菜单，700ms 长按及松手后菜单保留；桌面右键、Shift+F10、方向键、Escape 焦点恢复、外部点击保留输入焦点、剪贴板读取核对、房主置顶/取消、非房主无管理项、他人无撤回、作者撤回两端正文/置顶/头像短时文字同时清除、刷新保持撤回提示、撤回提示无菜单，均实际确认。含 HTML 的用户文字在 Chatscope TextContent 中保持纯文本。1440×844、390×844、320×667 无横向溢出，左右头像/气泡方向正确，长置顶与输入可用，菜单均在视口内。执行代理实际查看桌面与移动截图，截图保存于根工作区 .scratch/chat-review，不提交生成物。

断线验收采用浏览器 offline 阻断重试并显式关闭测试 WebSocket（Chromium 的 offline 仿真可保留已有连接）：确认出现重新连接中、菜单撤回 disabled；不是物理断网设备测试。房主置顶按钮使用相同 connected 门禁，差异审阅确认；未扩大为 iOS/Safari/屏幕阅读器专项验收。沿用 scripts/pin_check.cjs 并改为通过右键菜单操作，实际运行通过，补验双端置顶替换/顶部与菜单取消、手机短屏长置顶滚动。

AC-03 的服务边界由 recall_test.go 实际测试：原作者权限、拒绝房主撤回他人/旧连接/跨桌/无效 ID/未来时间/过期/重复，系统与房间开关、12次/10秒限流、119秒允许、牌局不变、快照恢复/旧字段兼容、独立置顶裁剪后撤回提示、保存故障正文/置顶/版本回滚且无广播、不清除其他置顶。最终 backend test/vet、frontend build 与 links 证据以以下 SDD runs 为准。

差异审阅确认保存成功后广播与失败恢复路径保留，未增加 SQL 迁移，客户端权限不替代服务端验证。补齐契约、组件许可和 shared 源码映射以及 server/store/table/shared 长期规格。聊天组件按需加载，主 JS 约 344KB、聊天块约 212KB（压缩前）；已有 Emoji 块仍触发 Vite 的 >500KB 提示，构建通过。开发在代码/规格两份 feat/chat-bubbles worktree 完成，从当前已提交 main 基线创建，原目录未提交变化保留；未合并、推送或部署。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T13:53:33.463591Z",
      "codeCommit": "215a1fd3a20f596e96d52533c7c2b839a8187c27",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "72805cef01bced5b1e63dc364d1cda03518e178dbbe81e8d63307ffc177a0946",
      "specSha256": {
        "server": "c908bbb0906ef57b213e7710812a75903c45193f78dcc46d8d456aeccf6790b6",
        "store": "50ca2f13ec4b0abbd9128398055572e449bcac428bbbd1dd9304576b9b831465",
        "table": "576d5e60e36cce0f524445de786413d34ea0d1849da320184b1da63ef96f4be1",
        "shared": "829a533cb8f1ff1f2c7e8f291dc447f2a15fd579cf98b1677cc97b210dcd6f85"
      },
      "planFingerprint": "653e9c8e3b560b37ed7b87d1f0aed96000d664dedbf265724383352abc74ac76"
    },
    {
      "check": "backend",
      "commands": [
        {
          "argv": [
            "C:/Users/s-k-y/AppData/Local/Temp/river-go-tools/go/bin\\go.EXE",
            "version"
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\chat-bubbles\\river-code\\backend",
          "exitCode": 0
        },
        {
          "argv": [
            "C:/Users/s-k-y/AppData/Local/Temp/river-go-tools/go/bin\\go.EXE",
            "test",
            "./..."
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\chat-bubbles\\river-code\\backend",
          "exitCode": 0
        },
        {
          "argv": [
            "C:/Users/s-k-y/AppData/Local/Temp/river-go-tools/go/bin\\go.EXE",
            "vet",
            "./..."
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\chat-bubbles\\river-code\\backend",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T13:53:34.261148Z",
      "codeCommit": "215a1fd3a20f596e96d52533c7c2b839a8187c27",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "72805cef01bced5b1e63dc364d1cda03518e178dbbe81e8d63307ffc177a0946",
      "specSha256": {
        "server": "c908bbb0906ef57b213e7710812a75903c45193f78dcc46d8d456aeccf6790b6",
        "store": "50ca2f13ec4b0abbd9128398055572e449bcac428bbbd1dd9304576b9b831465",
        "table": "576d5e60e36cce0f524445de786413d34ea0d1849da320184b1da63ef96f4be1",
        "shared": "829a533cb8f1ff1f2c7e8f291dc447f2a15fd579cf98b1677cc97b210dcd6f85"
      },
      "planFingerprint": "653e9c8e3b560b37ed7b87d1f0aed96000d664dedbf265724383352abc74ac76"
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
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\chat-bubbles\\river-code\\frontend",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T13:53:36.815036Z",
      "codeCommit": "215a1fd3a20f596e96d52533c7c2b839a8187c27",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "72805cef01bced5b1e63dc364d1cda03518e178dbbe81e8d63307ffc177a0946",
      "specSha256": {
        "server": "c908bbb0906ef57b213e7710812a75903c45193f78dcc46d8d456aeccf6790b6",
        "store": "50ca2f13ec4b0abbd9128398055572e449bcac428bbbd1dd9304576b9b831465",
        "table": "576d5e60e36cce0f524445de786413d34ea0d1849da320184b1da63ef96f4be1",
        "shared": "829a533cb8f1ff1f2c7e8f291dc447f2a15fd579cf98b1677cc97b210dcd6f85"
      },
      "planFingerprint": "653e9c8e3b560b37ed7b87d1f0aed96000d664dedbf265724383352abc74ac76"
    }
  ],
  "codeCommit": "215a1fd3a20f596e96d52533c7c2b839a8187c27",
  "delivery": {
    "status": "not_released",
    "notes": "两仓独立 worktree 开发与验收完成，原目录未提交改动保留；未合并、推送或部署。"
  }
}
```
