# 部署 RIVER 到 us1 和 river.skyli.xyz

## 元信息

```json
{
  "id": "deploy-us1",
  "status": "in_progress",
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

- [ ] AC-01: 发布指定代码版本，应用与独立 PostgreSQL 健康，容器重启策略和持久卷可核对。
- [ ] AC-02: 公网域名 HTTPS 页面、健康和配置端点正常，证书有效且配置续期，WebSocket 与登录可用。
- [ ] AC-03: 独立验收数据库上的多人牌局和恢复检查通过，既有站点仍可访问。
- [ ] AC-04: 用户提供的 GitHub 凭据写入服务器私有环境，临时副本删除，GitHub 登录启用且授权跳转使用正确的公网回调地址。

## 任务

- [ ] T-01: root 检查端口、代理和 DNS，打包当前提交并在服务器构建镜像、运行检查。
- [ ] T-02: root 配置独立 Compose、数据库、Nginx 与 HTTPS，验证公网访问和其他站点。
- [ ] T-03: root 记录发布版本、路径、检查证据与限制，同步 runtime 规格并完成计划。

## 审阅结论

TODO: 完成后补充实现差异审阅和人工验收结论。

## 验证记录

```json
{
  "runs": [],
  "codeCommit": "",
  "delivery": {
    "status": "not_released",
    "notes": ""
  }
}
```
