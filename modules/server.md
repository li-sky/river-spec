# RIVER 房间与实时服务模块规格

基线日期：2026-10-01。状态：当前源码与测试的文档基线。路径均相对于 RIVER 项目根目录。已确认需求、现有实现护栏和未实现能力分别标示。

## 目的与已确认需求

将登录身份、房间成员、现金桌设置、扑克引擎、实时通信和持久化组织成可玩的多人系统。host 是房主，guest 是加入房间的人；注册／访客是另一维度的账号身份。用户确认房主可开房、调整盲注及玩家手上金额，接受行动超时自动过牌／弃牌、断线重连与房主离开转移。现金桌使用虚拟筹码。

术语约定：系统能力和默认值叫“配置”；房间盲注、买入、行动时间、语音方式等叫“房间设置”或“单局设置”；音量、头像等叫“用户设置”。本模块不实现头像动画、声音合成或麦克风采集，但提供状态、声音事件、reaction 和 WebRTC 信令。

## 当前接口

Go 生命周期接口为 `New(ctx, cfg, auth, db) (*Server, error)`、`Handler() http.Handler`、`Close()`。存储依赖仅要求 `SaveRoom` 和 `LoadRooms`；账号服务负责会话和用户查询。各房间使用互斥锁串行修改状态，服务映射另有读写锁。

### HTTP

| 路由 | 当前用途与权限 |
| --- | --- |
| `GET /api/rooms` | 认证用户只读取公开房间摘要；私人房间对房主自己的大厅也隐藏。玩家人数统计已入座者，状态为 `waiting`／`playing`；不返回底牌或牌堆。 |
| `POST /api/rooms` | 任意已认证身份创建房间并成为房主；输入 `{name, settings}`，成功 201 返回 `{id}`。不是仅平台管理员可开房。 |
| `GET /api/rooms/{id}` | 认证用户读取按自身身份过滤的房间状态；HTTP 获取状态本身不创建成员。 |
| `GET /api/rooms/{id}/ws` | 认证后加入房间；首次连接作为座位 `-1` 的旁观成员，再通过 `sit` 入座。 |
| `GET /api/health`、`GET /healthz` | 调用存储 `LoadRooms` 探测就绪；成功 200，失败 503。不是只证明 HTTP 进程存活。 |
| `/api/*` 未知路由 | 404 JSON 错误。 |
| `GET/HEAD /...` | 静态文件服务与 SPA 回退；带文件扩展名的未知资源返回 404。 |

认证、用户资料和 `GET /api/config` 路由由 `identity` 注册，`server.Handler` 最后应用身份中间件；详细登录策略另见身份模块基线。

HTTP 错误返回 `{error:string}`，JSON 响应为 `no-store`。创建房间的 JSON 请求体当前上限 16 KiB，拒绝未知字段；房名去首尾空白后 1～48 个字符。房间不存在为 404，未认证为 401，输入无效为 400，存储失败为 503。

### WebSocket 命令与权限

每条消息均以 `type` 区分；实际成员身份从会话和连接取得，不接受客户端伪造 `from`。

| `type` | 输入关键字段 | 当前权限与条件 |
| --- | --- | --- |
| `sit` | `seat`、可选 `buyIn` | 成员自行入座；只在两手之间，目标座位空闲，范围符合人数上限。省略／0 买入使用本房间默认值。 |
| `sitout` | `sittingOut` 布尔值 | 仅本人且已入座；保留座位与筹码，跳过下一手或恢复参与，当前手及行动令牌不变。使用原有快照保存和失败回滚。 |
| `stand` | 无 | 成员自行离座；只在两手之间，设置座位为 `-1`。 |
| `start` | 无 | 仅房主开始下一手；不能覆盖进行中的手牌，至少两名在线、入座、有筹码且未休息的有效身份玩家。 |
| `action` | `action`、`amount`、`turnToken` | 当前行动者；动作由引擎验证。加注 `amount` 是本轮总额；令牌须来自最新状态，拒绝旧动作和重复提交。 |
| `settings` | 完整 `settings` 对象 | 仅房主且两手之间；不是 PATCH 合并。缩小人数前须让超出新座位范围的玩家离座。 |
| `stack` | `playerId`、`amount` | 仅房主且两手之间，为指定已入座玩家设置虚拟筹码绝对值。 |
| `kick` | `playerId` | 仅房主且两手之间；不能踢自己。提交成功后关闭目标连接，关闭码 4003。当前移出不是永久封禁。 |
| `chat` | `text` | 成员可发言，系统和房间同时允许；消息持久化并保留最近 100 条。 |
| `pin_message` | `messageId` | 当前房主且系统/房间聊天均开启；按本桌最近消息 ID 置顶或替换唯一置顶，牌局中亦可操作。客户端不能提供置顶内容。 |
| `unpin_message` | `messageId` | 同上权限；只允许取消匹配当前 ID 的置顶，过期取消请求被拒绝。 |
| `emoji` | `emoji` | 更新自己的头像 emoji，可用空字符串清除；系统和房间同时允许；调用身份服务保存个人值。 |
| `reaction` | `to`、`emoji` | 向本桌成员发射表情，广播瞬时事件；系统和房间同时允许，不写入房间快照。 |
| `signal` | `to`、`data` | 仅向本桌在线、获准语音名单内的另一成员转发有效 JSON；不写入房间快照。 |
| `leave` | 无 | 成员自行离开。进行中保留参赛记录到结算，设置离开／休息／离线标记；房主主动离开立即移交。 |

服务端事件为 `state`（完整个性化房间状态）、`error`（消息文本）、`reaction`、`signal`、`sound`。音效名称为 `deal/chips/fold/win`；发牌和结算由服务端行为触发。具体气泡动效和音色由前端完成。

## 房间设置与当前数值护栏

| 字段 | 当前允许范围／含义 |
| --- | --- |
| `visibility` | 必填 `public`／`private`；创建、设置请求和快照均拒绝缺失、空值或非法值，不保留旧数据兼容。前端新建表单初始选择公开。 |
| `smallBlind`／`bigBlind` | 正整数；小盲不超过 500,000，大盲至少为小盲两倍且不超过 1,000,000。 |
| `buyIn` | 房间默认买入，2 倍大盲至 1,000,000,000；入座自选买入采用同一范围。 |
| `maxPlayers` | 2～9；座位范围 `0 .. maxPlayers-1`。 |
| `actionSeconds` | 10～120 秒。 |
| `voiceEnabled`／`chatEnabled`／`reactionsEnabled` | 本桌能力设置，不能越过系统禁止。 |
| `voiceMode` | `free` 或 `push-to-talk`；缺失时补齐系统默认，系统默认缺失再回退 `free`。 |
| `spectatorVoiceEnabled` | 本桌是否允许旁观者语音；同时要求系统配置允许。 |

房主修改 `stack` 的范围为 0～1,000,000,000。房间创建、设置及筹码上限是当前资源／数值护栏，不代表 No-Limit 下注额存在固定桌面封顶；每次下注上限为玩家剩余筹码。

当前每身份最多作为房主拥有 10 个房间、单服务最多 1,000 个房间；超限创建返回 429。每房间最多保留 100 个成员（包括旁观者和断线未清理成员）。这些是实现上限，不是独立用户需求。

### 公开与私人房间

公开房间显示在大厅；私人房间不出现在列表，通过 `/?room=<房间 ID>` 邀请。房间 ID 来自 128 位密码学随机数；持链接的认证用户（含访客身份）可以读取个性化状态和通过 WS 加入。私人是限制大厅发现，不是逐人邀请白名单或房间密码；链接可以被转发，既有房间转私人后原来持链接者仍可进入。

可见性属于房间设置，房主在两手之间修改，非房主和进行中的手牌均不能修改。成功保存后广播最新设置，存储失败则回滚且不广播。切换不改变房间 ID、不撤销链接或现有成员；设置保存在既有 JSON 快照，无 SQL 迁移。按用户明确要求不保留兼容性：缺少可见性的请求直接拒绝，旧快照缺少该字段时启动恢复失败，无自动迁移。

`visibility_test.go` 覆盖 HTTP 创建/列表/链接加入、未认证访问、必填及非法值、房主权限、进行中限制、广播、保存失败及快照恢复；实际运行证据见本次计划。

## 状态模型与恢复

公开 `RoomState` 包含 `id/name/hostId/settings/players/hand/messages/version/voiceParticipantIds`。`Player` 区分座位、筹码、连接和休息状态，并包含本桌获胜手数 `wins`，源码还包含离线时间及主动离开标记。`hand` 来自 `Hand.View(userID)`，额外添加 `deadline` 和 `turnToken`。完整牌堆和其他玩家未公开底牌仅存在私有存储快照。

私有快照保存按身份的 `winCounts` 和 `lastCountedHand`。同步结算筹码时，仅对已完成且未计入的手牌更新统计；引擎 winners 内正额赢家每手各加一次，重复身份去重，平分及不同边池赢家分别计数。完成标记、筹码和统计使用相同保存、回滚和广播路径，覆盖普通行动、盲注直接全下及超时结束。读取视图、刷新和重复同步不增加次数。离开／清理成员保留其该桌统计，再连接从统计表恢复 `Player.wins`；新房间从零开始。该统计表和完成标记不对外公开，客户端无设置接口。旧快照缺统计字段时从零初始化并跳过其已完成手牌，旧进行中手牌结束后计入；不回填不存在的历史。

房间摘要不需要有成员身份；建立 WS 后才成为成员。同一身份在同一房间的新 WS 替换旧连接，旧连接的退出回调不会覆盖新连接。新连接从账号同步昵称、头像和个人 emoji。

开始每手时庄家从上手庄家后顺时针寻找参与者；开始和每次有效行动后同步引擎筹码、生成新行动令牌并设置截止时间。结束时清除截止时间，清理主动离开者。下一手由房主明确发起，当前不自动连续开局。

每秒计时任务检查截止时间：到时调用 `AutoAction`，能过牌则过牌，否则弃牌。断线本身不立即强制弃牌；参赛者仍受原行动期限约束，重连保留同一手牌。主动离开者的已参与手牌同样保留到结算。

房主断线 30 秒后移交给成员列表中首个在线、未主动离开的其他成员；无人可接管时房主 ID 清空，之后连接者可接任。两手之间，断线旁观者超过 2 分钟、断线入座者超过 5 分钟会清理；正在参与的一手不受该清理影响。

启动加载每个房间最新 JSON 快照，验证房间 ID 和设置；所有恢复成员标记为离线，记录新的离线时间，保留已有未过期／已过期的行动截止时间。进行中快照缺少令牌则补齐，缺少截止时间则设为当前时间，使计时任务接管而非无限停留。无法解码、非法房间 ID 或非法设置使服务构造失败，不静默略过房间。

## 持久化 安全与失败边界

### 房主置顶消息

`RoomState` 和私有快照包含 `pinnedMessage: Message|null`。每桌同时一条，独立保存原消息的 ID、发送者、文本和发送时间；最近 100 条聊天裁剪、发送者离开和房主移交都不会清除置顶。新房主继承管理权限；缺少该字段的旧快照恢复为 null。pin/unpin 使用正常快照保存、版本与失败回滚路径，成功后向所有成员广播；每连接两种操作共享 12 次/10 秒上限。聊天关闭时保留内容，前端隐藏面板和管理入口，重新开启后显示。

边界测试见 [backend/internal/server/pin_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/pin_test.go)：权限、当前连接、无效 ID、过期取消、功能开关、限流、手牌中操作、房主移交、裁剪、作者离开、恢复及保存故障。实际执行证据见 [置顶计划](../plans/host-pin-message.md)。

- 状态命令先保存旧快照，修改后版本递增；成功持久化后再广播个性化状态和音效。保存失败恢复旧快照，返回可重试错误，不广播未提交状态。连接和计时器变更也采用保存失败回滚。

- 上述回滚仅覆盖 `roomData`。`emoji` 先调用身份服务保存个人 emoji，再保存房间快照，两次写入没有跨模块事务；第二次失败可能使账号 emoji 已改变而房间回退。不能把这条路径描述为完整原子操作。

- `signal` 和 `reaction` 为即时事件，不增加房间版本、不落库；不保证重连补发。

- 每次接收命令重新验证会话，每次向连接排队也验证会话；注销或过期后不会继续获得新的私牌状态。

- WS Origin 允许同请求 Host 的 HTTP(S) origin，并允许没有 Origin 的客户端；拒绝不匹配浏览器来源。这是当前来源策略，不是对所有任意客户端的额外认证替代。

- WS 读消息上限 64 KiB；信令 `data` 为有效 JSON 且 1～32 KiB；当前没有服务端 SDP／ICE 深层 schema 校验。

- 10 秒窗口：全部消息最多 300 次，信令最多 240 次，reaction 和头像 emoji 各最多 15 次，聊天最多 12 次；超额命令返回错误。

- 聊天去首尾空白后 1～300 个字符，禁止 NUL；emoji 当前接受最多 16 个 Unicode 码点且最多 64 字节、没有换行或 NUL 的短文本，身份层头像保存采用相同上限。该验证不是严格的 Unicode emoji 白名单。

组合头像保存与 WS 上限对齐的代码基线为 `0e8d22b6a6708aaf0777586a8bee305ce8b4f7da`；本次验收见 [完整 Emoji 计划](../plans/all-emoji.md)。

- 每连接发送队列 64 项，队列满关闭连接；心跳每 25 秒、读存活窗口 70 秒、写截止 10 秒。慢客户端恢复依赖重连，不保证即时事件必达。

- `signal` 只允许权威 `voiceParticipantIds` 中的双方：在线入座者按座位优先，允许的旁观者按 ID 排序补足，最多 9 人。语音采用前端 WebRTC，服务端不转发音频媒体、不录音；房间语音模式只通过状态指导客户端行为。

## 关键验收场景与测试证据

| 场景 | [backend/internal/server/server_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server_test.go) 中对应测试 |
| --- | --- |
| 非房主不得开局；进行中禁止改筹码／设置；玩家与旁观者私牌过滤 | `TestHostPermissionsAndHandPrivacy` |
| 重启保留已过期行动期限、没有假在线连接，超时结算和筹码持久化 | `TestTimeoutAndRestartRecovery` |
| 信令不能跨桌、发送者由会话决定、能力关闭时拒绝 | `TestSignalIsolationAndDisabledFeatures` |
| 回滚不能残留原快照中省略的离开／离线字段 | `TestRollbackRestoresOmittedFields` |
| 匿名 HTTP 拒绝、跨来源 WS 拒绝、访客认证后作为旁观者加入、注销后不能获后续牌局状态 | `TestHTTPAuthAndWebSocketOrigin` |
| 存储失败不推进手牌、不广播，恢复后可用原行动令牌重试 | `TestPersistenceFailureDoesNotBroadcastOrAdvanceHand` |
| 上轮旧令牌不能在下一轮重复行动；极大整数盲注不能通过设置验证 | `TestStaleTurnTokenRejectsRepeatedCheckOnNextStreet` |
| 断线玩家不在当前手牌结算前清理，结算后清理过期成员 | `TestAbandonedPlayersReclaimedOnlyAfterSettlement` |
| 房主移出须在两手之间且持久化成功后才真正移除成员／连接 | `TestHostKickIsDurableAndBetweenHands` |
| 系统／房间两层旁观者语音许可、九人名单、发送者和目标均受名单约束 | `TestSpectatorVoicePermissionsAndNinePeerRoster` |
| 语音默认值补齐、非法模式拒绝、旧快照恢复时补齐 | `TestVoiceModeNormalizationAndRecovery` |
| 九人协商所需正常信令突发允许，超过窗口上限拒绝且不转发 | `TestNinePlayerVoiceNegotiationBurstAndSignalLimit` |

上表为当前测试源码覆盖。这些单元／服务测试使用内存存储，并通过模拟保存故障验证回滚，不足以单独证明 PostgreSQL 部署恢复。PostgreSQL、浏览器和重启执行记录位于 [docs/VERIFICATION.md](https://github.com/li-sky/river-code/blob/main/docs/VERIFICATION.md)，复现脚本见下列路径。可在 `backend` 中执行 `go test -race ./internal/server` 和 `go vet ./internal/server`。

## 源文件与测试相对路径

- [backend/internal/server/server.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server.go)：HTTP、WS、状态投影、连接及恢复。

- [backend/internal/server/commands.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/commands.go)：命令授权、房间修改、定时器、清理及语音信令。

- [backend/internal/server/server_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server_test.go)：服务权限、故障、恢复和语音规则测试。

- [backend/internal/poker/engine.go](https://github.com/li-sky/river-code/blob/main/backend/internal/poker/engine.go)、[backend/internal/identity/identity.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/identity.go)、[backend/internal/store/store.go](https://github.com/li-sky/river-code/blob/main/backend/internal/store/store.go)：依赖模块。

- [backend/cmd/river/main.go](https://github.com/li-sky/river-code/blob/main/backend/cmd/river/main.go)：配置、启动与停机。

- [scripts/smoke.py](https://github.com/li-sky/river-code/blob/main/scripts/smoke.py)、[scripts/recovery_check.py](https://github.com/li-sky/river-code/blob/main/scripts/recovery_check.py)、[scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py)、[scripts/table_layout_check.py](https://github.com/li-sky/river-code/blob/main/scripts/table_layout_check.py)：跨进程与浏览器验收脚本。

- [docs/CONTRACT.md](https://github.com/li-sky/river-code/blob/main/docs/CONTRACT.md)、[docs/DEPLOYMENT.md](https://github.com/li-sky/river-code/blob/main/docs/DEPLOYMENT.md)、[docs/VERIFICATION.md](https://github.com/li-sky/river-code/blob/main/docs/VERIFICATION.md)：跨模块接口、部署和既有验收记录。

## 已知限制与待实现

当前是单实例房间服务，房间以内存中的锁和快照为权威运行状态，没有多实例共享调度或分布式房间路由。只保存最新房间快照和最近聊天记录，没有每手完整可回放历史、长期牌局审计或跨桌虚拟筹码账户。

没有房间删除／归档接口，空房间仍占用当前房间数量额度。没有永久封禁、主动转移房主命令、自动下一手、玩家自行补充筹码的专用命令、逐房间密码或个人开房设置模板；房主可以通过已有 `stack` 命令调整金额。参与者加入进行中的房间可以旁观，但须等本手结束才能入座。

朋友反馈入口、收集存储和后续处理流程未实现。系统配置热重载未实现；服务和身份组件在启动时初始化，没有对外配置重载与传播机制。真实域名下 OAuth、跨网络 TURN/NAT 通话及主观音效体验仍应按部署文档在实际环境验收，不能仅由本模块测试证明。

## 文档与代码入口

[项目文档](https://github.com/li-sky/river-spec) · [代码仓库](https://github.com/li-sky/river-code)。公开／私人房间实现基线为提交 `92c1891`；后续实现变化需同步此规格和验收证据。

本人暂离／返回的基线与验证见 [紧凑 UI 计划](../plans/compact-table-ui.md)。`backend/internal/server/sitout_test.go` 覆盖不能指定他人、旁观者拒绝、下一手排除／恢复、进行中手牌保持、快照及保存失败不广播。

紧凑牌桌与本人暂离的当前代码基线：[23f4a52](https://github.com/li-sky/river-code/commit/23f4a521d52202e871c1a2e28a3729d7bd7e4938)。

### 本桌获胜次数验收

2026-10-01 服务端单元测试及真实浏览器计数／重连／退出再加入、320/390/600px 6/8/9人摊牌布局通过；隔离 PostgreSQL 17 数据库及真实房间服务进程重启验证精确次数和已完成手牌去重。详情、旧快照限制及实际验收范围见 [获胜次数计划](../plans/table-win-counter.md)。当前代码基线：[f38e725](https://github.com/li-sky/river-code/commit/f38e725aaf83a9e5ad0a60f5c28a83acd3eec739)。
