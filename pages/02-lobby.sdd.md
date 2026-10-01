# RIVER 大厅页规格

- 基线日期：2026-10-01。

- 页面标识：`LOBBY`；已登录且没有 `room` 参数时，由同一个 `App` 在 `/` 显示大厅。

- 术语：配置属于系统；设置属于用户或房间。host 是房主，guest 是加入房间的人，访客是临时身份。

## 目的

展示当前可进入的真实牌桌，让用户选择牌桌或创建自己的现金桌；无牌桌时提供明确的首次创建入口。

## 已确认需求

| 编号 | 需求 | 当前落实方式 |
| --- | --- | --- |
| LOBBY-R01 | 多人无限注德州扑克现金桌 | 列出真实服务端房间摘要；支持创建多张牌桌，每桌 2–9 个座位 |
| LOBBY-R02 | host 为房主，guest 为进入房间的人 | 创建房间的人获得房主身份；账号类型不决定房间角色 |
| LOBBY-R03 | 房主能够开房并设置默认盲注和筹码 | 创建弹窗提供房间设置；实际玩家手上筹码在牌桌内由房主调整 |
| LOBBY-R04 | 系统配置控制全站能力，用户选择自己的设置 | 创建设置受系统功能开关约束；顶部个人设置入口独立于房间设置 |
| LOBBY-R05 | 游戏 UI 与多端支持 | 深色卡片、示意牌桌、状态标签及空态引导；响应式房间卡片网格 |

“无限注”指下注规则，不意味着一张牌桌座位无限、筹码余额无限或支持真实资金。

## 现有行为

2026-10-01 主线已集成立体按钮与手机触觉分支，代码合并基线 `5b1751db96b1b5a53fe7b8b2867c2668971dd0e5`；分支验收记录保留，合并后的兼容性与检查证据见 [集成计划](../plans/merge-duolingo-buttons.md)。

### Duolingo 风格按钮

创建牌桌、空态创建与弹窗提交采用鲜绿色圆角立体按钮，房间卡片采用 20px 圆角与 6px 实色底边；顶部个人设置和常用图标也有一致的下压反馈。按钮阴影与 transform 不改变布局尺寸。代码基线 `dd28cdb7afc49626006b075655ef6028cbe28ff6`；本次桌面、390px、320px 大厅、真实房间卡片及创建流程验收见 [按钮风格计划](../plans/duolingo-buttons.md)。

### 房间列表

建立会话并处于大厅时，立即请求 `GET /api/rooms`，之后每 5 秒刷新；进入牌桌或离开当前组件状态后停止对应轮询。服务端仅返回公开房间，私人房间对房主自己的大厅也隐藏。页面以“公开牌桌”展示公开房间数量，并为每张房间卡片显示名称、盲注、已入座人数/座位数、默认买入和状态。私人房间通过邀请链接进入。

服务端摘要 `status` 为 `playing` 时显示“牌局进行中”，其他状态显示“等待入座”。卡片上的固定装饰牌组用于视觉展示，不是该房间的公共牌或底牌，也不是模拟对战数据。

点击房间卡片后更新地址为 `/?room=<房间 ID>`，进入牌桌流程；大厅点击不会自动坐下。没有牌桌时展示“好牌局，从第一张桌开始”和“创建第一张牌桌”，不插入示例房间。

### 创建牌桌

“创建牌桌”和空态按钮打开同一 Radix Dialog 弹窗，不是独立路由。提交 `POST /api/rooms {name, settings}`，成功后关闭弹窗并进入返回的房间 ID。

| 房间设置项 | 初始值/来源 | 前端限制 |
| --- | --- | --- |
| 牌桌名称 | 初始为空 | 必填，最多 50 个前端字符 |
| 房间可见性 | `public`（公开房间） | 公开房间在大厅显示；`private`（私人房间）只通过链接加入，持链接者登录后可进入 |
| 小盲注 | 10 | 1–500,000 |
| 大盲注 | 20 | 至少为小盲的 2 倍，最多 1,000,000 |
| 默认买入筹码 | 2,000 | 至少为大盲的 2 倍，最多 1,000,000,000 |
| 座位数 | 6 | 2–9 |
| 行动时间 | 30 秒 | 10–120 秒 |
| 语音、文字聊天、Emoji 互动 | 前端初始房间设置均为开启 | 系统配置关闭的能力不能通过房间设置启用 |
| 默认语音模式 | 系统配置 `defaultVoiceMode`，缺省使用 `free` | 自由说话或按住说话 |
| 允许旁观者加入语音 | 关闭 | 同时受系统旁观者语音权限和房间语音开关约束 |

这些初始值来源于当前前端代码，不代表已有按 host/guest 分类的持久化默认房间模板。创建表单状态在当前 `App` 生命周期内保留；重新加载后重新初始化。全站加入密码由系统配置提供，创建弹窗不提供每房间密码。

## 权限 状态与错误处理

大厅沿用深色绿毡，创建主操作采用鲜绿色立体按钮，保留装饰金色，突出创建入口、盲注和入座状态。房间卡片与顶部个人设置按钮使用至少 48px 的交互目标，正文至少 16px、辅助文字至少 14px；装饰牌桌不进入无障碍树。窄屏采用单列卡片，创建表单在 320px 宽度下使用单列字段与可滚动弹窗。

| 条件或状态 | 现有行为 |
| --- | --- |
| 未建立会话 | 不渲染大厅，显示入口 |
| 已建立会话 | 显示创建牌桌入口；是否可创建及请求内容合法性仍由服务端校验 |
| 房间列表为空 | 展示空态和首次创建按钮 |
| 房间列表请求失败 | 显示全局错误提示；已有房间列表保留，后续轮询继续；首次失败时默认空列表仍可能呈现空态 |
| 正在创建 | 提交按钮禁用；成功进入新牌桌，失败保留弹窗并显示错误 |
| 系统配置关闭媒体/互动 | 对应设置开关禁用；真正使用时还要通过系统配置和服务端授权 |
| 用户个人设置 | 顶部头像入口打开个人设置弹窗，改变用户偏好而不是修改房间 |
| 退出登录 | 请求注销会话，成功后回到入口 |

创建弹窗的字段校验不能替代服务端检查。房间名称和聊天内容通过 React 文本渲染。大厅不负责规则判定、发牌或结算。

## 验收场景

| 编号 | 场景与预期 | 现有验证入口 |
| --- | --- | --- |
| LOBBY-AC01 | 无牌桌时展示空态；不显示假房间 | 根据当前空列表分支进行隔离数据库专项验收 |
| LOBBY-AC02 | 创建真实牌桌后进入其 URL，其他会话可通过链接进入 | [scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py)、[scripts/smoke.py](https://github.com/li-sky/river-code/blob/main/scripts/smoke.py) |
| LOBBY-AC03 | 盲注、买入、座位和行动时间非法时拒绝创建 | HTML 限制与 [backend/internal/server/server_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server_test.go)；补充创建表单边界浏览器场景 |
| LOBBY-AC04 | 第二个用户创建/修改房间后，大厅在后续轮询中显示最新摘要 | 依据 5 秒轮询逻辑补充浏览器验收 |
| LOBBY-AC05 | 用户进入牌桌后轮询停止；返回大厅恢复轮询 | 当前 effect 生命周期逻辑；需补充网络请求级验收 |
| LOBBY-AC06 | 手机单列、较宽设备多列，无横向溢出，创建弹窗可以提交 | [scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py) 覆盖登录后大厅宽度与创建流程 |
| LOBBY-AC07 | 系统配置关闭聊天、语音或互动时，创建设置不能恢复该能力 | 系统/房间权限测试及专项浏览器场景；不能仅凭开关禁用判断服务端安全 |

现有执行结果由 [docs/VERIFICATION.md](https://github.com/li-sky/river-code/blob/main/docs/VERIFICATION.md) 提供，以上未标为本次新测试。

## 实现与测试相对路径

路径均相对于 `仓库根目录`。

| 路径 | 职责 |
| --- | --- |
| [frontend/src/App.tsx](https://github.com/li-sky/river-code/blob/main/frontend/src/App.tsx) | 大厅、房间轮询、创建弹窗、`SettingsFields`、URL 切换 |
| [frontend/src/style.css](https://github.com/li-sky/river-code/blob/main/frontend/src/style.css) | 房间卡片、空态、弹窗及响应式网格 |
| [frontend/src/lib/api.ts](https://github.com/li-sky/river-code/blob/main/frontend/src/lib/api.ts)、[frontend/src/lib/types.ts](https://github.com/li-sky/river-code/blob/main/frontend/src/lib/types.ts) | 房间摘要、房间设置与 HTTP 请求 |
| [backend/internal/server/server.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server.go) | 房间列表、创建及设置合法性检查 |
| [backend/internal/server/server_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server_test.go) | 服务端房间行为与权限测试 |
| [scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py)、[scripts/smoke.py](https://github.com/li-sky/river-code/blob/main/scripts/smoke.py) | 创建、加入等真实服务验收 |
| [docs/CONTRACT.md](https://github.com/li-sky/river-code/blob/main/docs/CONTRACT.md)、[docs/VERIFICATION.md](https://github.com/li-sky/river-code/blob/main/docs/VERIFICATION.md) | 契约及既有结果 |

## 待实现改进与待验证事项

1. 增加首次加载、列表错误和真正空大厅的不同状态；当前首次请求失败与空列表的视觉状态可能相同。

2. 大厅尚无搜索、筛选、分页和永久房间收藏；是否需要取决于实际房间数量。

3. 创建默认值尚未形成按用户保存的房间模板；host/guest 默认权限由当前服务端角色规则提供，不应写成已有完整的模板管理界面。

4. 朋友试用反馈收集、房间发现体验评审及反馈驱动的改进排序仅是后续方案，当前没有已收集反馈或产品内反馈渠道。

5. 保持进行中牌局的热更新、版本公告与升级提示仅属待设计方案；5 秒轮询和房间设置广播不是产品热更新能力。

## 本次 UI 验收证据

2026-10-01 在隔离的本机 PostgreSQL 与真实房间服务上完成浏览器 UI 验收。入口、大厅、创建与个人设置弹窗检查 320px、390px 手机布局及桌面焦点；九人真实会话在 320、390、601、768、1024、1440px 检查头像、卡牌、筹码标签及触控区域。两人牌局通过延迟服务器响应核查行动等待反馈和恢复，并检查键盘开关、滑块、聊天和弹窗。减少动态效果分支已作 CSS 审阅，本次未运行操作系统偏好切换或屏幕阅读器专项测试。完整条件、范围和检查结果见 [game-ui-readability 计划](../plans/game-ui-readability.md)，这些记录不扩大为 OAuth、真实公网语音或全量历史场景的新验收。

## 文档与代码入口

[项目文档](https://github.com/li-sky/river-spec) · [代码仓库](https://github.com/li-sky/river-code)。当前实现基线为提交 [3fb5101](https://github.com/li-sky/river-code/commit/3fb51017e9594191d01d1e372a663c457217a25c)；后续实现变化需同步此规格和验收证据。
