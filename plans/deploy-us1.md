# 部署 RIVER 到 us1 和 river.skyli.xyz

## 元信息

```json
{
  "id": "deploy-us1",
  "status": "done",
  "specs": [
    "runtime"
  ],
  "risk": "docs",
  "checks": [
    "links"
  ]
}
```

## 问题与目标

用户要求部署到 root@us1.skyli.xyz，访问地址使用 https://river.skyli.xyz。发布当前干净代码基线 5b1751db96b1b5a53fe7b8b2867c2668971dd0e5。

## 预期行为与范围

使用独立 Compose 项目、PostgreSQL 持久卷和本机应用端口，接入服务器已有 Nginx。生产配置与密码仅保存在服务器，源码不变；因此文档检查采用 docs 风险，发布另执行镜像构建、后端检查、独立数据库验收和公网验证。保留其他服务，配置 HTTPS 与证书续期。用户随后提供两行 GitHub OAuth 凭据文件，配置到生产环境并检查登录入口与回调地址；完整 GitHub 授权登录和公网 TURN 通话需实际账号/设备验证，不声称已完成。

## 验收场景

- [x] AC-01: 发布指定代码版本，应用与独立 PostgreSQL 健康，容器重启策略和持久卷可核对。
- [x] AC-02: 公网域名 HTTPS 页面、健康和配置端点正常，证书有效且配置续期，WebSocket 与登录可用。
- [x] AC-03: 独立验收数据库上的多人牌局和恢复检查通过，既有站点仍可访问。
- [x] AC-04: 用户提供的 GitHub 凭据写入服务器私有环境，临时副本删除，GitHub 登录启用且授权跳转使用正确的公网回调地址。

## 任务

- [x] T-01: root 检查端口、代理和 DNS，打包当前提交并在服务器构建镜像、运行检查。
- [x] T-02: root 配置独立 Compose、数据库、Nginx 与 HTTPS，验证公网访问和其他站点。
- [x] T-03: root 记录发布版本、路径、检查证据与限制，同步 runtime 规格并完成计划。

## 审阅结论

已按用户指定主机与域名发布当前干净代码，无产品源码变化。源码版本为 5b1751db96b1b5a53fe7b8b2867c2668971dd0e5，生产启动时间为 2026-10-01 22:17:43（Asia/Shanghai）。

- AC-01：`river-compose ps` 确认 app/db 均 healthy。app 为 UID 10001、只读根文件系统、unless-stopped；数据保存在 river_postgres_data，端口仅本机 18080/15432。配置权限 0600。
- AC-02：独立域名证书签发成功，2026-12-30 到期；Certbot timer active，`renew --cert-name river.skyli.xyz --dry-run` 成功。公网旧首页最初被 Cloudflare 缓存，使用已登录控制台按主机名定向清除后：首页为 RIVER，CF-Cache-Status BYPASS、Cache-Control no-store。实际 Chrome 显示登录页和 GitHub 按钮，截图保存于工作区 .scratch/river-deployed.jpg。
- AC-03：服务器上运行 backend 构建阶段的 `go test ./...`、`go vet ./...` 与 runtime 镜像构建（包含 `npm run build`），均退出 0。独立 river-acceptance 项目实际运行 smoke.py，确认三人全下/边池、私牌隔离、房主权限、筹码守恒、聊天和重连；随后 recovery_check.py prepare → 重启应用 → verify，确认身份、席位、筹码、手牌、deadline 和 turn token 恢复。独立验收项目及数据卷随后清理。生产公网测试分别从服务器与 Windows 开发者本机访问 HTTPS，完成访客登录、Secure cookie、双人 WSS 入座及一手全下结算；测试玩家已退出私人房间并注销。既有 skyli.xyz/us1.skyli.xyz 首页均 200。
- AC-04：用户提供的凭据文件写入私有生产环境，服务器临时副本已删除。公开配置 githubEnabled 为 true；授权跳转包含正确 HTTPS callback、client_id 和 state。已只读核对用户打开的 GitHub OAuth App，首页和回调均匹配域名。

审阅结论：目标达成。运维路径、命令和备份方式保存在 /opt/river/OPERATIONS.md。完整 GitHub 用户授权及跨网络 TURN 通话尚未实际验证；未配置 TURN，不声称语音已在不同网络验收。没有修改其他站点配置或生产数据卷。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T14:21:52.808047Z",
      "codeCommit": "5b1751db96b1b5a53fe7b8b2867c2668971dd0e5",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "a5b0600fff2821da6a225f61b19228ea396de368479a9d7989caebbfacc2ff07",
      "specSha256": {
        "runtime": "5de3293000216bc2081d515708765d3c502e95b323de2eb66fd10d70156fe504"
      },
      "planFingerprint": "a337579d43977fbc464461e043baac0bac0a6780527295cc407bba4507d48f2a"
    }
  ],
  "codeCommit": "5b1751db96b1b5a53fe7b8b2867c2668971dd0e5",
  "delivery": {
    "status": "released",
    "notes": "2026-10-01 22:17:43 Asia/Shanghai deployed 5b1751db96b1b5a53fe7b8b2867c2668971dd0e5 to us1.skyli.xyz at https://river.skyli.xyz; app/db healthy, public HTTPS/WSS verified, GitHub OAuth configured."
  }
}
```
