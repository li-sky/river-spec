# RIVER 用户设置与媒体互动模块规格

- 基线日期：2026-10-01。

- 模块标识：`SHARED`。本模块覆盖三个页面共用的弹窗、用户/房间设置、头像、音效、语音、文字与 Emoji 互动。

- 定位：个人设置、房间设置和互动选择器都是现有页面内的弹窗，**不是独立路由或第四个页面**。创建牌桌同样使用弹窗和共享房间设置字段。

- 术语：配置属于系统；设置属于用户或房间。host 是房主，guest 是加入房间的人；访客身份不意味着旁观者或特殊房间权限。

## 目的

为入口、大厅和牌桌提供一致的交互组件；把用户偏好、房间行为和系统能力边界分开，使头像、声音、语音及社交能力在真实会话中可用。

## 已确认需求

| 编号 | 需求 | 当前落实方式 |
| --- | --- | --- |
| SHARED-R01 | 用户可上传头像或使用公共头像服务 | 个人设置支持上传及 Gravatar 邮箱，登录身份也可携带自己的已有头像 |
| SHARED-R02 | 该属于用户的设置由用户调整 | 昵称、头像、音效、音量、语音静音和头像 Emoji 属于用户；房间不覆盖这些偏好 |
| SHARED-R03 | 语音相关能力放在系统配置与单局设置中 | 系统功能许可与默认模式、房间语音开关与模式、旁观者许可共同约束；用户可在当前语音会话临时切换模式 |
| SHARED-R04 | 良好的发牌和筹码音效 | 浏览器合成发牌、筹码、弃牌、获胜和 reaction 提示音 |
| SHARED-R05 | 语音聊天、定向反应、自身头像表情和文字气泡 | WebRTC 实时媒体；房间 WebSocket 驱动消息、反应及头像更新 |
| SHARED-R06 | 手机、平板和电脑均可操作 | 响应式弹窗、两侧抽屉、固定牌桌底栏及指针控制的按住说话 |
| SHARED-R07 | 尽可能复用公共组件 | Radix Dialog/Switch、Lucide 图标、emoji-picker-react 完整表情选择器；原生样式与合成音效承担游戏表现 |

## 现有行为

### 组件边界

`Modal` 包装 Radix Dialog，包含遮罩、标题、描述和关闭入口。`Toggle` 包装 Radix Switch，提供与可见字段相同的无障碍名称；`Button`、`Avatar` 和 `Card` 共用。弹窗在屏幕内限制宽度与高度，较长内容内部滚动，布局考虑 safe-area。主要按钮、开关、输入、滑块与上传入口的操作区域至少 48px；紧凑牌桌顶栏图标至少 44px，辅助文字至少 14px、表单文字至少 16px；按钮和输入提供明确的键盘焦点描边。

`Drawer` 同样包装 Radix Dialog，左侧用于牌桌工具、右侧用于聊天；遮罩、焦点约束、Escape、关闭后焦点恢复共用 Dialog 行为。抽屉宽度有界、覆盖屏幕高度，保持聊天输入和置顶区可见。房间页非控件区域（包含页面中部和边缘）向右滑打开左菜单、向左滑打开右聊天。Pointer Events 统一触摸与鼠标拖动，水平触控板输入也支持；抽屉只保存一个互斥状态。抽屉打开后，菜单左滑／聊天右滑仅关闭当前抽屉，不转而打开另一侧。短划、纵向滚动、取消、多指与输入／按钮／滑块不触发。水平指针手势超过 60px 且水平位移大于纵向 1.5 倍才提交，一次手势最多一次；轴向在初始移动后锁定，保留纵向滚动。触控板连续事件消费后忽略惯性，250ms 无事件才开始下一次识别。聊天关闭时清理聊天抽屉状态。验证范围见 [抽屉手势修复计划](../plans/drawer-gesture-conflicts.md)。

减少动态效果偏好会缩短一般动画、移除行动计时的持续闪烁；定向 Emoji 保留目标位置的静态反馈而不是在取消动画后消失。聊天开关声明展开状态与受控面板，Enter 继续发送文字。短动画用于状态变化，不增加媒体、消息或手柄输入协议。

当前不是一个独立发布的组件库，业务状态仍在 `App`、`Profile` 和 `Room` 内。媒体逻辑分成 `lib/sound.ts` 和 `lib/voice.ts`，共享数据类型位于 `lib/types.ts`。

### 系统配置 用户设置与房间设置

| 层级 | 字段或行为 | 调整入口与限制 |
| --- | --- | --- |
| 系统配置 | `guestEnabled`、`githubEnabled`、`passwordRequired` | 前端只读取 `/api/config`，没有系统配置编辑页面 |
| 系统配置 | `voiceEnabled`、`chatEnabled`、`reactionsEnabled` | 全站能力许可；房间不能绕过关闭状态 |
| 系统配置 | `defaultVoiceMode`、`spectatorVoiceEnabled`、`iceServers` | 语音默认行为、旁观者上限权限与网络连接参数；前端不会显示认证密钥 |
| 用户设置 | `soundEnabled`、`volume` | 个人设置及牌桌音效按钮；个人音量范围 0–1 |
| 用户设置 | `voiceMuted` | 牌桌麦克风按钮保存静音偏好 |
| 用户设置 | `avatarEmoji` | 牌桌自身 Emoji 选择器发送消息并由服务端保存 |
| 用户资料 | 昵称、上传头像、Gravatar 头像 | 顶部头像打开个人设置弹窗 |
| 房间设置 | `visibility`（公开／私人） | 共享 `SettingsFields` 选择器；默认公开，在大厅显示。私人不在大厅显示，持邀请链接的认证用户可加入；房主在两手之间切换 |
| 房间设置 | 盲注、默认买入、座位数、行动时间 | 创建弹窗或房主房间设置弹窗；已有牌桌两手之间修改 |
| 房间设置 | 语音开关、默认语音模式、旁观者语音、文字聊天和 Emoji 互动 | 共享 `SettingsFields`；功能受系统配置上限限制 |
| 临时用户操作 | 当前语音模式、关闭语音播放、按住说话 | 当前语音会话本地行为；目前不属于完整持久化用户设置字段 |

### 个人设置与头像

已登录用户可从顶部昵称/头像进入个人设置。开启时从当前用户读取昵称、音效开关和音量。修改声音会立即预览；关闭未保存弹窗会恢复已保存的音效开关和音量。

点击“保存设置”后 `PATCH /api/me` 提交昵称、可选 Gravatar 邮箱及本次需要修改的声音字段，再读取 `/api/me` 并关闭弹窗。声音或静音更新只提交目标设置字段，不传播旧 `avatarEmoji` 覆盖新表情。

上传入口接受 PNG、JPEG 和 GIF，使用 multipart 的 `file` 提交 `/api/me/avatar`。**上传成功立即保存并刷新用户**，不必等“保存设置”，取消弹窗不会撤销已上传头像；这与声音预览不同。后台上传及格式标准化的验证由身份模块负责。头像加载失败时保留昵称首字母/首字符占位。

填写非空 Gravatar 邮箱后，保存动作会请求服务器使用该头像来源；输入为空时本次保存不改变头像来源。前端没有独立的“删除头像”动作，也没有单独持久化的头像来源切换面板。牌桌内昵称或头像 URL 变化会重建连接以刷新成员展示。

### 游戏音效

`setSoundSettings` 维护本地开关和音量。页面指针操作调用 `unlockAudio`，尝试解锁浏览器 AudioContext。`playSound` 使用振荡器和带通噪声合成提示：

| 事件 | 用途 |
| --- | --- |
| `deal` | 发牌/牌面动作的纸牌提示 |
| `chips` | 筹码动作的短促叠落提示 |
| `fold` | 弃牌提示 |
| `win` | 本手获胜/结算提示 |
| `reaction` | 定向 Emoji 的轻量反馈 |

服务器的 `sound` 消息驱动游戏提示；定向反应事件在本地播放 reaction 音。相同类型提示在 70 毫秒内做去重；关闭、音量为零或 AudioContext 尚未运行时不播放。音效资源由浏览器合成，不依赖远程音频下载。当前没有背景音乐功能，也没有人的主观听感已完成验证的结论。

### WebRTC 语音

`useVoice` 封装 `VoiceSession`。只有系统与房间语音均启用，且当前用户在服务器 `voiceParticipantIds` 名单内，前端才允许加入。名单最多 9 人；服务端优先安排已连接的入座玩家，然后按许可安排旁观者。此名单表示获准参与者，不是一个按“已点击加入语音”统计的动态听众列表。

用户点击“加入语音”才请求麦克风权限。默认静音行为取用户 `voiceMuted`，初始默认偏好为静音。加入后可：

1. 切换麦克风，更新用户静音设置。

2. 选择自由说话或按住说话。房间模式提供默认值，当前用户可临时改自己的模式。

3. 在按住说话模式下按住按钮发言；明确按下时若静音会临时解除，松开、取消指针捕获、失去焦点或页面隐藏时停止发言。

4. 使用耳机按钮关闭/恢复本地远端播放，不修改其他人的麦克风。

5. 退出语音并释放麦克风、远端音频元素和连接。

媒体在浏览器之间传输；WebSocket 仅路由信令。每端最多八条对端连接，创建远端 audio 元素接收媒体。首次 offer 由固定身份顺序选出的发起方生成，后续继续处理协商冲突；提前到达的 ICE 候选会排队等待远端描述。当前未提供录音、服务端混音或通话历史。

### 文字 定向 Emoji 与自身表情

- 房主可置顶或替换本桌已有聊天消息，每桌同时一条；房主和其他成员均可在聊天顶部读取，只有当前房主可取消。置顶独立于聊天历史裁剪并保存在房间快照，作者离开/房主移交后仍存在。系统和房间聊天同时开启才可管理，关闭功能保留置顶数据。长正文区域可滚动，断线禁用管理按钮；消息仍作为 React 文本呈现。双浏览器与权限边界证据见 [置顶计划](../plans/host-pin-message.md)。

- 文字聊天需要系统与房间都允许；提交去掉首尾空白，最多 300 个前端字符。面板展示服务端消息、发送者和时间，Enter 发送。未显示聊天面板时仍可在已显示的头像旁呈现新消息气泡。

- 收到新文字或变化后的非空头像 Emoji，会显示约 5 秒思考气泡；气泡替换旧内容并重设计时器。未入座成员没有牌桌座位头像，不能据此承诺其气泡出现在牌桌上。

- 点击其他玩家头像打开定向 Emoji 选择器，向指定成员发送 reaction。动画使用实际牌桌尺寸，并保持目标头像的相对位置。

- 点击自己的座位头像或可用的自身表情入口，选择挂在头像旁的 Emoji；支持清除。自身头像与定向反应共用按需加载的 `emoji-picker-react` 选择器，提供中文搜索、全部分类（含旗帜）、肤色和最近使用，数据随构建提供，发送原始 Unicode。覆盖所安装组件的数据集，字体/系统版本可能影响新表情及旗帜的显示；不能任意上传。

- 系统或房间关闭互动、连接断开时，已打开的选择器显示对应状态，不呈现可选 Emoji，头像清除按钮禁用。恢复权限或连接后选择器可用。身份保存和房间命令均允许最多 16 个码点/64 字节，组合 Emoji 不被拆分。

- 服务器决定互动许可、限流与保存结果；前端 React 文本展示不是 HTML 消息编辑器。

## 权限 状态与错误处理

| 状态 | 现有行为 |
| --- | --- |
| 未登录 | 没有个人设置入口；不请求麦克风 |
| 非房主 | 无房间设置入口；不能调整别人的筹码 |
| 系统关闭功能 | 不允许房间重新开启；实际发送消息也由后端检查 |
| 旁观者语音未获许可 | 显示“入座后语音”，按钮禁用 |
| 获许可但不在九人名单内 | 显示“语音已满（9 人）”和上限提示 |
| 麦克风权限拒绝、无设备、设备占用 | 保持未加入并显示相应可理解的错误 |
| 非安全上下文或不支持 WebRTC | 提示需要 HTTPS/localhost 及兼容浏览器 |
| 浏览器暂停远端音频播放 | 显示错误并提供“重试播放”用户动作 |
| 部分语音连接失败 | ICE 有限次数恢复，后续提示重新加入或部署 TURN；不宣称所有网络可直连 |
| 语音权限撤销/名单移除/离开房间 | 清理连接与本地麦克风，正在授权时迟到的媒体也停止 |
| 上传或保存失败 | 显示全局错误，保存按钮恢复可用；不会把请求失败写成已保存 |
| WS 拒绝消息 | 显示服务端错误；消息、设置或 Emoji 的权威状态仍由后续快照给出 |

头像上传和 Gravatar 涉及不同的网络来源，但当前并无独立的隐私选择面板。

## 验收场景

| 编号 | 场景与预期 | 现有验证入口 |
| --- | --- | --- |
| SHARED-AC01 | 保存昵称、声音和音量；刷新后保留；只更新声音不会覆盖头像 Emoji | [scripts/profile_check.py](https://github.com/li-sky/river-code/blob/main/scripts/profile_check.py)、[scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py) |
| SHARED-AC02 | 上传合法头像后立即更新，服务返回标准化图片；失败显示错误 | [scripts/profile_check.py](https://github.com/li-sky/river-code/blob/main/scripts/profile_check.py)、身份模块测试；取消上传后的保存边界需人工验收 |
| SHARED-AC03 | 未保存的声音预览关闭后恢复；禁用音效或音量为零无声 | 依据 `Profile` 和 `sound.ts`；音效与取消分支需补充专项验收 |
| SHARED-AC04 | 默认静音加入、按住发声/松开停声、关闭播放、退出清理真实媒体 | [frontend/src/lib/voice.test.mjs](https://github.com/li-sky/river-code/blob/main/frontend/src/lib/voice.test.mjs)、[scripts/test-media.sh](https://github.com/li-sky/river-code/blob/main/scripts/test-media.sh) |
| SHARED-AC05 | 语音权限关闭时不请求麦克风；权限请求未完成就关闭也停止迟到音轨 | 媒体单元测试 |
| SHARED-AC06 | 初始协商选出唯一发起方、后续 offer 冲突处理、早到 ICE 排队 | 媒体单元测试；真实九端浏览器验收补充真实连接证据 |
| SHARED-AC07 | 九端语音，每端八条已连接对端及八路接收音轨；超过名单者不发送信令 | [scripts/table_layout_check.py](https://github.com/li-sky/river-code/blob/main/scripts/table_layout_check.py) 的完整语音模式、服务端权限测试 |
| SHARED-AC08 | 聊天在另一端出现气泡；头像 Emoji 更新及定向反应可见；移出清理语音 | [scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py) |
| SHARED-AC09 | 麦克风拒绝、断线、退出/重入、刷新后重新加入有合理状态 | 媒体单元测试与 [scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py) |
| SHARED-AC10 | 真实域名 HTTPS、不同网络 TURN 连接及声音体验达到要求 | 仍待部署环境和人工验证，不能由本机模拟麦克风验收代替 |
| SHARED-AC11 | 中文搜索、分类、肤色、电脑/手机布局、两端定向反应、复杂头像刷新/清除与关闭/断线禁用 | [scripts/emoji_check.cjs](https://github.com/li-sky/river-code/blob/main/scripts/emoji_check.cjs)、`TestEmojiSequencesAndLimits`；本次实际证据见 [完整 Emoji 计划](../plans/all-emoji.md) |

[docs/VERIFICATION.md](https://github.com/li-sky/river-code/blob/main/docs/VERIFICATION.md) 提供已执行检查的历史记录。各验收表描述源码覆盖及验证入口，运行结果以对应验证记录为准。

## 实现与测试相对路径

路径均相对于 `仓库根目录`。

| 路径 | 职责 |
| --- | --- |
| [frontend/src/App.tsx](https://github.com/li-sky/river-code/blob/main/frontend/src/App.tsx) | 共享组件、`Profile`、`SettingsFields`、媒体/聊天/Emoji 入口及状态桥接 |
| [frontend/src/components/EmojiPicker.tsx](https://github.com/li-sky/river-code/blob/main/frontend/src/components/EmojiPicker.tsx) | 按需加载的中文完整表情选择器，保留所选混合肤色的原始 Unicode 序列 |
| [frontend/src/lib/types.ts](https://github.com/li-sky/river-code/blob/main/frontend/src/lib/types.ts) | 系统配置、用户设置、房间设置和语音名单类型 |
| [frontend/src/lib/api.ts](https://github.com/li-sky/river-code/blob/main/frontend/src/lib/api.ts) | 局部用户更新、multipart 上传及错误解析 |
| [frontend/src/lib/sound.ts](https://github.com/li-sky/river-code/blob/main/frontend/src/lib/sound.ts) | 本地合成音效、音量、去重和资源清理 |
| [frontend/src/lib/voice.ts](https://github.com/li-sky/river-code/blob/main/frontend/src/lib/voice.ts) | WebRTC 会话、协商、媒体清理及 hook |
| [frontend/src/lib/voice.test.mjs](https://github.com/li-sky/river-code/blob/main/frontend/src/lib/voice.test.mjs)、[scripts/test-media.sh](https://github.com/li-sky/river-code/blob/main/scripts/test-media.sh) | 七项生命周期与信令测试及执行脚本 |
| [frontend/src/style.css](https://github.com/li-sky/river-code/blob/main/frontend/src/style.css) | 弹窗、Switch、头像、气泡、聊天、语音与动态效果 |
| [backend/internal/identity/identity.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/identity.go)、[backend/internal/identity/identity_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/identity_test.go) | 用户设置、头像、会话及身份测试 |
| [backend/internal/server/server.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server.go)、[backend/internal/server/commands.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/commands.go)、[backend/internal/server/server_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server_test.go) | 名单、房间许可、信令、互动和权限测试 |
| [scripts/profile_check.py](https://github.com/li-sky/river-code/blob/main/scripts/profile_check.py)、[scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py)、[scripts/table_layout_check.py](https://github.com/li-sky/river-code/blob/main/scripts/table_layout_check.py) | 真实账号、互动、布局及语音验收 |
| [docs/CONTRACT.md](https://github.com/li-sky/river-code/blob/main/docs/CONTRACT.md)、[docs/CREDITS.md](https://github.com/li-sky/river-code/blob/main/docs/CREDITS.md)、[docs/VERIFICATION.md](https://github.com/li-sky/river-code/blob/main/docs/VERIFICATION.md) | 契约、组件素材来源和既有验证记录 |

## 待实现改进与待验证事项

1. 朋友对声音、表情、手机输入及语音体验的反馈收集与问题闭环仅是方案；没有已收集反馈或已实现反馈页面。本基线不虚构主观听感结论。

2. 面向进行中牌局和语音连接的热更新仅属待设计方案；尚需定义升级后设备授权、媒体清理/重建和用户设置兼容性。当前重连机制不是热更新实现证明。

3. 音效目前没有独立自动化听感验收；可后续增加可重复音效预览与人工评价。是否增加背景音乐仍需确认。

4. 语音模式和关闭播放偏好目前为临时会话操作，尚未完整持久化到用户设置；未来若新增，应明确默认房间模式与个人偏好的优先级。

5. 语音名单按连接和座位资格排列，尚未按实际加入者动态回收空闲名额；可评估大规模旁观场景是否需要独立的语音加入登记。

6. 个人设置上传为立即保存、声音为确认保存，交互边界不同；可考虑更明确的保存提示和头像来源选择，当前不具有统一撤销事务。

7. 缺少针对键盘、屏幕阅读器、移动软键盘与气泡遮挡的完整专项验收；复用 Radix 不能替代整个产品的无障碍验证。

## 本次 UI 验收证据

2026-10-01 在隔离的本机 PostgreSQL 与真实房间服务上完成浏览器 UI 验收。入口、大厅、创建与个人设置弹窗检查 320px、390px 手机布局及桌面焦点；九人真实会话在 320、390、601、768、1024、1440px 检查头像、卡牌、筹码标签及触控区域。两人牌局通过延迟服务器响应核查行动等待反馈和恢复，并检查键盘开关、滑块、聊天和弹窗。减少动态效果分支已作 CSS 审阅，本次未运行操作系统偏好切换或屏幕阅读器专项测试。完整条件、范围和检查结果见 [game-ui-readability 计划](../plans/game-ui-readability.md)，这些记录不扩大为 OAuth、真实公网语音或全量历史场景的新验收。

## 文档与代码入口

[项目文档](https://github.com/li-sky/river-spec) · [代码仓库](https://github.com/li-sky/river-code)。前次可读性改进基线为提交 [3fb5101](https://github.com/li-sky/river-code/commit/3fb51017e9594191d01d1e372a663c457217a25c)；后续实现变化需同步此规格和验收证据。

完整 Emoji 选择器与组合头像保存的实现基线为代码提交 `0e8d22b6a6708aaf0777586a8bee305ce8b4f7da`；开发验收见 [完整 Emoji 计划](../plans/all-emoji.md)，已集成本地主线，未发布。

紧凑顶栏、左右抽屉、移动聊天／置顶和 Raise 金额弹窗的当前实现与真实浏览器证据见 [紧凑 UI 计划](../plans/compact-table-ui.md)。本次移动了语音入口，未修改信令或媒体生命周期，也未重新宣称公网语音验收。

紧凑牌桌与本人暂离的当前代码基线：[23f4a52](https://github.com/li-sky/river-code/commit/23f4a521d52202e871c1a2e28a3729d7bd7e4938)。

页面中部与互斥抽屉手势代码基线：[f91654c](https://github.com/li-sky/river-code/commit/f91654cc41b4d590e7b25e82097a93fd5e3e98b3)，验收见 [手势修复计划](../plans/drawer-gesture-conflicts.md)。
