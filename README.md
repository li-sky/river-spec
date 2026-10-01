# RIVER 规格文档

本仓库维护 RIVER 自部署多人 No-Limit Texas Hold’em 现金桌的需求、模块规格、页面交互与验收场景。实现、测试、构建和部署文件位于 [river-code](https://github.com/li-sky/river-code)。

## 术语与范围

配置属于系统，设置属于用户或房间。host 是房主，guest 是加入房间的人；访客是临时账号身份，旁观者是尚未入座的房间成员。

当前使用整数娱乐筹码，每桌最多 9 人，支持手机竖屏、平板与电脑横屏。无限注描述下注规则。规则、房间、身份、存储和媒体保持适当解耦。

## 后端模块

| 规格 | 对应实现 |
| --- | --- |
| [系统配置模块规格](modules/config.md) | [backend/internal/config](https://github.com/li-sky/river-code/tree/main/backend/internal/config), [.env.example](https://github.com/li-sky/river-code/blob/main/.env.example) |
| [身份与用户设置模块规格](modules/identity.md) | [backend/internal/identity](https://github.com/li-sky/river-code/tree/main/backend/internal/identity) |
| [数据存储模块规格](modules/store.md) | [backend/internal/store](https://github.com/li-sky/river-code/tree/main/backend/internal/store) |
| [德州扑克规则模块规格](modules/poker.md) | [backend/internal/poker](https://github.com/li-sky/river-code/tree/main/backend/internal/poker) |
| [房间与实时服务模块规格](modules/server.md) | [backend/internal/server](https://github.com/li-sky/river-code/tree/main/backend/internal/server) |
| [服务启动与部署模块规格](modules/runtime.md) | [backend/cmd/river](https://github.com/li-sky/river-code/tree/main/backend/cmd/river), [Dockerfile](https://github.com/li-sky/river-code/blob/main/Dockerfile), [compose.yaml](https://github.com/li-sky/river-code/blob/main/compose.yaml), [scripts/run-dev.sh](https://github.com/li-sky/river-code/blob/main/scripts/run-dev.sh) |

## 前端页面

| 规格 | 对应实现 |
| --- | --- |
| [入口与登录页规格](pages/01-entry-login.sdd.md) | [frontend/src/App.tsx](https://github.com/li-sky/river-code/blob/main/frontend/src/App.tsx) |
| [大厅页规格](pages/02-lobby.sdd.md) | [frontend/src/App.tsx](https://github.com/li-sky/river-code/blob/main/frontend/src/App.tsx) |
| [牌桌页规格](pages/03-table.sdd.md) | [frontend/src/App.tsx](https://github.com/li-sky/river-code/blob/main/frontend/src/App.tsx) |

入口、大厅和牌桌目前由 App 根据会话和 room 参数切换。个人设置、创建牌桌、买入、房间设置和表情选择器属于页面内弹窗，见 [共享设置与媒体互动](pages/04-shared-settings-media.sdd.md)。

## SDD 与朋友试玩

[开发工作流](workflow.md) 已提供一变更一计划的执行约定、[计划模板](templates/plan.md)和标准库命令行工具。通过 `new → check → start → run → finish` 将规格、任务、代码提交和验收证据关联起来。

[首个实际计划](plans/sdd-workflow.md) 用工作流自身的变更验证流程。开发完成与发布分开记录；朋友反馈可先人工整理成计划。

```bash
python3 scripts/sdd.py new mobile-raise-input --title "改善手机加注输入" --spec table --risk ui
# 填写计划，然后执行：
python3 scripts/sdd.py check plans/mobile-raise-input.md
python3 scripts/sdd.py start plans/mobile-raise-input.md
# 实现并提交代码，实际验收，再运行：
python3 scripts/sdd.py run plans/mobile-raise-input.md
python3 scripts/sdd.py finish plans/mobile-raise-input.md
```

朋友反馈入口、统一开发命令、版本提醒、后端安全重启和手牌边界发布仍为待实现方案。已有 Vite HMR 与快照恢复不代表这些能力已经完成。

## 代码对应与验证

[spec-map.json](spec-map.json) 提供机器可读的源码与规格对应关系。规格基线对应代码仓库提交 `4975694e5a0793a1ffaec30deecb57d181e4d791`。

公开／私人房间变更基于代码提交 `92c18911c8ae6198441f7833e25b7588a8478af1` 更新 server/lobby/shared/table 规格，验收证据见 [房间可见性计划](plans/room-visibility.md)。可见性必填，不兼容缺少字段的旧请求或快照；完成开发，已在本地 Docker 重建启动，尚未发布生产环境。

2026 年 10 月 1 日已通过后端 `go test ./...` 与前端 `npm run build`。测试表记录验收要求和源码覆盖，不代表每次文档变更都重新执行所有外部验收；真实 PostgreSQL、多人浏览器、GitHub OAuth 与公网 TURN 的验证范围以记录为准。

2026 年 10 月 1 日已将完整 Emoji、房主置顶消息、当前可见手牌牌型的代码与规格 worktree 合入各自本地 `main`，保留主线房间可见性和 UI 可读性改进。集成代码基线为 `8bdbd38`，具体合并提交、后端 test/vet、前端构建、双仓链接及隔离内存服务上的桌面/手机双会话验证见 [worktree 集成计划](plans/merge-worktrees.md)。本次未推送或部署，原功能计划中的独立分支证据保留为历史记录。

- [HTTP 与 WebSocket 契约](https://github.com/li-sky/river-code/blob/main/docs/CONTRACT.md)
- [部署说明](https://github.com/li-sky/river-code/blob/main/docs/DEPLOYMENT.md)
- [已有验证记录](https://github.com/li-sky/river-code/blob/main/docs/VERIFICATION.md)
- [组件与素材来源](https://github.com/li-sky/river-code/blob/main/docs/CREDITS.md)

运行所需技术说明随代码保存；本仓库集中维护模块与页面规格，行为变化时同步相应契约、测试和规格。
