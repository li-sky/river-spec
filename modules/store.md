# RIVER 数据存储模块规格

基线日期：2026-10-01。依据当前 `store` 实现、迁移及测试源码整理；源码路径均相对于代码仓库根目录。“测试覆盖”描述现有测试源码的断言，不代表每次文档更新都重新执行了该测试。

## 需求与责任边界

自部署系统以 PostgreSQL 保存账号、用户设置、会话、头像、房间及进行中的牌局，供重启后恢复。存储层应与身份、牌局规则、HTTP/WebSocket 分离，保留完整私有牌局快照供服务端使用。

`store` 提供 Go 仓储接口，不提供 HTTP API、不认证调用者、不判断房主权限、不删除对手手牌，也不执行德州扑克规则。上层身份服务负责密码哈希和会话令牌摘要；房间服务负责合法动作、权限、私有快照构造与面向每个用户的公开投影。系统配置决定数据库连接；音量、静音及头像 emoji 属于用户设置，房间盲注等单局设置作为房间快照的一部分保存。

## 当前实现

### 后端模式与启动

`Open(ctx,databaseURL)` 返回 `*Store`：连接地址非空时创建 pgx/v5 连接池，执行 Ping，再执行编译时嵌入的 `migration.sql`；任一步失败均返回错误并关闭已建立的池，不会悄悄降级内存。连接地址为空时创建内存映射，供本地演示/测试使用。`MemoryMode()` 可辨别实际模式，`Close()` 关闭数据库池，内存模式无需额外关闭资源。

迁移使用 `CREATE TABLE/INDEX IF NOT EXISTS`，适用于当前初始化结构；没有迁移版本表、列升级、降级或多版本兼容管理。内存实现用一个 RWMutex 保护映射；服务重启后全部数据丢失，不应视为生产持久化方案。

### 数据模型与数据库结构

| 表 / Go 模型 | 已实现数据 | 约束与用途 |
| --- | --- | --- |
| `river_users` / `Account` | `id`、可空 `email`、可空 `github_id`、`password_hash`、User 的 JSONB `profile` | id 主键；邮箱与 GitHub ID 各自唯一；空账号字段写为 NULL，使多个访客可共存 |
| `User` | `id,name,avatarUrl,guest,settings` | HTTP 可公开的用户资料，不含账号凭据；`guest` 表示访客身份，不是房间 guest 角色 |
| `Settings` | `soundEnabled,volume,voiceMuted,avatarEmoji` | 用户设置；存储层不自行校验值域或默认值，身份模块负责 |
| `river_sessions` | `token_hash,user_id,expires_at` | token_hash 主键；user_id 外键删除级联；过期时间索引；存储参数需已是摘要 |
| `river_rooms` / `RoomRecord` | `id,name,host_id,snapshot,updated_at` | id 主键；快照 JSONB；host_id 是普通文本，没有用户外键；按 ID upsert |
| `river_messages` | 自增 `id,room_id,message` | room_id 外键删除级联；room/id DESC 索引；message 为 JSONB |
| `river_avatars` | `id,mime_type,data` | id 主键；data 为 bytea；没有用户归属外键或删除策略 |

`Account` 将身份凭据与对外 `User` 分开。`RoomRecord.Snapshot` 是服务端内部数据；存储层既不知道其规则版本，也不会生成安全的浏览器视图。

### 会话及资料

`SessionUser` 仅返回未过期会话的用户，并重新读取账号资料，使新的用户设置在后续请求生效。内存使用进程时间，PostgreSQL 使用数据库 `now()` 判定过期。创建会话时清理已过期记录；没有独立周期清理任务。`DeleteSession` 删除单条会话，无此记录也成功。

`UpdateUser` 只替换 JSON 资料，不修改邮箱、GitHub ID 或密码哈希；未知用户返回 `ErrNotFound`。这是完整资料覆盖写入，没有字段级合并、乐观版本或比较交换。

### 房间快照与消息

房主置顶消息通过完整房间快照中的 `pinnedMessage: Message|null` 保存，独立于最近 100 条 `Messages`；裁剪不影响置顶。房间服务负责 ID 查找、权限、保存后广播及失败回滚；存储层仍只保存 JSON。无需新增 SQL 字段或采用独立消息表，旧快照缺置顶字段时由房间服务恢复为 null。实现与验证见 [置顶计划](../plans/host-pin-message.md)。

`SaveRoom` 要求输入是合法 JSON，然后将 ID、名称、房主 ID 和完整快照一次写入；PostgreSQL 更新 `updated_at`，内存复制输入字节避免外部修改。`LoadRooms` 读取所有房间，PostgreSQL 按 `updated_at` 排序；内存映射遍历顺序不保证稳定。JSON 校验只保证语法，不验证必须为对象、牌局规则、资金守恒或 schema。

独立消息接口 `SaveMessage/LoadMessages` 已实现：保存合法 JSON，裁剪至每房间最近 100 条，读取按时间顺序对应的自增 ID 顺序返回。PostgreSQL 的插入和裁剪处于同一事务；内存锁内操作并复制字节。

**当前房间服务实际使用的消息持久化路径是房间完整快照。** [backend/internal/server/commands.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/commands.go) 将 `Messages` 截断为最近 100 条，随后通过 `SaveRoom` 保存；房间服务的仓储接口只声明 `SaveRoom/LoadRooms`，没有调用独立消息接口。消息表和仓储测试的存在不能当作当前产品已采用独立消息表的证据。

### 头像

存储层接受调用者提供的 MIME 和任意二进制数据，不做解码、安全校验、尺寸限制或图片转换；这些工作属于身份模块。内存保存和返回时复制字节；PostgreSQL直接保存 bytea。头像按新 ID 插入，没有替换 upsert、垃圾回收或删除接口。

## Go 接口契约

| 方法 | 输入/输出与行为 | 调用权限边界 |
| --- | --- | --- |
| `Open(ctx,databaseURL)`、`Close()`、`MemoryMode()` | 创建仓储、关闭池、查询后端模式 | 仅服务器内部生命周期管理；连接地址是系统配置，不应发送客户端或写入普通文档 |
| `CreateAccount(ctx,Account)` | 新建账号；重复 id/email/GitHub ID 返回 `ErrConflict` | 身份服务构造；本方法不自行计算密码哈希 |
| `AccountByID/AccountByEmail/AccountByGitHub(ctx,key)` | 返回内部 Account；没有记录返回 `ErrNotFound` | 返回值含凭据字段，禁止直接用作 HTTP 用户响应 |
| `UpdateUser(ctx,User)` | 全量替换用户资料；无用户返回 `ErrNotFound` | 上层必须验证只能修改当前用户或获授权用户 |
| `CreateSession(ctx,hash,userID,expires)` | 保存会话并清理过期项 | hash 由身份服务提供；不验证其是否真为 SHA-256；PostgreSQL要求用户存在 |
| `SessionUser(ctx,hash)` | 有效会话 → 最新 User | 不存在/过期返回 `ErrNotFound`；数据库故障向上返回错误 |
| `DeleteSession(ctx,hash)` | 删除指定会话 | 上层决定该令牌所属请求能否撤销；不存在亦成功 |
| `SaveRoom(ctx,id,name,hostID,snapshot)` | JSON 语法校验及覆盖/upsert | 不判定 host 身份、牌局动作或版本顺序 |
| `LoadRooms(ctx)` | 返回所有完整私有快照 | 仅启动恢复/内部健康检查等服务器调用；不是公开房间列表接口 |
| `SaveMessage(ctx,roomID,json.RawMessage)` | 保存及裁剪最近 100 条 | 调用者负责用户、房间、聊天功能权限和内容长度；PostgreSQL要求房间存在 |
| `LoadMessages(ctx,roomID)` | 最近 100 条按顺序返回；无消息返回空切片 | 没有房间可见性判断 |
| `SaveAvatar(ctx,id,mime,data)` | 保存二进制头像 | 调用者必须先校验图片；同 ID 在内存覆盖、在数据库违反主键约束 |
| `Avatar(ctx,id)` | 返回 MIME、字节及错误 | 内存无头像返回 `ErrNotFound`；PostgreSQL无头像返回 pgx 行不存在错误，身份 HTTP 层统一转 404 |

除仓储级规则之外，不应依赖内存测试替代 PostgreSQL约束：内存没有数据库外键校验；`CreateSession` 同 token 可覆盖，而 PostgreSQL同 token 插入冲突；`SaveAvatar` 同 ID 也有上述差异。

## 隐私 失败及一致性边界

- 密码哈希、邮箱、GitHub ID、令牌摘要和完整私有牌局均属于服务端数据。数据库读取权限不能等同于房间加入权限；本模块不执行手牌脱敏，公开房间 API必须由上层构造。

- 实现没有应用层数据库内容加密；连接 TLS、数据库访问权限、磁盘保护和备份由自部署配置及运维保障。

- `CreateAccount` 仅把 PostgreSQL SQLSTATE 23505 转换为 `ErrConflict`，其余数据库错误保留返回；查找/更新/快照/头像也将故障交给上层。启用连接地址但连接失败不会启动可用的内存实例。

- `SaveRoom` 单行写入具备单语句原子性，但没有 expected-version 检查；多个调用者最后完成的写入可覆盖先前快照。房间服务负责单实例锁、先保存后广播及持久化失败回滚；详见其自身文档与 `TestPersistenceFailureDoesNotBroadcastOrAdvanceHand`。

- 用户创建、会话创建、头像写入、用户资料更新之间没有跨方法事务。发生部分失败可出现已注册但未登录、已保存但未引用头像等状态。

- `SaveMessage` 的插入和裁剪在单调用事务内；不同进程并发写同房间没有专门串行锁，严格最大 100 条的并发保证未单独测试。当前产品消息通过受房间服务锁管理的快照路径保存。

- 无账号/房间/头像删除业务接口、无数据库连接池动态配置入口、无私有快照 schema 迁移工具、无历史牌局归档、无备份/恢复实现。过期会话没有定时清理；不再产生新会话时，过期数据库记录仍可能保留。

## 验收场景与现有证据

| 场景 | 现有测试覆盖 |
| --- | --- |
| 内存账号及会话 | 创建账号、相同邮箱冲突、有效会话读取。`TestMemoryPersistenceIsolation` |
| 内存快照隔离 | 写入后改动原始字节不会污染快照；修改读取结果后再次读取仍为有效 JSON。`TestMemoryPersistenceIsolation` |
| 内存消息保留 | 写 110 条后返回最近 100 条，首条是原第 11 条。`TestMemoryPersistenceIsolation` |
| PostgreSQL初始化与数据持久化 | 两个独立 Store/连接池间读取账号会话、快照、消息、头像；重复邮箱冲突；跨池用户 emoji 更新可见。`TestPostgresDurableRoundTrip` |
| PostgreSQL单会话撤销 | 第二个仓储删除会话后，第一个仓储无法再读取会话用户。`TestPostgresDurableRoundTrip` |
| 身份层过期会话 | 过期令牌访问 `/api/me` 返回 401。身份模块 `TestSessionExpiryAndOrigin` |
| 产品快照失败与恢复 | 房间服务测试覆盖持久化失败不广播/不推进、重启超时恢复，分别为 `TestPersistenceFailureDoesNotBroadcastOrAdvanceHand`、`TestTimeoutAndRestartRecovery`；不属于存储仓储单元测试 |

仓储测试源码：[backend/internal/store/store_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/store/store_test.go)、[backend/internal/store/postgres_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/store/postgres_test.go)。在 `backend/` 下可执行 `go test -race ./internal/store`。PostgreSQL测试仅在测试进程提供 `TEST_DATABASE_URL` 时执行，否则会跳过；它会创建并清理带独立测试 ID 的记录。该测试是两个连接池间往返验证，没有主动重启 PostgreSQL进程，也没有覆盖真实机器故障恢复。

## 已实现与后续范围

已实现：当前 schema 初始化、PostgreSQL和本地内存两种仓储、内部账号/会话/资料接口、完整房间快照、独立消息接口、头像二进制保存、上述测试源码。

尚未实现且没有本次新增排期：版本化 schema 迁移、跨节点写入一致性、事务化账号会话/头像资料操作、数据删除及垃圾回收、私有数据归档、独立消息表产品接入、备份自动化。若后续要求多实例部署，应先定义房间写入所有权和快照版本策略，不能仅凭 PostgreSQL连接池推定系统已经支持多实例。

## 源码定位

- [backend/internal/store/store.go](https://github.com/li-sky/river-code/blob/main/backend/internal/store/store.go)：类型、仓储接口及两种后端实现。

- [backend/internal/store/migration.sql](https://github.com/li-sky/river-code/blob/main/backend/internal/store/migration.sql)：编译时嵌入的初始化 SQL。

- [backend/internal/store/store_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/store/store_test.go)：内存数据及字节隔离、消息保留测试。

- [backend/internal/store/postgres_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/store/postgres_test.go)：可选真实 PostgreSQL往返测试。

- [backend/internal/identity/identity.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/identity.go)、[backend/internal/identity/oauth.go](https://github.com/li-sky/river-code/blob/main/backend/internal/identity/oauth.go)：凭据处理、调用权限、上传校验的上层边界；详见 `identity.md`。

- [backend/internal/server/server.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server.go)、[backend/internal/server/commands.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/commands.go)、[backend/internal/server/server_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/server_test.go)：快照恢复、消息实际保存路径及持久化失败处理。

## 文档与代码入口

[项目文档](https://github.com/li-sky/river-spec) · [代码仓库](https://github.com/li-sky/river-code)。当前源码基线为提交 `4975694`；后续实现变化需同步此规格和验收证据。

消息撤回继续通过房间 JSON 快照持久化，不调用独立消息表：`Messages` 中保留作者、时间和 ID，清空 text 并保存 `recalled:true`；撤回关联置顶时清空 `pinnedMessage`。旧快照没有 recalled 字段保持普通消息，无 SQL 迁移。保存失败时服务端回滚内容与版本，不广播。实际恢复及故障测试见 [聊天气泡计划](../plans/chat-bubbles.md)。
