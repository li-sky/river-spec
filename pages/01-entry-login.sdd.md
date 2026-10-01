# RIVER 入口与登录页规格

- 基线日期：2026-10-01。

- 页面标识：`ENTRY`。未建立会话时显示入口；URL 可为 `/` 或带 `room` 参数的邀请链接。

- 术语：配置属于系统；设置属于用户或房间。host 是房主，guest 是加入房间的人，访客是未使用正式账号的临时身份。访客身份与房间角色不是同一维度。

## 目的

让用户通过访客、自建账号或 GitHub OAuth 建立会话，再进入大厅或邀请指向的牌桌。入口同时介绍无限注德州扑克、朋友聚会和娱乐筹码用途。

## 已确认需求

| 编号 | 需求 | 当前落实方式 |
| --- | --- | --- |
| ENTRY-R01 | 支持访客、自建账号和 GitHub OAuth | 访客、登录、注册三种表单；GitHub 按钮受系统配置控制 |
| ENTRY-R02 | 可通过系统配置要求全站统一加入密码 | 根据 `passwordRequired` 显示全站加入密码输入框；密码由服务端校验 |
| ENTRY-R03 | 手机竖屏，平板和桌面适配 | 同一入口使用响应式布局；手机收起装饰牌组，保留表单 |
| ENTRY-R04 | 漂亮且带游戏 UI 感 | 深色背景、鲜绿色立体操作按钮、原生卡牌展示及 RIVER 品牌元素 |
| ENTRY-R05 | 登录成功后能够实际参与多人牌局 | 使用真实会话接口，成功后读取用户及系统配置，保留当前邀请参数 |

## 现有行为

2026-10-01 主线已集成立体按钮与手机触觉分支，代码合并基线 `5b1751db96b1b5a53fe7b8b2867c2668971dd0e5`；分支验收记录保留，合并后的兼容性与检查证据见 [集成计划](../plans/merge-duolingo-buttons.md)。

### Duolingo 风格按钮

访客、登录、注册的主提交按钮采用鲜绿色、14px 圆角、加粗文字和 4px 实色底边。模式切换项及 GitHub 登录共用立体按钮样式，选中模式使用绿色描边；悬停轻抬、按压下移并收起底边，禁用按钮使用灰色且不位移。保留原有键盘焦点、至少 48px 操作区域及减少动态效果支持。代码基线 `dd28cdb7afc49626006b075655ef6028cbe28ff6`；本次桌面、390px、320px 入口与实际访客登录验收见 [按钮风格计划](../plans/duolingo-buttons.md)。本次未验证真实 GitHub OAuth。

### 路由与初始化

入口、大厅和牌桌由 `App` 条件渲染，没有独立的登录路由或前端路由库。初始化并行读取 `GET /api/config` 和 `GET /api/me`；读取用户失败时按无会话处理。系统配置尚未就绪时显示“正在准备牌桌…”。配置读取失败时显示错误及“重新连接”，按钮会重新加载页面。

无会话时优先显示访客模式；系统配置关闭访客后，默认显示账号登录。`room` 参数在此阶段保留：登录成功且参数存在时进入对应牌桌，否则进入大厅。浏览器前进、后退会重新读取该参数。

### 认证方式

| 方式 | 输入及前端限制 | 请求 |
| --- | --- | --- |
| 访客 | 昵称必填，最多 30 个前端字符；按需填写全站加入密码 | `POST /api/auth/guest`，加入密码使用请求字段 `password` |
| 自建账号登录 | 必填邮箱和账号密码；按需填写全站加入密码 | `POST /api/auth/login`，只提交登录相关字段 |
| 自建账号注册 | 必填昵称、邮箱和账号密码；账号密码至少 8 位；按需填写全站加入密码 | `POST /api/auth/register` |
| GitHub OAuth | 系统配置启用 GitHub 时显示按钮 | 必要时先 `POST /api/auth/access` 校验加入密码，再跳转 `GET /api/auth/github` |

认证成功后重新读取 `/api/me` 和 `/api/config`。账号密码与加入密码用途不同，GitHub 流程不会把加入密码放入跳转 URL。HTTP 使用同源会话 cookie；前端不在本地存储保存密码或会话令牌。

入口装饰牌组属于视觉素材，不表示正在进行的牌局。入口没有头像选择流程，头像与声音偏好在登录后的个人设置弹窗中调整，详见 [共享设置与媒体模块](https://github.com/li-sky/river-spec/blob/main/pages/04-shared-settings-media.sdd.md)。

## 权限 状态与错误处理

入口采用统一的游戏界面排版：正文与表单文字至少 16px，辅助文字至少 14px；按钮、切换项和输入区域至少 48px。访客/登录/注册切换项提供 `aria-pressed` 状态与“入座方式”分组名称，装饰卡牌不进入无障碍树。手机竖屏保留表单主路径与清晰焦点，装饰区按可用空间收起。

| 条件或状态 | 现有行为 |
| --- | --- |
| `guestEnabled=false` | 隐藏访客切换项，默认进入账号登录 |
| `githubEnabled=false` | 不展示 GitHub 登录按钮 |
| `passwordRequired=true` | 三种本地认证表单显示全站加入密码；GitHub 按钮同样要求先校验该密码 |
| 正在提交 | 主提交按钮及 GitHub 按钮禁用，主按钮显示“正在入座…”；模式切换项仍可操作 |
| 输入不满足 HTML 限制 | 浏览器表单校验阻止提交；服务端仍是最终校验方 |
| HTTP 返回错误 | 优先显示响应的 `error` 或 `message`，否则显示带状态码的通用错误；使用可关闭的全局提示 |
| GitHub 登录缺少加入密码 | 提示“请先输入全站加入密码”，不执行授权跳转 |
| 已登录 | 入口表单隐藏，显示大厅或牌桌；顶部显示昵称、个人设置和退出登录入口 |
| 退出登录 | 请求 `/api/auth/logout` 成功后清除前端用户状态并返回 `/` |

前端按钮隐藏不替代服务端权限、密码、会话与限流校验。真实 GitHub 授权还依赖部署方自己的 OAuth 应用配置。

## 验收场景

| 编号 | 场景与预期 | 现有验证入口 |
| --- | --- | --- |
| ENTRY-AC01 | 允许访客时填写昵称进入大厅；关闭访客时不出现访客入口 | 浏览器主流程；系统配置关闭分支需专门运行验收 |
| ENTRY-AC02 | 注册账号、退出、重新登录后身份保持正确 | [scripts/profile_check.py](https://github.com/li-sky/river-code/blob/main/scripts/profile_check.py) |
| ENTRY-AC03 | 登录请求不带注册专用字段，避免被严格 JSON 解码拒绝 | [scripts/profile_check.py](https://github.com/li-sky/river-code/blob/main/scripts/profile_check.py) 的真实登录流程 |
| ENTRY-AC04 | 配置加入密码后，缺少或错误密码失败，正确密码建立会话 | [scripts/smoke.py](https://github.com/li-sky/river-code/blob/main/scripts/smoke.py)、身份模块测试；脚本通过环境变量提供测试密码 |
| ENTRY-AC05 | GitHub 开启加入密码时先校验访问密码；OAuth 状态不能重复使用 | [backend/internal/identity/identity_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/identity_test.go)、[backend/internal/identity/oauth.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/oauth.go)；实际 GitHub 登录待部署环境验证 |
| ENTRY-AC06 | 邀请链接未登录时显示入口，登录后进入原牌桌 | 根据当前参数保留逻辑进行跨会话邀请验收；不把已有主流程视为该分支的完整测试 |
| ENTRY-AC07 | 手机竖屏无横向溢出，表单和按钮可使用；接口错误有可理解的提示 | [scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py) 覆盖登录后宽度；入口异常及小屏表单需补充专项场景 |

上述表格描述应验收的行为及已有验证入口，不代表本次新执行了所有场景。仓库 [docs/VERIFICATION.md](https://github.com/li-sky/river-code/blob/main/docs/VERIFICATION.md) 记录了 2026-09-30 的既有执行结果，并明确真实 GitHub、证书和跨网络语音仍待部署验证。

## 实现与测试相对路径

下列路径均相对于代码仓库根目录 `仓库根目录`。

| 路径 | 职责 |
| --- | --- |
| [frontend/src/App.tsx](https://github.com/li-sky/river-code/blob/main/frontend/src/App.tsx) | `App` 初始化、认证表单、GitHub 加入密码前置校验及页面切换 |
| [frontend/src/lib/api.ts](https://github.com/li-sky/river-code/blob/main/frontend/src/lib/api.ts) | 同源请求、JSON 请求体和响应错误解析 |
| [frontend/src/lib/types.ts](https://github.com/li-sky/river-code/blob/main/frontend/src/lib/types.ts) | `User`、`UserSettings`、`Config` 类型 |
| [frontend/src/style.css](https://github.com/li-sky/river-code/blob/main/frontend/src/style.css) | 入口、认证面板、提示及手机布局 |
| [backend/internal/identity/identity.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/identity.go) | 访客、自建账号、会话与个人接口 |
| [backend/internal/identity/oauth.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/oauth.go) | GitHub 授权流程 |
| [backend/internal/identity/identity_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/identity_test.go) | 身份与 OAuth 等自动化验证 |
| [scripts/profile_check.py](https://github.com/li-sky/river-code/blob/main/scripts/profile_check.py)、[scripts/browser_check.py](https://github.com/li-sky/river-code/blob/main/scripts/browser_check.py)、[scripts/smoke.py](https://github.com/li-sky/river-code/blob/main/scripts/smoke.py) | 真实服务和浏览器验收 |
| [docs/CONTRACT.md](https://github.com/li-sky/river-code/blob/main/docs/CONTRACT.md)、[docs/VERIFICATION.md](https://github.com/li-sky/river-code/blob/main/docs/VERIFICATION.md) | 数据契约与既有验证记录 |

## 待实现改进与待验证事项

1. 配置读取失败与用户读取失败的提示可进一步区分，尤其是网络故障与会话过期；当前用户读取错误统一回退到入口。

2. 增加入口专用的弱网、错误密码、访客关闭、GitHub 隐藏及小屏键盘遮挡验收；当前不存在覆盖所有入口分支的专用浏览器脚本。

3. 注册流程尚无邮箱验证、找回密码和密码重置页面；是否加入需后续确认。

4. 朋友试用反馈的收集入口、分类、修复闭环仅是待设计方案；当前没有产品内反馈功能或已收到反馈的数据。

5. 面向运行中系统、会话及牌局的热更新仅是方案，不是当前已实现能力；后续需定义升级后会话保持与邀请跳转的验收标准。

## 本次 UI 验收证据

2026-10-01 在隔离的本机 PostgreSQL 与真实房间服务上完成浏览器 UI 验收。入口、大厅、创建与个人设置弹窗检查 320px、390px 手机布局及桌面焦点；九人真实会话在 320、390、601、768、1024、1440px 检查头像、卡牌、筹码标签及触控区域。两人牌局通过延迟服务器响应核查行动等待反馈和恢复，并检查键盘开关、滑块、聊天和弹窗。减少动态效果分支已作 CSS 审阅，本次未运行操作系统偏好切换或屏幕阅读器专项测试。完整条件、范围和检查结果见 [game-ui-readability 计划](../plans/game-ui-readability.md)，这些记录不扩大为 OAuth、真实公网语音或全量历史场景的新验收。

## 文档与代码入口

[项目文档](https://github.com/li-sky/river-spec) · [代码仓库](https://github.com/li-sky/river-code)。当前实现基线为提交 [3fb5101](https://github.com/li-sky/river-code/commit/3fb51017e9594191d01d1e372a663c457217a25c)；后续实现变化需同步此规格和验收证据。
