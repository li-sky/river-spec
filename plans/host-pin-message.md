# 房主置顶聊天消息

## 元信息

```json
{
  "id": "host-pin-message",
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

用户要求增加房主 pin 消息功能，并使用 worktree 实现。当前聊天仅展示最近 100 条，重要消息容易被后续聊天淹没；目标是由房主将已有消息固定在聊天面板顶部，所有房间成员可读。

## 预期行为与范围

每房间同时置顶一条消息；房主可置顶自己或其他成员的已有消息，替换当前置顶，或取消。服务端从本房间最近消息中按 messageId 查找，不接受客户端提供内容；pin_message/unpin_message 都由当前房主且系统与房间聊天均开启时操作，牌局中也可使用。取消须匹配当前 messageId，避免旧界面取消新置顶。每连接置顶操作最多 12 次/10 秒。

RoomState 和房间快照增加 pinnedMessage: Message|null，旧快照缺字段视为 null，无需 SQL schema 改动。独立保留消息内容，即使原消息被最近 100 条裁剪或发送者离开，置顶仍保留；房主移交不清除，新房主获得操作权限。保存成功后广播；失败恢复原置顶和版本，不广播。

聊天面板标题下显示置顶、发送者、原文与时间，独立于聊天滚动区；消息行向房主显示置顶/取消置顶按钮，断线禁用。非房主只读，手机和桌面均可操作，长文本可滚动且不会挤掉输入框。聊天关闭时入口与面板隐藏，置顶保留，重新开启后显示。范围不包含多条置顶、编辑消息、删除消息或发布部署。

## 验收场景

- [x] AC-01: 房主置顶任一成员消息、替换与取消，所有成员收到一致状态；非房主、替换连接、无效/跨房间消息及过期取消被拒绝且不修改状态。
- [x] AC-02: 聊天的系统/房间开关及置顶操作限流生效；进行中牌局可置顶，房主移交后权限随当前 hostId 变化。
- [x] AC-03: 最近聊天被裁剪后仍显示原置顶；发送者离开不丢失；保存失败回滚且无广播；恢复保留置顶，旧快照缺字段恢复为 null。
- [x] AC-04: 双浏览器真实服务验证房主置顶、替换、取消，guest 无管理按钮，刷新仍可见；桌面及手机长文本与滚动不遮挡置顶/输入框且无横向溢出。

## 任务

- [x] T-01: 在代码和规格各自 worktree 中完成 SDD 计划提交及后端命令、状态、持久化与边界测试。
- [x] T-02: 完成前端置顶内容、权限按钮和响应式布局，并运行双浏览器验收。
- [x] T-03: 同步数据契约、server/store/table/shared 长期规格、提交代码与最终验证证据，完成计划。

## 审阅结论

实现达成目标。代码基线为 [c21c80c253356a714b3ac5691a6ed9fdc59e5647](https://github.com/li-sky/river-code/commit/c21c80c253356a714b3ac5691a6ed9fdc59e5647)，代码提交引用开工规格提交 6e4eb3870a1e3a12ab76fc99b9adcbbc85fb5c01。两仓库均在独立 feat/host-pin-message worktree 完成，主目录既有 App.tsx 改动保留。

AC-01/02/03：已实际运行五项 TestPin* 服务测试，确认原消息内容不被客户端伪造覆盖、仅本桌消息可置顶、拒绝非房主和旧连接、过期取消无状态变化/广播、两层聊天开关及限流、牌局中操作、新房主继承、105 次新聊天后最近 100 条外的置顶仍保留、作者离开和服务重建后保留、取消持久化、旧字段缺失为 null，以及失败保存回滚/无广播。

AC-04：在隔离服务 localhost:8091、内存存储、两份 Chrome 会话实际执行 scripts/pin_check.cjs 通过。验证置顶/替换/顶部和消息行取消、guest 无管理按钮、双端同步、刷新、React 转义含 HTML 的文本、聊天滚动。1440×1000、390×844、390×667 均无横向溢出且置顶与输入区可用；执行代理实际查看桌面与手机截图，确认长置顶有界滚动。验收过程中补齐手机聊天图标的可读名称。断线按钮的 disabled 属性经差异审阅确认，未将网络离线场景记录为浏览器验收通过。

差异审阅确认沿用保存后广播和回滚路径；原消息复制独立于列表裁剪，不引入 SQL schema 变化或客户端权限判定替代。server/store/table/shared 规格、README 与契约同步。后端全套 test/vet、前端构建和链接检查以以下最终提交运行记录为准。可选 race 因当前 Windows 缺少 CGO 未运行成功，真实 PostgreSQL 进程重启不在本次证据内。开发完成，未合入主目录、未部署、未推送。

首次 SDD frontend profile 因 Windows subprocess 找不到 npm 可执行文件失败，随后复用已存在的临时 npm.exe 启动器，检查其源码确实调用 D:/node.exe 和真实 npm CLI、透传参数与退出码，再运行 frontend profile 通过。未修改 SDD 工具，失败记录保留；最终代码提交 c21c80c 上再次执行双浏览器脚本通过。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T11:20:42.611559Z",
      "codeCommit": "c21c80c253356a714b3ac5691a6ed9fdc59e5647",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "b4d5772649036f685f3f70c7a1bf2789d50dfd47af67f06a952a39a810d8def6",
      "specSha256": {
        "server": "96d1c44119c6ce444d6e558d3425fe96c595d3fc77993983a65d0fa256a19ad9",
        "store": "14bb0d8a90eb4bf336d8d66f0225f86e3e782ada61fdb639fbf57b8bcea351dd",
        "table": "b5fef642cb3b3b3073b95fb6cc305f4d81d83fd7691026aab377e55d3edd583e",
        "shared": "bc9c6f8b3a6ed375c9741f9b6a391c9a12ddfeaf32064ec302403f47369bf057"
      },
      "planFingerprint": "a35d7ac727b5080ed8cc9a7503e1fc833b5f6afeb71fb4505a48f19702dabdb6"
    },
    {
      "check": "backend",
      "commands": [
        {
          "argv": [
            "C:\\Users\\s-k-y\\AppData\\Local/Temp/river-go-tools/go/bin/go.exe",
            "version"
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\host-pin-message\\river-code\\backend",
          "exitCode": 0
        },
        {
          "argv": [
            "C:\\Users\\s-k-y\\AppData\\Local/Temp/river-go-tools/go/bin/go.exe",
            "test",
            "./..."
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\host-pin-message\\river-code\\backend",
          "exitCode": 0
        },
        {
          "argv": [
            "C:\\Users\\s-k-y\\AppData\\Local/Temp/river-go-tools/go/bin/go.exe",
            "vet",
            "./..."
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\host-pin-message\\river-code\\backend",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T11:20:43.114676Z",
      "codeCommit": "c21c80c253356a714b3ac5691a6ed9fdc59e5647",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "b4d5772649036f685f3f70c7a1bf2789d50dfd47af67f06a952a39a810d8def6",
      "specSha256": {
        "server": "96d1c44119c6ce444d6e558d3425fe96c595d3fc77993983a65d0fa256a19ad9",
        "store": "14bb0d8a90eb4bf336d8d66f0225f86e3e782ada61fdb639fbf57b8bcea351dd",
        "table": "b5fef642cb3b3b3073b95fb6cc305f4d81d83fd7691026aab377e55d3edd583e",
        "shared": "bc9c6f8b3a6ed375c9741f9b6a391c9a12ddfeaf32064ec302403f47369bf057"
      },
      "planFingerprint": "a35d7ac727b5080ed8cc9a7503e1fc833b5f6afeb71fb4505a48f19702dabdb6"
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
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\host-pin-message\\river-code\\frontend",
          "exitCode": 127
        }
      ],
      "exitCode": 127,
      "at": "2026-10-01T11:20:44.246333Z",
      "codeCommit": "c21c80c253356a714b3ac5691a6ed9fdc59e5647",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "b4d5772649036f685f3f70c7a1bf2789d50dfd47af67f06a952a39a810d8def6",
      "specSha256": {
        "server": "96d1c44119c6ce444d6e558d3425fe96c595d3fc77993983a65d0fa256a19ad9",
        "store": "14bb0d8a90eb4bf336d8d66f0225f86e3e782ada61fdb639fbf57b8bcea351dd",
        "table": "b5fef642cb3b3b3073b95fb6cc305f4d81d83fd7691026aab377e55d3edd583e",
        "shared": "bc9c6f8b3a6ed375c9741f9b6a391c9a12ddfeaf32064ec302403f47369bf057"
      },
      "planFingerprint": "a35d7ac727b5080ed8cc9a7503e1fc833b5f6afeb71fb4505a48f19702dabdb6"
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
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\host-pin-message\\river-code\\frontend",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T11:20:55.892665Z",
      "codeCommit": "c21c80c253356a714b3ac5691a6ed9fdc59e5647",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "b4d5772649036f685f3f70c7a1bf2789d50dfd47af67f06a952a39a810d8def6",
      "specSha256": {
        "server": "96d1c44119c6ce444d6e558d3425fe96c595d3fc77993983a65d0fa256a19ad9",
        "store": "14bb0d8a90eb4bf336d8d66f0225f86e3e782ada61fdb639fbf57b8bcea351dd",
        "table": "b5fef642cb3b3b3073b95fb6cc305f4d81d83fd7691026aab377e55d3edd583e",
        "shared": "bc9c6f8b3a6ed375c9741f9b6a391c9a12ddfeaf32064ec302403f47369bf057"
      },
      "planFingerprint": "a35d7ac727b5080ed8cc9a7503e1fc833b5f6afeb71fb4505a48f19702dabdb6"
    }
  ],
  "codeCommit": "c21c80c253356a714b3ac5691a6ed9fdc59e5647",
  "delivery": {
    "status": "not_released",
    "notes": "仅在本地独立 worktree 完成开发与验收，保留主目录未提交改动；没有部署或替换现有服务。"
  }
}
```
