# RIVER 服务启动与部署模块规格

本模块把配置、身份、数据库和房间服务组合成可自部署的应用，并提供进程停止与就绪检查。本文记录当前实现；不停机升级和统一热重载仍是下一阶段方案。

## 需求与职责

- 使用 PostgreSQL、Go 和 React，在一台服务器上运行多人娱乐筹码现金桌。

- 手机竖屏、平板和电脑横屏通过同一 Web 应用访问。公网麦克风需要 HTTPS，复杂网络需要独立 TURN 服务。

- 配置来自环境变量；部署者保管数据库密码及 OAuth Client Secret。GitHub 仓库访问令牌不属于应用的登录配置。

- 系统配置关闭的能力不能由房间设置重新开启。

## 当前启动与停止行为

`cmd/river/main.go` 先读取配置，再以 30 秒启动超时连接数据库并运行幂等迁移，创建身份服务，恢复房间和截止时间，最后启动 HTTP 服务。配置、数据库或恢复失败会停止启动，不会声称可玩。

HTTP 服务设置请求头和连接超时，接收 SIGINT 或 SIGTERM 后执行最长 10 秒的 HTTP Shutdown，再关闭房间服务和数据库。WebSocket 和运行中的牌局不能因此被假定为无缝迁移；升级后客户端依赖重连和持久化快照恢复。

## 当前部署方式

Docker 多阶段构建前端和 Go 可执行文件，运行容器使用非 root 用户、只读根文件系统及临时目录。Compose 包含 PostgreSQL 17、应用和可选 Caddy HTTPS 反向代理，数据库使用命名卷。

应用默认绑定本机端口；健康检查访问 `/healthz`，应用服务依赖数据库就绪。数据库密码为必填配置。头像和牌局保存在数据库，前端构建文件随镜像发布。

本地 [scripts/run-dev.sh](https://github.com/li-sky/river-code/blob/main/scripts/run-dev.sh) 启动数据库、构建前端并运行 Go；它没有统一监视后端源码。另开 Vite 可以获得前端 HMR，`/api` 及 WebSocket 代理到 Go。涉及 OAuth 的开发必须保持 BASE_URL 和 callback 一致。

## 验收场景

1. Compose 和开发脚本缺少数据库密码时失败；无效系统配置或非空 DATABASE_URL 连接失败时 Go 启动失败。直接运行 Go 且连接地址为空会使用无持久化的内存开发模式，不能据此验收生产持久化。

2. 数据库就绪后应用可访问静态页面和健康端点，至少两个玩家可以开始一手。

3. 重新启动连接同一数据库的应用，已登录身份、席位、筹码、私有牌局状态和行动截止时间恢复。

4. HTTPS 页面申请麦克风；不同网络下用已部署 TURN 验证语音。这项必须在实际部署环境验收。

5. 镜像以非 root、只读根文件系统运行，通过健康检查。

## 实现与验证入口

- [backend/cmd/river/main.go](https://github.com/li-sky/river-code/blob/main/backend/cmd/river/main.go)、[Dockerfile](https://github.com/li-sky/river-code/blob/main/Dockerfile)、[compose.yaml](https://github.com/li-sky/river-code/blob/main/compose.yaml)、[.env.example](https://github.com/li-sky/river-code/blob/main/.env.example)。

- [scripts/run-dev.sh](https://github.com/li-sky/river-code/blob/main/scripts/run-dev.sh)、[scripts/smoke.py](https://github.com/li-sky/river-code/blob/main/scripts/smoke.py)、[scripts/recovery_check.py](https://github.com/li-sky/river-code/blob/main/scripts/recovery_check.py)。

- [docs/DEPLOYMENT.md](https://github.com/li-sky/river-code/blob/main/docs/DEPLOYMENT.md) 包含完整启动、备份、升级、OAuth、HTTPS 和 TURN 操作。

- [docs/VERIFICATION.md](https://github.com/li-sky/river-code/blob/main/docs/VERIFICATION.md) 记录 2026 年 9 月 30 日已执行的验证及外部环境验证边界。

## 2026-10-01 公网部署

代码 `5b1751db96b1b5a53fe7b8b2867c2668971dd0e5` 已部署到 `us1.skyli.xyz`，公开地址为 https://river.skyli.xyz 。应用镜像 `river:5b1751d`、Compose 项目 `river` 和 PostgreSQL 持久卷 `river_postgres_data` 独立运行；本机端口分别为 `127.0.0.1:18080` 和 `127.0.0.1:15432`，通过现有 Nginx 与 Cloudflare 提供 HTTPS 和 WebSocket。

运行文件位于 `/opt/river`：`current` 指向源码版本，`river-compose` 为运维入口，`OPERATIONS.md` 记录日志、备份和更新方式。配置文件权限为 `0600`，不进入仓库。独立 Let's Encrypt 证书于 2026-12-30 到期；已启用 Certbot 定时续期及 Nginx reload hook，并通过续期演练。已定向清理该域名旧缓存，公开首页返回 `Cache-Control: no-store` 和 `CF-Cache-Status: BYPASS`。

后端 test/vet、前端构建、隔离 PostgreSQL 上的三人牌局与重启恢复、服务器及开发者本机通过公网域名的双人 WSS 完整结算均通过。既有 `skyli.xyz` 和 `us1.skyli.xyz` 首页仍返回 200。GitHub OAuth 已使用用户提供的凭据启用，授权跳转和 GitHub App 中的回调地址均为 `https://river.skyli.xyz/api/auth/github/callback`；完整用户授权登录未执行。TURN 未配置，跨网络语音未验收。发布证据见 [部署计划](../plans/deploy-us1.md)。

## 当前限制与下一阶段

当前采用单 Go 实例和最新快照恢复，不提供跨服务器房间迁移、完整牌局回放或零停机规则更新。下一阶段可建立稳定试玩环境与独立开发环境，先完成统一开发命令，再按手牌边界安排后端版本更新；具体规格见反馈与迭代方案。

## 文档与代码入口

[项目文档](https://github.com/li-sky/river-spec) · [代码仓库](https://github.com/li-sky/river-code)。当前源码基线为提交 `4975694`；后续实现变化需同步此规格和验收证据。
