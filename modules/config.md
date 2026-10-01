# RIVER 系统配置模块规格

基线日期：2026-10-01。状态：依据源码整理的当前基线，非新增产品需求。本文路径均相对于 RIVER 项目根目录。

## 目的与术语

将部署环境变量读成启动时的系统配置，并提供供前端发现能力的公开投影。按用户约定，“配置”指系统本身，“设置”指用户或房间／单局自己的选择。音量、头像 emoji 等个人设置不属于本模块；盲注、买入和当前桌语音模式属于房间设置。

已确认需求包括自部署、GitHub OAuth 与自建账号／访客、可选的全站统一加入密码，以及可在系统配置和房间设置中控制的语音功能。当前配置同时包含聊天和 reaction 的系统开关，用于限制房间可用能力。

## 当前配置接口

`Load() (Config, error)` 从进程环境读取并验证配置。`Config.Public() PublicConfig` 生成能力投影。主程序调用一次 `Load()`，将配置分别传给存储、身份服务和房间服务；当前没有配置写入 HTTP 接口或运行中重载机制。

下表为**当前实现默认值和验证边界**，不是用户指定的全部产品要求。敏感字段仅列名称与用途，不给出值。

| 环境变量 | 当前默认／用途／约束 |
| --- | --- |
| `LISTEN_ADDR` | 默认 `:8080`，服务监听地址。`Address` 与兼容字段 `Addr` 同值。 |
| `STATIC_DIR` | 默认 `../frontend/dist`，前端静态文件目录。 |
| `DATABASE_URL` | 无默认连接字符串；交由 `store.Open` 处理。空值时存储模块使用开发用途的内存实现，不满足生产持久化要求。 |
| `BASE_URL` | 默认 `http://localhost:8080`；须为完整 HTTP(S) origin，不允许用户名密码、查询、fragment 或非根路径，移除尾部 `/`。 |
| `JOIN_PASSWORD` | 可选全站准入密码，空值表示无此密码；不是逐房间密码。 |
| `GITHUB_CLIENT_ID`、`GITHUB_CLIENT_SECRET` | 两者同时提供才启用 GitHub OAuth；仅提供一个会使启动配置验证失败。 |
| `GUEST_ENABLED` | 默认 `true`，是否允许创建访客会话。与房间角色 guest 不同：房间 guest 表示加入房间的人。 |
| `VOICE_ENABLED` | 默认 `true`，系统级语音开关。 |
| `CHAT_ENABLED` | 默认 `true`，系统级文字聊天开关。 |
| `REACTIONS_ENABLED` | 默认 `true`，系统级定向表情和头像 emoji 开关。 |
| `DEFAULT_VOICE_MODE` | 默认 `free`，可选 `free`／`push-to-talk`；房间未指定 `voiceMode` 时采用此值。 |
| `SPECTATOR_VOICE_ENABLED` | 默认 `false`；旁观者通话还须获得对应房间设置允许。 |
| `ICE_SERVERS_JSON` | 默认空列表；JSON 数组，各项包含非空 `urls` 数组，URL 前缀仅允许 `stun:`、`stuns:`、`turn:`、`turns:`，可含 TURN 用户名和凭据。 |
| `TRUST_PROXY` | 默认 `false`，供身份中间件决定是否信任反向代理来源信息。 |

所有布尔环境变量使用 `strconv.ParseBool` 解析；无值使用默认值，非法非空值返回错误。当前 `SessionTTL` 固定为 30 天，没有对应环境变量。`SecureCookies` 根据 `BASE_URL` 是否为 HTTPS 自动推导，不是独立可覆盖的开关。

`DATABASE_URL`、全站准入密码、OAuth 凭据和 ICE 凭据不得写入文档、前端静态文件或公开日志。

## 公开能力与权限

`GET /api/config` 在身份服务中注册，匿名可访问。公开字段为：

```text
guestEnabled, githubEnabled, passwordRequired,
voiceEnabled, defaultVoiceMode, spectatorVoiceEnabled,
chatEnabled, reactionsEnabled, iceServers
```

- `githubEnabled` 只表示两项 OAuth 参数都存在，不能证明提供方连通性或实际登录已经验证。

- `passwordRequired` 只表示全站密码是否已配置，不输出密码本身。

- `Public()` 本身保留 ICE 配置，不执行身份授权；`identity.Register` 中的 HTTP 处理器在未认证时将整个 `iceServers` 清为空数组。不能直接把 `Public()` 当作适合任意匿名输出的过滤器。

- 已认证用户会获得 ICE 配置，可能包括通话所需 TURN 凭据；是否采用短期动态凭据不是本模块已实现的能力。

- 房主可以调节本房间设置，不能绕过系统开关。系统和房间语音／聊天／reaction 同时允许才可使用；旁观者语音也要求两个层级同时允许。

- 配置模块没有操作员账号或 RBAC API；当前更改配置的权限来自部署环境本身。

## 生命周期与错误边界

主程序启动顺序为加载配置 → 打开存储 → 构造身份服务 → 恢复房间服务 → 启动 HTTP。配置解析失败直接使启动失败，不会启动半配置的游戏服务。

当前显式失败条件包括非法布尔值、非法默认语音模式、非法 `BASE_URL`、不成对的 OAuth 参数、ICE JSON 解码失败、ICE 项缺少 URL 或 URL 前缀不允许。错误可能来自标准库原文，不是稳定的面向用户错误码契约。

本模块仅做静态格式验证：没有检查数据库是否连接成功、OAuth 是否真实可用、STUN/TURN 是否能联通，也没有证明某项地址参数可以监听；这些由启动后相应模块或部署验收处理。ICE URL 当前只是前缀验证，不是完整协议地址验证。

服务和身份组件各持有初始化的配置值；没有运行中更新或配置传播接口。环境变量修改后需重启进程。默认语音模式只补齐新建／恢复时缺失的房间 `voiceMode`，不会持续覆盖已有房间明确选择的语音设置。

## 关键验收场景与证据

| 场景 | 当前测试或核实入口 |
| --- | --- |
| HTTPS origin 推导安全 cookie，允许代理信任开关及可解析 ICE 配置 | `config_test.go::TestLoadValidation` |
| 非根路径 origin、单项 OAuth 参数应阻止启动 | `config_test.go::TestLoadValidation` |
| 语音默认值为自由发言、旁观者默认禁止；可选按住说话并公开对应能力 | `config_test.go::TestVoiceConfiguration` |
| 非法语音模式、非法旁观者布尔值拒绝加载 | `config_test.go::TestVoiceConfiguration` |
| 匿名配置响应不得含 ICE 凭据；已认证用户可得到配置 | `identity_test.go::TestICECredentialsRequireSession` |
| 房间未给语音模式时补齐系统默认，旧快照恢复亦补齐 | `server_test.go::TestVoiceModeNormalizationAndRecovery` |
| 系统／房间任一层禁止旁观者时信令被拒绝 | `server_test.go::TestSpectatorVoicePermissionsAndNinePeerRoster` |

上表为当前测试源码覆盖，不代表所有环境变量、所有 URL 变体或部署外部依赖均有测试覆盖，也不替代实际环境执行记录。可在 `backend` 中运行 `go test ./internal/config`。

## 源文件与测试相对路径

- [backend/internal/config/config.go](https://github.com/li-sky/river-code/blob/main/backend/internal/config/config.go)、[backend/internal/config/config_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/config/config_test.go)。

- [backend/cmd/river/main.go](https://github.com/li-sky/river-code/blob/main/backend/cmd/river/main.go)：启动时加载及使用配置。

- [backend/internal/identity/identity.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/identity.go)、[backend/internal/identity/identity_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/identity_test.go)：公开配置响应及认证过滤。

- [backend/internal/server/server.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server.go)、[backend/internal/server/server_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server_test.go)：语音默认设置、系统能力约束。

- [docs/DEPLOYMENT.md](https://github.com/li-sky/river-code/blob/main/docs/DEPLOYMENT.md)、[docs/CONTRACT.md](https://github.com/li-sky/river-code/blob/main/docs/CONTRACT.md)、[docs/VERIFICATION.md](https://github.com/li-sky/river-code/blob/main/docs/VERIFICATION.md)：部署和跨模块参考。

## 已知限制与待实现

配置热重载、在线配置编辑、可持久化的系统配置管理台、动态 TURN 凭据签发、配置版本／变更审计、独立可调的会话 TTL 均未实现。当前也没有按 host／guest 持久化管理的默认权限配置矩阵或个人开房模板；房间设置不等同于系统配置。朋友反馈功能未实现，不存在对应配置开关。

## 文档与代码入口

[项目文档](https://github.com/li-sky/river-spec) · [代码仓库](https://github.com/li-sky/river-code)。当前源码基线为提交 `4975694`；后续实现变化需同步此规格和验收证据。
