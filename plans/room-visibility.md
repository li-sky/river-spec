# 支持公开与私人房间

## 元信息

```json
{
  "id": "room-visibility",
  "status": "done",
  "specs": [
    "server",
    "lobby",
    "shared",
    "table"
  ],
  "risk": "service",
  "checks": [
    "links",
    "backend",
    "frontend"
  ]
}
```

## 问题与目标

用户要求区分公开与私人房间。当前所有房间均在认证后的大厅公开，创建与设置无法选择可见性；目标是支持公开发现和仅链接邀请的私人牌桌。

## 预期行为与范围

RoomSettings 新增必填 visibility（public/private）。用户明确要求不保留兼容性：创建、设置请求及快照必须包含有效值，缺失、空值或非法值拒绝，不迁移旧快照。前端新建表单初始选择 public。GET /api/rooms 只返回公开房间，包括对房主自己也隐藏私人房间。私人房间使用已有随机 128 位房间 ID 的链接作为邀请，认证后可读取并通过 WS 加入；所有持链接用户都能加入，没有逐人邀请名单或每房间密码。创建和房主设置使用共享选择器并解释公开/私人差异；牌桌显示当前可见性，沿用邀请链接复制。房主在两手之间可切换，保存失败回滚，非房主不得修改；链接及已有成员不因切换失效。设置存入现有快照，无 SQL 迁移。

## 验收场景

- [x] AC-01: HTTP 创建公开与私人房间；认证大厅仅返回公开房间，缺失、空值或非法 visibility 返回 400，匿名访问仍返回 401。
- [x] AC-02: 第二个身份持私人房间链接可以读取及 WS 加入；私人房间不会出现在任一身份的大厅，状态继续按用户过滤。
- [x] AC-03: 非房主切换被拒绝；房主两手之间切换影响列表并广播状态，进行中不能切换；存储失败时可见性及广播回滚；缺失、空值和非法可见性设置命令被拒绝。
- [x] AC-04: 重启快照恢复保留私人设置；缺失、空值或非法 visibility 的快照被拒绝，不提供旧数据迁移。
- [x] AC-05: 浏览器实际创建私人房间、检查第二个身份大厅隐藏、链接加入、房主切换公开及大厅刷新；桌面和手机选择器及牌桌标记无横向溢出。

## 任务

- [x] T-01: root 修改服务端必填设置验证、恢复校验、列表过滤并添加权限/恢复/失败验收测试。
- [x] T-02: root 修改前端共享设置、默认类型、大厅文案及牌桌可见性标记并实际浏览器验收。
- [x] T-03: root 同步契约和 server/lobby/shared/table 长期规格，审阅差异、提交代码并执行 links/backend/frontend，完成计划。

## 审阅结论

root 已审阅最终差异，目标达成；代码提交为 92c18911c8ae6198441f7833e25b7588a8478af1，按用户要求没有新增可见性兼容回退。AC-01/02：TestRoomVisibilityHTTPAndLinkJoin 实际验证两种房间创建、缺失/空/非法值返回 400、两个身份列表隐藏、匿名 401、认证私人链接读取与 WS 旁观加入；个性化私牌隔离由本次同时运行的 TestHostPermissionsAndHandPrivacy 验证。AC-03：TestRoomVisibilitySettingsPermissionsAndBroadcast、TestRoomVisibilityPersistenceFailure 实际验证房主权限、缺字段拒绝、非法值回滚、广播、列表切换、进行中限制和保存失败保持私人且无广播。AC-04：TestRoomVisibilityRecovery 实际验证 public/private 内存快照恢复与缺失/空/非法快照拒绝。AC-05：对隔离的实际 Go 服务运行 visibility_check.cjs，Chrome 桌面 1440×1000、手机 390×844 三个独立会话验证创建、邀请链接先登录、加入、标记广播、公开/私人切换、大厅轮询、刷新及手机房主设置；无页面异常及横向溢出。执行代理已查看手机创建、牌桌和设置截图，确认选择器文字可读且牌桌标记可见。

同步 HTTP 契约、server/lobby/shared/table 长期规格和现有验收脚本的必填字段。权限与恢复变更没有改 SQL schema；本次恢复测试使用内存仓储，真实 PostgreSQL 未重新验证。未部署，旧快照无 visibility 会拒绝启动恢复，不进行自动迁移。Windows SDD frontend profile 使用临时 npm.exe 启动器调用已安装的 D:/node.exe 与真实 npm CLI，透传参数与退出码；未修改 SDD 工具或伪造检查结果。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T11:01:33.063348Z",
      "codeCommit": "92c18911c8ae6198441f7833e25b7588a8478af1",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "b4d5772649036f685f3f70c7a1bf2789d50dfd47af67f06a952a39a810d8def6",
      "specSha256": {
        "server": "338397d48f822b1c99cbb4883777a32d9a7fba12de749810c0cb5e7aa451c88a",
        "lobby": "7020dcd81d63d9249163fdd99d146c4c7d0b6350a9f6efbf35689182b231e28f",
        "shared": "0aa188a837a915009eef8b44595c3d65a070a0846b3e3f480a3099e65560cf5b",
        "table": "2baef35588905a83de776e18e5534bae6b978e4786b41bb98431e9a211da8da3"
      },
      "planFingerprint": "3ad4951b102dd345f82ef469021a6c0869c62a87eb2952bc96fb7db97fbffe64"
    },
    {
      "check": "backend",
      "commands": [
        {
          "argv": [
            "C:\\Users\\s-k-y\\AppData\\Local\\Temp\\river-go-tools\\go\\bin\\go.exe",
            "version"
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\river-code\\backend",
          "exitCode": 0
        },
        {
          "argv": [
            "C:\\Users\\s-k-y\\AppData\\Local\\Temp\\river-go-tools\\go\\bin\\go.exe",
            "test",
            "./..."
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\river-code\\backend",
          "exitCode": 0
        },
        {
          "argv": [
            "C:\\Users\\s-k-y\\AppData\\Local\\Temp\\river-go-tools\\go\\bin\\go.exe",
            "vet",
            "./..."
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\river-code\\backend",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T11:01:33.598654Z",
      "codeCommit": "92c18911c8ae6198441f7833e25b7588a8478af1",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "b4d5772649036f685f3f70c7a1bf2789d50dfd47af67f06a952a39a810d8def6",
      "specSha256": {
        "server": "338397d48f822b1c99cbb4883777a32d9a7fba12de749810c0cb5e7aa451c88a",
        "lobby": "7020dcd81d63d9249163fdd99d146c4c7d0b6350a9f6efbf35689182b231e28f",
        "shared": "0aa188a837a915009eef8b44595c3d65a070a0846b3e3f480a3099e65560cf5b",
        "table": "2baef35588905a83de776e18e5534bae6b978e4786b41bb98431e9a211da8da3"
      },
      "planFingerprint": "3ad4951b102dd345f82ef469021a6c0869c62a87eb2952bc96fb7db97fbffe64"
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
      "at": "2026-10-01T11:01:35.965807Z",
      "codeCommit": "92c18911c8ae6198441f7833e25b7588a8478af1",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "b4d5772649036f685f3f70c7a1bf2789d50dfd47af67f06a952a39a810d8def6",
      "specSha256": {
        "server": "338397d48f822b1c99cbb4883777a32d9a7fba12de749810c0cb5e7aa451c88a",
        "lobby": "7020dcd81d63d9249163fdd99d146c4c7d0b6350a9f6efbf35689182b231e28f",
        "shared": "0aa188a837a915009eef8b44595c3d65a070a0846b3e3f480a3099e65560cf5b",
        "table": "2baef35588905a83de776e18e5534bae6b978e4786b41bb98431e9a211da8da3"
      },
      "planFingerprint": "3ad4951b102dd345f82ef469021a6c0869c62a87eb2952bc96fb7db97fbffe64"
    }
  ],
  "codeCommit": "92c18911c8ae6198441f7833e25b7588a8478af1",
  "delivery": {
    "status": "local_running",
    "notes": "2026-10-01（Asia/Shanghai）按用户要求删除 river-code 的 app/db 旧容器并重建，保留 postgres_data 卷；部署前确认数据库房间数为 0。docker compose up -d --build --wait 成功，镜像 sha256:ae111f51f3a9de2007bd3d27d3fc8df8ca041e9a4e70c0c743281ba28ea8648a，app/db 均 healthy。http://localhost:8080 的 healthz、首页和 JS 资源均返回 200，实际资源包含公开／私人设置 UI；未发布生产环境。"
  }
}
```
