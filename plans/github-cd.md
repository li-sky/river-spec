# GitHub Actions 自动检查与 us1 持续部署

## 元信息

```json
{
  "id": "github-cd",
  "status": "done",
  "specs": [
    "runtime",
    "workflow"
  ],
  "risk": "tooling",
  "checks": [
    "links",
    "sdd"
  ]
}
```

## 问题与目标

用户要求为已部署的 https://river.skyli.xyz 增加自动部署/CD。当前代码仓库没有 Actions 工作流，生产版本为 5b1751d，发布依赖手工打包、SSH 构建和更新。

## 预期行为与范围

增加 GitHub Actions：PR 运行检查；main push 和 main 上的手动执行在检查通过后构建按完整 SHA 标记的镜像，通过专用受限 SSH 密钥传到 us1。部署凭据仅保存为 GitHub Secret，宿主密钥固定，不关闭 SSH 主机验证；生产 .env 和 OAuth 凭据保留在服务器。

服务器接收器只接受合法完整 SHA 的发布命令，无交互 shell/端口转发。收到版本后排队，systemd 定时发布器在没有在线玩家和进行中牌局时处理；使用独占锁、临时维护响应、停止应用后备份、切换版本、Compose 健康检查和公网检查。失败切回旧应用与源码，保留数据库备份，不自动恢复数据库或删除生产卷。失败版本不无限重试；新版本可替代旧待发布版本。维护窗口是短暂的单实例重启，不声称零停机、手牌边界热更新、语音无缝重连或不兼容 schema 自动回滚。

配置并实际运行一次 main 工作流，核对线上版本和数据保留。源码测试使用临时目录与隔离 Compose 项目，覆盖队列、忙碌暂缓、成功发布、备份失败与健康失败回滚；不修改生产玩家/牌局数据。既有本地已部署功能提交随 main 工作流发布，两仓保留可追溯计划与代码链接。

## 验收场景

- [x] AC-01: PR 检查不接触部署密钥；main 检查通过后才传输指定 SHA 镜像，失败检查不会发布。
- [x] AC-02: SSH 专用凭据禁止普通 shell 和转发，主机验证保持开启；仓库无真实凭据，生产 .env 保留。
- [x] AC-03: 发布器遇到在线玩家/进行中牌局暂缓，空闲后备份并切换，成功记录版本与结果。
- [x] AC-04: 备份失败不切换版本；新应用健康失败切回旧版、移除维护标记、记录失败，生产卷不删除且数据库不自动恢复。
- [x] AC-05: 工作流上传 GitHub 并实际成功执行，线上健康且版本匹配；运行文档明确手动执行、队列状态、回滚和限制。

## 任务

- [x] T-01: root 实现 .github/workflows/ci-cd.yml、scripts/cd.py、安装脚本和独立部署测试。
- [x] T-02: root 安装服务器接收器/定时发布器/维护 gate，注册专用受限 SSH 密钥与 GitHub Secrets，并验证权限边界。
- [x] T-03: root 运行检查、隔离部署验收、失败回滚演练，推送 main 并确认真实 Actions 与线上版本。
- [x] T-04: root 同步 runtime/workflow 规格与部署说明，完成 SDD 证据及发布记录。

## 审阅结论

已达成目标：Actions 与 us1 的受限接收器、空闲队列、备份和回退已投入运行；main a4a15bf28751d195bbca978a887e1e27d6ab7f00 实际自动发布，非手工切换。

- AC-01/02：审阅 PR/main 条件、contents:read 权限、不可漂移的 checkout SHA、检查在上传之前及 step 级凭据范围。PR 分支不会执行部署步骤，未为验收额外创建 PR。专用 ed25519 私钥仅进入 GitHub Secret；实际使用固定 known_hosts 连接成功，普通 shell 与 TCP 转发均被服务器拒绝。临时本地私钥已删除，生产 .env 的私有摘要比较一致，无凭据进入两仓。
- AC-03/04：最终 Actions 在独立 Docker/PostgreSQL 项目运行 16 项单元测试和真实发布验收通过。实际私人在线房间、离线进行中手牌均阻止发布，空闲后生成 pg_dump 备份、切换镜像和源码、保持登录会话；故意失败的镜像实际回退旧应用并移除维护标记。备份失败、到达竞态、中断恢复和回退失败由单元测试实际覆盖。维护期间只开放 /healthz，页面和 WebSocket 在公网检查通过后才开放。测试卷清理仅限随机隔离项目，生产卷未删除，未自动恢复数据库。
- AC-05：2026-10-01T15:13:10Z，us1 定时发布器在用户退出牌桌后自行部署最终 a4a15bf；[运行 36881976711](https://github.com/li-sky/river-code/actions/runs/36881976711) status=completed、conclusion=success。deployed-version 与应用镜像 revision 均等于完整代码 SHA，本机/公网 healthz=ok、首页 HTTP 200；生产账号和房间 ID 全部保留，数据库容器仍为首次部署实例。两份真实发布备份权限 0600、清单校验通过，队列、维护与事务文件已清除。
- SDD：原生 Windows 无法执行测试中的 POSIX fake-go fixture，失败结果保留；使用未修改的工具与测试，在 Linux 双仓检出执行 19 项 SDD 测试及 links 通过，最终门禁在相同 Linux 检出完成。Go test/vet、前端与生产镜像构建以最终 Actions 为实际证据。

边界已写入运行说明：单实例短暂维护，在线玩家即使不打牌也会使发布等待；无手牌边界热更新、零停机或玩家通知。备份与旧版本保留，容量管理及不兼容 schema 的迁移/恢复仍需管理员处理。后续更新 root 发布器须管理员重新运行安装脚本，应用流水线不自行替换它。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 1,
      "at": "2026-10-01T15:00:16.254571Z",
      "codeCommit": "1350ff348ad813f6d6b058488630e28b2e765e79",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "640b79ed6125ae40db2adcbc0185e2a60e045b289e0cf4a558d306a6730e19a7",
      "specSha256": {
        "runtime": "ce75d68ab5f5a79a28fbc331c53d18b3b90e3da130632ab6785e55ff84f67e22",
        "workflow": "cf4cc75af562ef94deb4d0a12e4a3c664aff98b5c70d12996bae89025506618d"
      },
      "planFingerprint": "e5b430883066084e65ba4426d9b3a6272d1d45c0e0d4ee0a4d1bd22f516eff5c"
    },
    {
      "check": "sdd",
      "commands": [
        {
          "argv": [
            "C:\\Users\\s-k-y\\scoop\\apps\\python\\current\\python.exe",
            "-m",
            "unittest",
            "discover",
            "-s",
            "scripts",
            "-p",
            "test_sdd.py"
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\river-spec",
          "exitCode": 1
        }
      ],
      "exitCode": 1,
      "at": "2026-10-01T15:00:16.533708Z",
      "codeCommit": "1350ff348ad813f6d6b058488630e28b2e765e79",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "640b79ed6125ae40db2adcbc0185e2a60e045b289e0cf4a558d306a6730e19a7",
      "specSha256": {
        "runtime": "ce75d68ab5f5a79a28fbc331c53d18b3b90e3da130632ab6785e55ff84f67e22",
        "workflow": "cf4cc75af562ef94deb4d0a12e4a3c664aff98b5c70d12996bae89025506618d"
      },
      "planFingerprint": "e5b430883066084e65ba4426d9b3a6272d1d45c0e0d4ee0a4d1bd22f516eff5c"
    },
    {
      "check": "backend",
      "commands": [
        {
          "argv": [
            "C:/Users/s-k-y/AppData/Local/Temp/river-go-tools/go/bin/go.exe",
            "version"
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\river-code\\backend",
          "exitCode": 0
        },
        {
          "argv": [
            "C:/Users/s-k-y/AppData/Local/Temp/river-go-tools/go/bin/go.exe",
            "test",
            "./..."
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\river-code\\backend",
          "exitCode": 0
        },
        {
          "argv": [
            "C:/Users/s-k-y/AppData/Local/Temp/river-go-tools/go/bin/go.exe",
            "vet",
            "./..."
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\river-code\\backend",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T15:00:18.179806Z",
      "codeCommit": "1350ff348ad813f6d6b058488630e28b2e765e79",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "640b79ed6125ae40db2adcbc0185e2a60e045b289e0cf4a558d306a6730e19a7",
      "specSha256": {
        "runtime": "ce75d68ab5f5a79a28fbc331c53d18b3b90e3da130632ab6785e55ff84f67e22",
        "workflow": "cf4cc75af562ef94deb4d0a12e4a3c664aff98b5c70d12996bae89025506618d"
      },
      "planFingerprint": "e5b430883066084e65ba4426d9b3a6272d1d45c0e0d4ee0a4d1bd22f516eff5c"
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
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\river-code\\frontend",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T15:00:19.383128Z",
      "codeCommit": "1350ff348ad813f6d6b058488630e28b2e765e79",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "640b79ed6125ae40db2adcbc0185e2a60e045b289e0cf4a558d306a6730e19a7",
      "specSha256": {
        "runtime": "ce75d68ab5f5a79a28fbc331c53d18b3b90e3da130632ab6785e55ff84f67e22",
        "workflow": "cf4cc75af562ef94deb4d0a12e4a3c664aff98b5c70d12996bae89025506618d"
      },
      "planFingerprint": "e5b430883066084e65ba4426d9b3a6272d1d45c0e0d4ee0a4d1bd22f516eff5c"
    },
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T15:00:40.398596Z",
      "codeCommit": "1350ff348ad813f6d6b058488630e28b2e765e79",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "c1b4d83f40542cb13d9710b525fc1848222c3844b5bf610f2b64ab4973830b48",
      "specSha256": {
        "runtime": "ce75d68ab5f5a79a28fbc331c53d18b3b90e3da130632ab6785e55ff84f67e22",
        "workflow": "cf4cc75af562ef94deb4d0a12e4a3c664aff98b5c70d12996bae89025506618d"
      },
      "planFingerprint": "e5b430883066084e65ba4426d9b3a6272d1d45c0e0d4ee0a4d1bd22f516eff5c"
    },
    {
      "check": "sdd",
      "commands": [
        {
          "argv": [
            "C:\\Users\\s-k-y\\scoop\\apps\\python\\current\\python.exe",
            "-m",
            "unittest",
            "discover",
            "-s",
            "scripts",
            "-p",
            "test_sdd.py"
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\river-spec",
          "exitCode": 1
        }
      ],
      "exitCode": 1,
      "at": "2026-10-01T15:00:41.128070Z",
      "codeCommit": "1350ff348ad813f6d6b058488630e28b2e765e79",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "c1b4d83f40542cb13d9710b525fc1848222c3844b5bf610f2b64ab4973830b48",
      "specSha256": {
        "runtime": "ce75d68ab5f5a79a28fbc331c53d18b3b90e3da130632ab6785e55ff84f67e22",
        "workflow": "cf4cc75af562ef94deb4d0a12e4a3c664aff98b5c70d12996bae89025506618d"
      },
      "planFingerprint": "e5b430883066084e65ba4426d9b3a6272d1d45c0e0d4ee0a4d1bd22f516eff5c"
    },
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T15:04:33.882246Z",
      "codeCommit": "cd4d9190911320e3cdee00134288caa9b3e49dde",
      "codeClean": true,
      "toolSha256": "92eaeb143234befefb3f05aa58cfa120cbbdf2ec973c8f18ff1d8e9c94dae768",
      "supportSha256": {
        "scripts/test_sdd.py": "6db367b3d51bc2c7a8142d458cd1485237e005eb635af00984aeaeff837e788e"
      },
      "specMapSha256": "c1b4d83f40542cb13d9710b525fc1848222c3844b5bf610f2b64ab4973830b48",
      "specSha256": {
        "runtime": "bc14b9d95b48a463bd65617d44034a5d2a8c9ff3c2f7bf589e90f0d5986f13f0",
        "workflow": "cf4cc75af562ef94deb4d0a12e4a3c664aff98b5c70d12996bae89025506618d"
      },
      "planFingerprint": "e844f1d1367b579ec484833b77a4c3db96bf25310cd86743a4911ee65d80917a"
    },
    {
      "check": "sdd",
      "commands": [
        {
          "argv": [
            "/usr/bin/python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "scripts",
            "-p",
            "test_sdd.py"
          ],
          "cwd": "/tmp/river-cd-sdd/river-spec",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T15:04:34.053577Z",
      "codeCommit": "cd4d9190911320e3cdee00134288caa9b3e49dde",
      "codeClean": true,
      "toolSha256": "92eaeb143234befefb3f05aa58cfa120cbbdf2ec973c8f18ff1d8e9c94dae768",
      "supportSha256": {
        "scripts/test_sdd.py": "6db367b3d51bc2c7a8142d458cd1485237e005eb635af00984aeaeff837e788e"
      },
      "specMapSha256": "c1b4d83f40542cb13d9710b525fc1848222c3844b5bf610f2b64ab4973830b48",
      "specSha256": {
        "runtime": "bc14b9d95b48a463bd65617d44034a5d2a8c9ff3c2f7bf589e90f0d5986f13f0",
        "workflow": "cf4cc75af562ef94deb4d0a12e4a3c664aff98b5c70d12996bae89025506618d"
      },
      "planFingerprint": "e844f1d1367b579ec484833b77a4c3db96bf25310cd86743a4911ee65d80917a"
    },
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T15:05:25.841341Z",
      "codeCommit": "cd4d9190911320e3cdee00134288caa9b3e49dde",
      "codeClean": true,
      "toolSha256": "92eaeb143234befefb3f05aa58cfa120cbbdf2ec973c8f18ff1d8e9c94dae768",
      "supportSha256": {
        "scripts/test_sdd.py": "6db367b3d51bc2c7a8142d458cd1485237e005eb635af00984aeaeff837e788e"
      },
      "specMapSha256": "013f3b18c676758251819fe3df99fb7cbd20a50c3a3dbff60870713ead1dded0",
      "specSha256": {
        "runtime": "f1ff4d2e85ca0b501ccf3b68918a785cd7ce84479a6911d0aeb20c2d3373f3d8",
        "workflow": "827830aab652a2a919c0e474c17cefda7b444dbd8f76b1d51e2bd781ae41421e"
      },
      "planFingerprint": "e844f1d1367b579ec484833b77a4c3db96bf25310cd86743a4911ee65d80917a"
    },
    {
      "check": "sdd",
      "commands": [
        {
          "argv": [
            "/usr/bin/python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "scripts",
            "-p",
            "test_sdd.py"
          ],
          "cwd": "/tmp/river-cd-sdd/river-spec",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T15:05:26.054188Z",
      "codeCommit": "cd4d9190911320e3cdee00134288caa9b3e49dde",
      "codeClean": true,
      "toolSha256": "92eaeb143234befefb3f05aa58cfa120cbbdf2ec973c8f18ff1d8e9c94dae768",
      "supportSha256": {
        "scripts/test_sdd.py": "6db367b3d51bc2c7a8142d458cd1485237e005eb635af00984aeaeff837e788e"
      },
      "specMapSha256": "013f3b18c676758251819fe3df99fb7cbd20a50c3a3dbff60870713ead1dded0",
      "specSha256": {
        "runtime": "f1ff4d2e85ca0b501ccf3b68918a785cd7ce84479a6911d0aeb20c2d3373f3d8",
        "workflow": "827830aab652a2a919c0e474c17cefda7b444dbd8f76b1d51e2bd781ae41421e"
      },
      "planFingerprint": "e844f1d1367b579ec484833b77a4c3db96bf25310cd86743a4911ee65d80917a"
    },
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T15:09:57.663546Z",
      "codeCommit": "a4a15bf28751d195bbca978a887e1e27d6ab7f00",
      "codeClean": true,
      "toolSha256": "92eaeb143234befefb3f05aa58cfa120cbbdf2ec973c8f18ff1d8e9c94dae768",
      "supportSha256": {
        "scripts/test_sdd.py": "6db367b3d51bc2c7a8142d458cd1485237e005eb635af00984aeaeff837e788e"
      },
      "specMapSha256": "013f3b18c676758251819fe3df99fb7cbd20a50c3a3dbff60870713ead1dded0",
      "specSha256": {
        "runtime": "b25ba3d74bb0ae29b0154aa07e883885e4e7e149e55ce3221c61a877b5bc662b",
        "workflow": "827830aab652a2a919c0e474c17cefda7b444dbd8f76b1d51e2bd781ae41421e"
      },
      "planFingerprint": "e844f1d1367b579ec484833b77a4c3db96bf25310cd86743a4911ee65d80917a"
    },
    {
      "check": "sdd",
      "commands": [
        {
          "argv": [
            "/usr/bin/python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "scripts",
            "-p",
            "test_sdd.py"
          ],
          "cwd": "/tmp/river-cd-sdd/river-spec",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T15:09:57.816959Z",
      "codeCommit": "a4a15bf28751d195bbca978a887e1e27d6ab7f00",
      "codeClean": true,
      "toolSha256": "92eaeb143234befefb3f05aa58cfa120cbbdf2ec973c8f18ff1d8e9c94dae768",
      "supportSha256": {
        "scripts/test_sdd.py": "6db367b3d51bc2c7a8142d458cd1485237e005eb635af00984aeaeff837e788e"
      },
      "specMapSha256": "013f3b18c676758251819fe3df99fb7cbd20a50c3a3dbff60870713ead1dded0",
      "specSha256": {
        "runtime": "b25ba3d74bb0ae29b0154aa07e883885e4e7e149e55ce3221c61a877b5bc662b",
        "workflow": "827830aab652a2a919c0e474c17cefda7b444dbd8f76b1d51e2bd781ae41421e"
      },
      "planFingerprint": "e844f1d1367b579ec484833b77a4c3db96bf25310cd86743a4911ee65d80917a"
    },
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T15:14:54.336273Z",
      "codeCommit": "a4a15bf28751d195bbca978a887e1e27d6ab7f00",
      "codeClean": true,
      "toolSha256": "92eaeb143234befefb3f05aa58cfa120cbbdf2ec973c8f18ff1d8e9c94dae768",
      "supportSha256": {
        "scripts/test_sdd.py": "6db367b3d51bc2c7a8142d458cd1485237e005eb635af00984aeaeff837e788e"
      },
      "specMapSha256": "013f3b18c676758251819fe3df99fb7cbd20a50c3a3dbff60870713ead1dded0",
      "specSha256": {
        "runtime": "e5547d6b7af7860c0879975978506dfd905d1e868e1810116bc205ed636f9246",
        "workflow": "827830aab652a2a919c0e474c17cefda7b444dbd8f76b1d51e2bd781ae41421e"
      },
      "planFingerprint": "e844f1d1367b579ec484833b77a4c3db96bf25310cd86743a4911ee65d80917a"
    },
    {
      "check": "sdd",
      "commands": [
        {
          "argv": [
            "/usr/bin/python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "scripts",
            "-p",
            "test_sdd.py"
          ],
          "cwd": "/tmp/river-cd-sdd/river-spec",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T15:14:54.591085Z",
      "codeCommit": "a4a15bf28751d195bbca978a887e1e27d6ab7f00",
      "codeClean": true,
      "toolSha256": "92eaeb143234befefb3f05aa58cfa120cbbdf2ec973c8f18ff1d8e9c94dae768",
      "supportSha256": {
        "scripts/test_sdd.py": "6db367b3d51bc2c7a8142d458cd1485237e005eb635af00984aeaeff837e788e"
      },
      "specMapSha256": "013f3b18c676758251819fe3df99fb7cbd20a50c3a3dbff60870713ead1dded0",
      "specSha256": {
        "runtime": "e5547d6b7af7860c0879975978506dfd905d1e868e1810116bc205ed636f9246",
        "workflow": "827830aab652a2a919c0e474c17cefda7b444dbd8f76b1d51e2bd781ae41421e"
      },
      "planFingerprint": "e844f1d1367b579ec484833b77a4c3db96bf25310cd86743a4911ee65d80917a"
    }
  ],
  "codeCommit": "a4a15bf28751d195bbca978a887e1e27d6ab7f00",
  "delivery": {
    "status": "released",
    "notes": "GitHub Actions https://github.com/li-sky/river-code/actions/runs/36881976711 completed/success; us1 deployed a4a15bf28751d195bbca978a887e1e27d6ab7f00 at 2026-10-01T15:13:10Z to https://river.skyli.xyz. Production users/rooms and .env retained; validated backups in /opt/river/backups, local/public health ok. Queue, maintenance and transaction cleared."
  }
}
```
