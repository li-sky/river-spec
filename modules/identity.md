# RIVER 身份与用户设置模块规格

基线日期：2026-10-01。依据当前实现及测试源码整理；以下源码路径均相对于代码仓库根目录。标记“已实现”表示存在实现；标记“测试覆盖”表示对应测试源码包含该场景，不代表每次文档更新都重新执行了该测试。

## 需求与范围

用户可以使用自建账号、GitHub OAuth 或访客身份进入系统。系统配置可关闭访客入口，或要求初次认证时输入统一加入密码。登录用户可以维护昵称、头像及个人设置。系统配置属于系统；音效、音量、个人静音和头像 emoji 属于用户设置。

身份与房间角色分离：用户响应中的 `guest=true` 表示访客身份；房间中的 host 是房主、guest 是加入房间的人。访客也可以成为房主，房主权限由房间服务判定，本模块没有管理员或房主权限模型。

## 当前实现

### 身份及默认用户设置

| 项目 | 已实现行为 |
| --- | --- |
| 用户模型 | `id`、`name`、`avatarUrl`、`guest`、`settings`；API 不返回账号密码哈希、账号邮箱、GitHub ID |
| 自建账号 | 邮箱与密码注册、登录；邮箱去除首尾空白后转小写；昵称 1–32 个 Unicode 字符且不含控制字符；注册密码 8–72 **字节**；bcrypt 默认成本保存密码哈希 |
| 访客 | 系统配置允许时创建独立身份及会话；无账号密码；需验证统一加入密码；没有凭昵称找回身份的接口 |
| GitHub | 使用稳定的 GitHub 数字 ID 查找或创建账号；初次创建时使用 GitHub 昵称、登录名回退及合法头像；已有账号不会每次登录覆盖资料 |
| 新身份设置 | `soundEnabled=true`、`volume=0.65`、`voiceMuted=true`、`avatarEmoji=""` |
| 设置校验 | 音量范围 0–1；头像 emoji 最多 8 个 Unicode 字符、40 字节，拒绝 CR/LF/NUL；允许空值清除 emoji |

自建账号注册默认使用 Gravatar：对规范化邮箱计算 MD5，生成带 identicon 回退的头像 URL。这里的 MD5 是 Gravatar 标识格式，密码和会话不使用 MD5。

### 会话

会话令牌由 32 字节加密随机数生成并编码成 64 字符十六进制串。浏览器持有 `river_session` Cookie，服务端仅将其 SHA-256 摘要交给存储层。Cookie 使用 `HttpOnly`、`SameSite=Lax`、根路径；当系统配置的 `BASE_URL` 为 HTTPS 时启用 `Secure`。默认有效期 30 天，不提供滑动续期。

建立新会话后，会尝试删除当前请求携带的旧会话。退出删除当前令牌对应会话并清除 Cookie；不会退出同一账号的其他设备。每次 `User(r)` 调用根据 Cookie 查询尚未过期的会话，再加载最新用户资料。

### GitHub OAuth 与统一加入密码

1. 配置了统一加入密码时，客户端先向 `POST /api/auth/access` 的 JSON 请求体提交密码。

2. 成功后签发有效期 5 分钟的 `river_access` HttpOnly Cookie，并在本进程内保存令牌摘要。

3. `GET /api/auth/github` 消费一次 access 许可，创建有效期 5 分钟的 OAuth state 及 `river_oauth_state` Cookie，然后跳转 GitHub。

4. 回调必须同时匹配请求 state、Cookie state 和服务端尚未消费的 state；在兑换 code 前消费 state，阻止重复回调。

5. 后端通过 POST 兑换 token，再调用 GitHub 用户 API；成功后建立本地会话并跳转 `/`。

统一加入密码不放入 URL 或 GitHub 跳转参数。GitHub token 仅用于当前回调，不写入本地账号记录，也不返回前端。当前请求 scope 为 `read:user user:email`，实现没有读取 GitHub 邮箱或按邮箱自动合并本地账号。

### 头像

支持三种入口：上传文件、Gravatar 邮箱、合法的外部 HTTPS 头像 URL。用户同时提交 `avatarUrl` 和 `gravatarEmail` 时，后处理的 Gravatar 覆盖外部 URL。

上传采用 multipart 字段 `file`：原文件最大 2 MiB，总请求允许额外 64 KiB multipart 开销；实际解码格式仅 PNG/JPEG/GIF；宽高各最多 4096、像素总数最多 400 万。图片中心裁剪为正方形，缩放至 256×256 后重新编码 PNG，再写入存储。GIF 动画不保留，WebP/SVG 不支持。头像 ID 为随机 64 字符标识，公开读取 URL 为 `/api/avatars/{id}`。

外部 URL 校验拒绝凭据、非 HTTPS、localhost、`.localhost`、`.local` 及若干直接填写的内网/回环 IP；本地头像仅允许 `/api/avatars/` 路径且不含 `..`、查询串或片段。本模块不会代理下载外部头像，也没有 DNS 解析或域名白名单验证。

## HTTP 接口及权限

除上传外，带请求体的认证/资料接口要求 `application/json`，最大 64 KiB，拒绝未知字段和多段 JSON。JSON 响应采用 `Cache-Control: no-store`；错误格式为 `{error: string}`。

| 接口 | 请求/返回 | 身份与权限 |
| --- | --- | --- |
| `GET /api/config` | 返回系统公开配置 | 不要求登录；无有效会话时强制 `iceServers=[]`，避免公开 TURN 凭据；登录后返回配置中的 ICE 信息 |
| `POST /api/auth/guest` | `{name,password}` → 201 User | 要求访客已开放；`password` 是统一加入密码 |
| `POST /api/auth/register` | `{name,email,password,joinPassword}` → 201 User | 要求统一加入密码正确；邮箱冲突返回 409 |
| `POST /api/auth/login` | `{email,password,joinPassword}` → 200 User | 账号密码及统一加入密码都需正确；账号或账号密码错误统一返回 401 |
| `POST /api/auth/access` | `{password}` → `{ok:true}` | 验证统一加入密码，用于 OAuth 前置许可；不建立登录会话 |
| `GET /api/auth/github` | 302 GitHub 授权页 | 必须配置 GitHub；配置加入密码时要求 access 许可；未配置 GitHub 返回 503 |
| `GET /api/auth/github/callback` | 查询参数 `code,state` → 302 `/` | 要求有效、未消费的 state；不能作为普通无条件登录入口 |
| `POST /api/auth/logout` | 204 | 无会话也可调用；删除会话失败返回 500 |
| `GET /api/me` | 200 User | 必须持有有效会话；未登录或会话查询失败返回 401 |
| `PATCH /api/me` | 可选 `name,avatarUrl,gravatarEmail,settings` → 200 User | 仅更新当前会话用户；没有任意用户 ID 输入；省略设置字段保留原值 |
| `POST /api/me/avatar` | multipart `file` → 200 User | 必须登录；保存失败返回 500 |
| `GET /api/avatars/{id}` | PNG 字节 | 公开资源，无会话要求；无效/不存在/读取失败返回 404；一年 public immutable 缓存 |

Go 集成接口：`New(config.Config,*store.Store)`、`Register(*http.ServeMux)`、`User(*http.Request)`、`Middleware(http.Handler)`、`SetEmoji(context.Context,userID,emoji)`。`User` 和 `Settings` 为存储层类型别名。`SetEmoji` 不自行验证调用者身份，调用它的房间服务负责只允许用户更新自己的头像 emoji。

## 安全 隐私及失败边界

- 中间件对修改类请求校验存在的 `Origin` 必须与系统 `BASE_URL` 的 scheme/host 一致，拒绝带路径/查询/片段/凭据的 Origin；拒绝 `Sec-Fetch-Site: cross-site`。允许缺少 Origin 的非浏览器请求，并非独立 CSRF token 方案。设置 `X-Content-Type-Options: nosniff`。

- guest/register/login/access/GitHub 发起及回调共用按客户端 IP 计数的每分钟 15 次窗口；超出返回 429 和 `Retry-After: 60`。限流在内存中，重启即清空；启用系统 `TRUST_PROXY` 后采用最右侧合法 `X-Forwarded-For` IP，需部署保证后端只接受可信代理请求。

- 账号不存在或没有本地密码时仍执行一次 dummy bcrypt 比较。账号查询故障在登录入口也表现为 401，不能从该状态码区分数据库故障与账号错误。

- 修改统一加入密码不会自动撤销已存在的登录会话；密码只在初次认证/OAuth 前置验证时检查。

- 头像资源公开且缓存时间长，没有用户归属读取限制。替换头像不会删除旧文件；存储成功而资料更新失败时可能留下未引用头像。

- Gravatar 邮箱哈希与外部头像 URL 会被浏览器发送给对应第三方；邮箱哈希不等于不可推测的匿名标识。

- OAuth pending access/state 存于当前进程，服务重启后需要重新发起授权；多实例无共享状态，未提供完整多实例 OAuth 保证。外部 HTTP 客户端超时为 15 秒，网络/兑换/资料获取失败返回 502。

- 注册创建账号与创建会话不是同一事务：会话创建失败时账号仍可能已存在。旧会话删除失败被忽略。资料 PATCH 与 `SetEmoji` 采用完整资料读改写，没有乐观版本控制，同时修改可能覆盖对方字段。

- 房主权限、房间密码策略、牌局隐私投影、WebSocket 断开/续验均属于房间服务；身份模块只提供会话验证基础能力。

## 验收场景与现有证据

| 场景 | 期望与测试覆盖 |
| --- | --- |
| 注册密码门禁 → 注册 → 读取/修改自己 → 登录 → 退出 | 加入密码错误 403；正确注册 201；Cookie 安全属性及 no-store；用户设置更新；非法头像 URL 400；邮箱大小写登录；退出后会话 401。`TestAccountSessionAndJoinPassword` |
| 过期会话及跨站修改 | 过期会话 401；跨源 PATCH 403；访客加入密码错误 403。`TestSessionExpiryAndOrigin` |
| 合法 PNG 上传 | 上传后头像可读取，并为 256×256 PNG。`TestAvatarNormalization`；超大小/损坏/GIF/WebP 等边界有实现校验，但此测试不逐项覆盖 |
| OAuth 门禁、state 与重放 | 未验证密码不能跳转；OAuth URL 不带加入密码；模拟 GitHub 成功创建会话；重复回调 403。`TestGitHubPasswordStateAndReplay`；不是真实 GitHub 集成验收 |
| 认证限流 | 同一 IP 的第 16 次认证请求返回 429。`TestAuthRateLimit` |
| TURN 信息隐私 | 未登录配置响应无 ICE 凭据；有效登录后获得 ICE 配置。`TestICECredentialsRequireSession` |

全部身份测试在 [backend/internal/identity/identity_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/identity_test.go)。可在 `backend/` 下执行 `go test -race ./internal/identity`；

## 当前限制与待决策项

已实现范围包括上述认证、会话、头像和个人设置。未实现：邮箱验证、密码重置/修改、账号注销、GitHub 与邮箱账号关联、撤销全部设备会话、头像垃圾回收、共享 OAuth/限流状态、MFA。没有新增这些功能的已批准排期；若后续提出需求，应单独写变更规格和验收场景。真实 GitHub 回调需部署系统配置及提供商应用注册配合，现有模拟测试不能代替部署验收。

## 源码定位

- [backend/internal/identity/identity.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/identity.go)：HTTP 路由、Cookie、会话读取、同源与限流、个人设置、头像。

- [backend/internal/identity/oauth.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/oauth.go)：统一密码 access 许可与 GitHub OAuth。

- [backend/internal/identity/identity_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/identity_test.go)：上述验收测试源码。

- [backend/internal/store/store.go](https://github.com/li-sky/river-code/blob/main/backend/internal/store/store.go)：User/Settings 模型及身份持久化；详见 `store.md`。

- [backend/internal/config/config.go](https://github.com/li-sky/river-code/blob/main/backend/internal/config/config.go)：身份功能所依赖的系统配置加载和公开投影。

- [backend/internal/server/server.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server.go)、[backend/internal/server/commands.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/commands.go)：调用 Middleware/User/SetEmoji 的房间集成边界。

## 文档与代码入口

[项目文档](https://github.com/li-sky/river-spec) · [代码仓库](https://github.com/li-sky/river-code)。当前源码基线为提交 `4975694`；后续实现变化需同步此规格和验收证据。
