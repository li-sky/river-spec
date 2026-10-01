# RIVER 牌桌页规格

- 基线日期：2026-10-01。

- 页面标识：`TABLE`；已登录且 URL 带 `room` 参数时显示，地址为 `/?room=<房间 ID>`。

- 术语：配置属于系统；设置属于用户或房间。host 是房主，guest 是加入房间的人；访客是身份类型，旁观者是尚未坐下的房间状态。

## 目的

提供能够实际进行多人无限注德州扑克现金桌的交互界面。页面展示服务器提供的个性化状态，允许玩家合法下注，支持房主管理、重连、语音和轻量社交。

## 已确认需求

| 编号 | 需求 | 当前落实方式 |
| --- | --- | --- |
| TABLE-R01 | No-Limit Texas Hold’em 现金桌 | 服务器负责发牌、下注校验、边池、分池及结算；前端使用整数娱乐筹码 |
| TABLE-R02 | 房主/加入者角色和管理权限 | 房主开始下一手、修改房间设置、调整筹码和移出其他玩家；服务端再校验权限 |
| TABLE-R03 | 行动限时、断线重连 | 展示行动倒计时与连接状态；重连采用退避；超时由服务器处理 |
| TABLE-R04 | 适当解耦规则判定 | 前端展示状态和提交动作，不计算获胜牌型或结算；独立牌局规则包位于后端 |
| TABLE-R05 | 游戏 UI、卡牌及音效 | 原生卡牌、筹码、庄家标记、行动高亮、胜者状态和事件音效 |
| TABLE-R06 | 语音、定向 Emoji、自身 Emoji 和文字气泡 | 使用真实 WebRTC 信令、服务器消息和 Emoji 事件；规则及限制见共享模块文档 |
| TABLE-R07 | 手机竖屏、平板与电脑横屏布局 | 手机牌桌纵向布局，手机与平板底牌放入操作区；宽桌面底牌保留在自身座位旁 |
| TABLE-R08 | 按当前公开牌面自动计算手牌组合并显示在玩家旁边 | 服务端结合可见底牌与已发公共牌计算当前最佳五张牌型，座位筹码下方和手机底牌区展示 |

## 现有行为

### 加入与连接

先调用 `GET /api/rooms/:id` 读取个性化状态，成功后建立同源 `/api/rooms/:id/ws` WebSocket。加入房间后可先旁观：`seat=-1` 的成员不占座位。坐下通过空座位按钮打开“准备入座”弹窗，买入范围为 2 倍大盲至 10 亿筹码；默认取房间买入设置。

当前前端在一手进行期间禁用空位入座与离座按钮；不存在前端的“预约下一手入座”流程。已入座玩家等待房主开局。房主只有在当前手不活跃、至少两名有筹码且未暂停参与的玩家入座时，才能点击“开始牌局”或“开始下一手”。

离座通过左侧菜单发送 `stand`，顶栏“退出房间”发送 `leave`、退出语音并返回大厅。牌桌不再显示大厅品牌导航。浏览器历史变化仍只切换页面并清理连接，离线成员的后续处理由服务器负责。顶栏“暂离／返回牌局”发送本人 `sitout` 布尔命令，保留座位和筹码，影响下一手的参与名单；进行中的手牌和当前行动义务保持不变。

### 牌局展示

展示房间名称、房主标记、盲注、连接状态、入座/旁观人数、手数、阶段、底池、五张公共牌位、座位、筹码、当轮下注、庄家、弃牌、All-in、倒计时及胜者信息。

- 所有明牌统一展示一个点数与一个花色，去除角落重复花色和底部角标。公共牌、底牌及紧凑摊牌保留红黑颜色与完整可读名称；手机紧凑摊牌将点数和唯一花色横排显示。共享 Card 同时用于入口和大厅装饰牌，代码基线为 `f177020d21477b8253506b1a7a4cdaeb8787387d`，验收见 [单一花色计划](../plans/single-card-suit.md)。
- 十点牌的服务端编码 T 在共享 Card 中统一显示为 `10`，可读名称同步使用 `10`；已有 `10` 字符串和 A/J/Q/K 等点数保持原样。适用于公共牌、底牌、摊牌及入口/大厅装饰牌，服务端编码和规则不变。代码基线为 `6b28070`，验收见 [十点牌显示计划](../plans/card-ten-label.md)。

- 自己已入座时，将视觉座位旋转到牌桌下方；实际座位编号和行动次序仍来自服务器。

- 对手未公开的底牌显示牌背；自己的底牌及允许公开的摊牌由服务器个性化视图决定。前端不会自行获得或恢复对手私牌。

- 翻牌开始以 `HandPlayer.currentHand` 显示“当前：一对”等最佳五张牌型，随当前公共牌的快照更新；本人座位筹码下方显示，手机底牌区同步显示。摊牌后未弃牌对手也显示，隐藏对手、旁观期间未摊牌、已弃牌及下一手翻牌前不显示。前端不计算结果，牌型不表示获胜、胜率或未来听牌。新增标签下方预留间距。手机与平板操作区同步显示当前牌型，布局与主线 UI 改进一致。

- 1180px 及以下宽度分支中，自己两张底牌移至操作区，避免九人桌头像和筹码遮挡；宽桌面保持座位旁底牌。CSS 隐藏另一种布局，验收应检查可见卡牌。

- 有文字或头像 Emoji 更新时，已显示头像的成员出现短暂思考气泡；定向 Emoji 按实际牌桌尺寸飞向目标头像。

- 房间页使用一层紧凑顶栏：左侧菜单，房间名及盲注、连接／可见性两行；右侧头像（无设置标）、分享、暂离／返回、退出房间、玩法简介。手机右侧图标分两行，导航触控区域至少 44px。房主设置、离座、表情及语音／音效放在左抽屉，聊天从右抽屉进入，不挤压牌桌。删除牌桌下方服务器发牌及娱乐筹码说明条，玩法弹窗仍保留筹码说明。

### 行动接口与金额语义

底部固定操作栏始终显示 Call、Raise、Check、Fold 四个按钮；未轮到本人、旁观、弃牌、全下、断线或等待响应时相应动作禁用。Call 和 Check 分别显示，依据待跟金额互斥启用。等待提示、筹码和房主开局入口收为一行；没有独立 All-in 按钮。

| 动作 | 现有前端行为 |
| --- | --- |
| 弃牌 | 发送 `action:'fold'` |
| 过牌／跟注 | 两个独立按钮；没有待跟金额只允许 Check，有待跟金额只允许 Call，跟注最多到剩余筹码 |
| Raise | 打开加注弹窗；`amount` 为本轮累计下注总额，最小完整加注为 `currentBet + minRaise`；使用服务端 `canRaise` 授权并检查整数与上下界 |
| 弹窗 All-in | 将金额设到本轮已下注与剩余筹码之和，确认时发送 `allin`；不足完整加注但可增加当前下注时仍可进入 Raise；低于待跟金额时通过 Call 投入全部剩余筹码 |
| 金额调整 | 弹窗滑块和数字输入，25%／50%／75% 分别为 `currentBet + round(pot × 比例)` 并限制至合法范围，All-in 设最高金额；短全下时滑块上下界均为最高金额 |

每次行动带服务器 `turnToken`。本地记录已发送的令牌，忽略同一令牌的重复点击；提交后操作按钮、金额输入、滑块和快捷选项禁用，显示“已发送，等待牌桌更新…”并标记 `aria-busy`。服务器更新到不同的行动令牌后清除等待显示；服务器错误会释放本地记录并恢复操作，服务器也拒绝过期令牌。断线时继续展示连接状态与禁用操作，不新增自动重发或重试协议。

牌桌状态栏以文字标明当前行动者，本人行动区同时显示剩余秒数和进度条；最后 5 秒使用警示图标与“即将超时”文字，避免只靠颜色或持续闪烁。显示秒数限制在 0 至房间行动时长之间；倒计时仅用于展示，不能替代服务器行动计时。加注输入明确标注本轮累计总额及最低/最高金额，普通加注要求整数且在合法区间内；弹窗确认全下显示将投入的剩余筹码；行动令牌或连接变化会关闭加注弹窗，避免提交过期金额。

公共牌、底池与本人底牌保持视觉优先级；头像触控区域至少 48px，辅助文字至少 14px。九人手机桌使用独立的成对座位位置并增加纵向间距，公开的对手底牌显示紧凑的点数和花色；手机底牌位于固定底栏的紧凑状态行；ResizeObserver 根据底栏实际高度给牌桌页预留底部空间，滚到底时本人座位、筹码及牌型不被遮挡。桌面手牌位于头像外侧，公共牌宽度随可用空间调整，座位与定向 Emoji 共用位置计算。

### 房主管理与邀请

房主设置弹窗可查看并调整房间设置，针对已入座玩家设置筹码总额、移出其他玩家。前端限制这些操作在两手之间执行；不能移出自己。房主管理最终依赖服务端身份及当前牌局状态校验。

牌桌顶栏连接行显示“公开”或“私人”。房主设置提供房间可见性选择器，在两手之间修改；切换后更新所有成员的标记，大厅随后轮询更新。私人房间不在大厅显示，持链接的用户登录后可加入；切换不撤销已有链接或移除成员。

顶栏分享按钮复制当前牌桌链接，公开和私人房间共用该入口；成功短暂显示“链接已复制”。剪贴板不可用时打开只读链接弹窗供手动复制。该弹窗、玩法说明、买入、房间设置和 Emoji 选择器均不是独立路由。

## 权限 状态与错误处理

| 状态/角色 | 现有行为 |
| --- | --- |
| 非房主 | 不显示房间设置与开始下一手入口；无法通过接口绕过服务端权限 |
| 旁观者 | 可观看公共状态并按空位入座；文字/互动受系统与房间开关控制，语音另受服务端名单约束 |
| 未轮到自己、已弃牌或 All-in | 展示等待／结果提示，四动作保持显示并禁用 |
| 正在行动 | 高亮当前座位与倒计时；剩余时间较少时使用紧急视觉状态 |
| 无网络连接 | 显示“重新连接中”，多数需要发送请求的操作禁用；发送保护提示等待恢复 |
| 普通 WebSocket 关闭 | 以 1 秒起始指数退避重试，上限 10 秒；成功后恢复连接状态 |
| 被房主移出，关闭码 4003 | 显示服务器理由，返回大厅，不自动重连该牌桌 |
| 初始房间请求失败 | 显示“无法进入这张牌桌”、全局错误及返回大厅入口 |
| 服务器拒绝动作/设置 | 全局错误提示；状态以随后的服务端快照为准 |
| 名称或头像更新 | 读取新用户后重建牌桌连接，确保房间成员展示刷新；不同于产品代码热更新 |
| 页面清理 | 关闭 socket、重试和倒计时；媒体模块销毁连接并停止麦克风 |

超时自动过牌或弃牌、房主迁移和离线席位清理由后端负责；前端没有对应的自结算或自迁移逻辑。完整可回放的牌局历史界面尚未实现。

## 验收场景

| 编号 | 场景与预期 | 现有验证入口 |
| --- | --- | --- |
| TABLE-AC01 | 两个独立会话创建、进入同一桌、买入、房主开局，双方只收到应见底牌 | [scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py)、[scripts/smoke.py](https://github.com/li-sky/river-code/blob/main/scripts/smoke.py)；私牌也由服务端测试验证 |
| TABLE-AC02 | 完整行动、All-in、边池和分池由服务器完成，显示正确筹码与结果 | [scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py)、[scripts/smoke.py](https://github.com/li-sky/river-code/blob/main/scripts/smoke.py)、[backend/internal/poker/engine_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/poker/engine_test.go) |
| TABLE-AC03 | 无权管理、短全下未重新开放加注、过期或重复行动令牌不能改变下一轮状态 | [backend/internal/server/server_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server_test.go)、[backend/internal/poker/engine_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/poker/engine_test.go) 及前端合法按钮逻辑 |
| TABLE-AC04 | 超时、断线和进程重启后保持底牌、筹码、截止时间与动作合法性 | [scripts/smoke.py](https://github.com/li-sky/river-code/blob/main/scripts/smoke.py)、[scripts/recovery_check.py](https://github.com/li-sky/river-code/blob/main/scripts/recovery_check.py) |
| TABLE-AC05 | 房主两手间修改盲注/筹码；移出后目标返回大厅，语音随之清理 | [scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py)、[backend/internal/server/server_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server_test.go) |
| TABLE-AC06 | 九名真实玩家入座，桌面、平板和手机无横向溢出或头像相交，手机底牌清楚可见 | [scripts/table_layout_check.py](https://github.com/li-sky/river-code/blob/main/scripts/table_layout_check.py)；卡牌可读性还应人工核查截图 |
| TABLE-AC07 | 双端聊天气泡、头像 Emoji 更新、定向互动可见；用户音效设置不覆盖 Emoji | [scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py) |
| TABLE-AC08 | 系统与房间开启语音后，九端各连接八名成员；退出、移出、刷新清理并可重新加入 | [scripts/table_layout_check.py](https://github.com/li-sky/river-code/blob/main/scripts/table_layout_check.py) 的完整语音模式、[scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py)、媒体单元测试 |
| TABLE-AC09 | 首次房间请求失败、被移出和普通断线分别显示适当处理 | 4003 路径有主流程覆盖；首次失败与持续弱网应补充专项场景 |
| TABLE-AC10 | 翻牌至河牌更新本人牌型，摊牌后显示公开对手，弃牌和换手清除；手机底牌区与座位结果一致且不被操作区遮挡 | `backend/internal/poker/current_hand_test.go`；本次独立双人服务及桌面、390px、320px 浏览器验收记录见 [当前牌型计划](../plans/current-hand-rank.md) |

仓库 [docs/VERIFICATION.md](https://github.com/li-sky/river-code/blob/main/docs/VERIFICATION.md) 记录既有执行结果；验收表不表示每次文档更新都重新执行了该场景。语音跨公网网络、真实 TURN 和人的听感仍需部署验证。

## 实现与测试相对路径

### 房主置顶聊天消息

聊天面板标题下固定显示每桌唯一置顶消息，包含发送者、原文及原发送时间，独立于消息列表滚动。房主可在消息行点击置顶、替换或取消，也可从置顶区取消；其他成员只能读取。按钮由当前 `hostId` 决定，断线时禁用；服务端仍验证权限。手机聊天图标提供“牌桌聊天”可读名称，长置顶正文在有界区域内滚动，保留聊天输入区。聊天功能关闭时隐藏面板、保留置顶数据。

双浏览器验证入口：[scripts/pin_check.cjs](https://github.com/li-sky/river-code/blob/main/scripts/pin_check.cjs)。规格、代码基线与实际证据见 [置顶计划](../plans/host-pin-message.md)。

路径均相对于 `仓库根目录`。

| 路径 | 职责 |
| --- | --- |
| [frontend/src/App.tsx](https://github.com/li-sky/river-code/blob/main/frontend/src/App.tsx) | `Room`、座位、动作、状态消费、倒计时、房主管理及弹窗 |
| [frontend/src/style.css](https://github.com/li-sky/river-code/blob/main/frontend/src/style.css) | 牌桌、卡牌、动画、九人布局、手机底牌和操作区 |
| [frontend/src/lib/types.ts](https://github.com/li-sky/river-code/blob/main/frontend/src/lib/types.ts)、[frontend/src/lib/api.ts](https://github.com/li-sky/river-code/blob/main/frontend/src/lib/api.ts) | 个性化状态类型、HTTP 请求 |
| [frontend/src/lib/voice.ts](https://github.com/li-sky/river-code/blob/main/frontend/src/lib/voice.ts)、[frontend/src/lib/sound.ts](https://github.com/li-sky/river-code/blob/main/frontend/src/lib/sound.ts) | 媒体与音效，见共享模块 |
| [backend/internal/server/server.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server.go)、[backend/internal/server/commands.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/commands.go) | 个性化视图、连接、房主管理、计时、信令与社交事件 |
| [backend/internal/poker/engine.go](https://github.com/li-sky/river-code/blob/main/backend/internal/poker/engine.go)、[backend/internal/poker/engine_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/poker/engine_test.go) | 无网络依赖的规则及结算 |
| [backend/internal/server/server_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server_test.go) | 权限、连接和状态校验 |
| [scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py)、[scripts/table_layout_check.py](https://github.com/li-sky/river-code/blob/main/scripts/table_layout_check.py)、[scripts/smoke.py](https://github.com/li-sky/river-code/blob/main/scripts/smoke.py)、[scripts/recovery_check.py](https://github.com/li-sky/river-code/blob/main/scripts/recovery_check.py) | 实际多人、布局、媒体及恢复验收 |
| [docs/CONTRACT.md](https://github.com/li-sky/river-code/blob/main/docs/CONTRACT.md)、[docs/VERIFICATION.md](https://github.com/li-sky/river-code/blob/main/docs/VERIFICATION.md) | 消息语义与既有结果 |

## 待实现改进与待验证事项

1. 朋友反馈驱动的易用性调整仅是方案。尚无实际反馈条目、反馈入口或反馈优先级管理；应先收集真实操作困难再形成变更。

2. 面向进行中牌局的热更新仅是待设计方案。当前 WebSocket 重连和数据库快照恢复不能证明无中断升级；仍需版本协商、旧新客户端兼容及升级期间行动令牌场景。

3. 行动发出后的等待反馈与令牌去重已实现；完整弱网、长时间无响应和可解释的重试机制仍可进一步验收与设计。

4. 暂无下一手预约入座、完整手牌回放、牌局历史页面和房间设置变更日志；不能把最新快照恢复写成完整历史。

5. 对“公正发牌”的独立可验证机制尚未实现；牌局合法性、私牌隔离和规则测试不等同于密码学公平证明。

6. 牌桌已合并为单层房间顶栏，退出房间显式发送 leave；浏览器历史仍依赖原有断线处理。

## 本次 UI 验收证据

2026-10-01 在隔离的本机 PostgreSQL 与真实房间服务上完成浏览器 UI 验收。入口、大厅、创建与个人设置弹窗检查 320px、390px 手机布局及桌面焦点；九人真实会话在 320、390、601、768、1024、1440px 检查头像、卡牌、筹码标签及触控区域。两人牌局通过延迟服务器响应核查行动等待反馈和恢复，并检查键盘开关、滑块、聊天和弹窗。减少动态效果分支已作 CSS 审阅，本次未运行操作系统偏好切换或屏幕阅读器专项测试。完整条件、范围和检查结果见 [game-ui-readability 计划](../plans/game-ui-readability.md)，这些记录不扩大为 OAuth、真实公网语音或全量历史场景的新验收。

## 文档与代码入口

[项目文档](https://github.com/li-sky/river-spec) · [代码仓库](https://github.com/li-sky/river-code)。前次可读性改进基线为提交 [3fb5101](https://github.com/li-sky/river-code/commit/3fb51017e9594191d01d1e372a663c457217a25c)；后续实现变化需同步此规格和验收证据。

当前可见牌型提示实现基线：`8a2be43d24690b0884749d483d50c9f63a36697e`，验收见 [当前牌型计划](../plans/current-hand-rank.md)。

## 紧凑牌桌 UI 验收

2026-10-01 在隔离的本机内存服务与真实浏览器会话上完成 320、390、768、1440px 检查：顶栏无溢出，四动作底栏固定，左右抽屉、模拟触摸滑动、Escape／焦点恢复、聊天／置顶可用。真实双人牌局核查普通加注、跟注、过牌、弃牌、All-in、短全下及行动更新关闭弹窗；九人会话头像无重叠，本人座位滚到底后不被底栏覆盖。服务端暂离测试覆盖本人范围、保留座位／筹码、当前手不变、下一手排除、快照与保存回滚。详细证据、限制与代码基线见 [紧凑 UI 计划](../plans/compact-table-ui.md)，验收入口为 `scripts/compact_ui_check.cjs` 与 `backend/internal/server/sitout_test.go`。

紧凑牌桌与本人暂离的当前代码基线：[23f4a52](https://github.com/li-sky/river-code/commit/23f4a521d52202e871c1a2e28a3729d7bd7e4938)。
