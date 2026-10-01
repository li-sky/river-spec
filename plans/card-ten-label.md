# 牌面点数十显示为 10

## 元信息

```json
{
  "id": "card-ten-label",
  "status": "done",
  "specs": [
    "table"
  ],
  "risk": "ui",
  "checks": [
    "links",
    "frontend"
  ]
}
```

## 问题与目标

服务端以 T 编码十点牌，前端直接显示该编码，用户在公共牌看到 T 后无法直观识别点数，要求改为 10。

## 预期行为与范围

共享 Card 将点数 T 显示为 10，可读名称同步使用 10；覆盖公共牌、底牌、摊牌和装饰小牌。兼容已有 10 点数字符串，保留 A/J/Q/K、其他点数、花色、红黑颜色、牌背和空位；仅调整显示，不修改服务端牌码或规则。保留工作区已有的其他界面改动，只提交本次牌面修复。

## 验收场景

- [x] AC-01: 四花色的 T 明牌均显示 10，可读名称包含 10；已有 10 与 A/J/Q/K 正常。
- [x] AC-02: 桌面普通牌、小牌和 320px 手机紧凑摊牌的两位点数完整可读，牌背和空位保持原样。
- [x] AC-03: 前端构建及 links 检查通过，同步牌桌规格，localhost:8080 提供修复后的前端资源。

## 任务

- [x] T-01: 修改共享 Card 的点数显示与可读名称，单独提交相关差异。
- [x] T-02: 用真实组件和产品 CSS 检查桌面与手机渲染，构建前端并同步规格和运行证据，更新本机静态资源。

## 审阅结论

目标达成，代码提交 6b28070。差异只有共享 Card 的 rawRank 与显示点数映射两行，可读名称复用显示点数；服务端仍使用 T，A/J/Q/K、已有 10、花色与背面逻辑不变。单独暂存 HEAD 中的牌面差异后提交，已有其他 UI 和服务端工作区改动没有纳入。为固定可复现证据，在同一提交的干净隔离 worktree 执行构建和 links；Windows npm 路径通过已有 run-sdd-windows.py 适配。

从实际 Card 提取组件，用真实 React、lucide 和完整产品 CSS 渲染合成的 Ts/Th/Td/Tc、10h、A/J/Q/K，以及普通牌、小牌、手机底牌、紧凑摊牌和牌背/空位。1440px、390px、320px 的可读名称均使用 10，四花色名称完整，未出现 T。执行代理查看 1440px 和 320px 截图，确认两位点数完整可读，红黑颜色、唯一花色、牌背/空位正常；手机横向测试样例包含九张公共牌以覆盖全部点数，超过真实五张布局的部分属于样例容器。截图保存 .scratch/card-ten-1440.png、card-ten-390.png、card-ten-320.png，不提交生成物。没有新增重复实现的产品测试，也没有声称完整牌局回归。

本机容器 rootfs 只读，直接复制资源失败，未改变旧资源。最终在原运行镜像基础上只复制已验证的 dist，生成本机镜像 sha256:9ed1575a087cb821d0693262c26a24986fa838de30476723197fb73772a09748，docker compose up -d --no-deps app 成功，仅重启应用。现有数据库继续运行，app/db healthy；localhost:8080 首页和 JS/CSS 返回 200，并与本次构建逐字节一致，healthz 为 200。已同步规格并在更新后的规格上运行检查。未推送或发布公网。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T12:38:54.879995Z",
      "codeCommit": "6b280705598ba0ed37d1f5f5e290f92fbb4ec181",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "table": "5093a930f7e70d2caf87d88a000fd92f11f76ef06da4041b551bc31fff28995a"
      },
      "planFingerprint": "183665f094b3aea80d7d084f555c2cd27b75dd64c3c22a5c57bf28c6bc033f29"
    },
    {
      "check": "frontend",
      "commands": [
        {
          "argv": [
            "npm",
            "run",
            "build"
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\card-ten-label\\river-code\\frontend",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T12:38:55.587175Z",
      "codeCommit": "6b280705598ba0ed37d1f5f5e290f92fbb4ec181",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "table": "5093a930f7e70d2caf87d88a000fd92f11f76ef06da4041b551bc31fff28995a"
      },
      "planFingerprint": "183665f094b3aea80d7d084f555c2cd27b75dd64c3c22a5c57bf28c6bc033f29"
    }
  ],
  "codeCommit": "6b280705598ba0ed37d1f5f5e290f92fbb4ec181",
  "delivery": {
    "status": "local_running",
    "notes": "2026-10-01（Asia/Shanghai）本机 localhost:8080 已提供提交 6b28070 的修复前端；原应用镜像基础上更新 dist 后重新创建 app，数据库继续运行，首页及 JS/CSS 与已验证构建一致、healthz 为 200，app/db healthy。未推送或发布公网。"
  }
}
```
