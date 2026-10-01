# 牌桌获胜次数与单一皇冠标记

## 元信息

```json
{
  "id": "table-win-counter",
  "status": "done",
  "specs": [
    "table",
    "server",
    "store"
  ],
  "risk": "storage",
  "checks": [
    "links",
    "backend",
    "frontend"
  ]
}
```

## 问题与目标

同一玩家同时出现房主与本手赢家两个皇冠，含义混淆；用户希望皇冠旁显示每位桌上玩家的获胜次数。增加服务器负责的每桌累计赢牌次数，并统一皇冠含义。

## 预期行为与范围

每桌按身份累计获胜手数；服务器结算 winners 中金额大于零的身份，每手各记一次，主池／边池重复身份去重，平分赢家各记一次。每位入座玩家显示单一皇冠及次数（含零），本手赢家高亮；房主改成“主”文字标记并保留完整房主可读名称。计数随房间私有快照保存，刷新、断线、离座、离开再进入及服务重启保持，同一身份新房间从零开始。旧快照没有统计时从零开始，已结束旧手牌不追溯，进行中的手牌结束后计入；没有完整历史不能回填。客户端不能设置计数。保存失败回滚计数和完成标记，重试只计一次。保留手机3+2公共牌及既有行动规则，不新增SQL表。

## 验收场景

- [x] AC-01: 普通行动、全下与超时结算只给真实服务器赢家加一次；分池／边池不重复，未结束牌局与状态刷新不增加。
- [x] AC-02: 保存失败可回滚并重试；计数与完成标记从快照恢复，旧已结束快照不回填，旧进行中牌局正常计入，离开再加入同房间保留。
- [x] AC-03: 所有入座玩家皇冠旁可见次数且每人只有一个皇冠，房主显示文字标记；本手赢家高亮，320/390px与桌面文字、头像和公开底牌不互相遮挡，刷新显示一致。

## 任务

- [x] T-01: 实现房间统计、公开玩家次数与快照恢复／回滚。
- [x] T-02: 修改皇冠、房主标记与紧凑计数样式，覆盖服务端边界和真实浏览器牌局。
- [x] T-03: 更新契约与长期规格，执行必需检查并更新本地预览。

## 审阅结论

审阅通过：服务器在结算同步筹码时更新按身份的房间获胜统计，并将完成标记与计数保存在同一快照／回滚边界；公开状态仅暴露玩家 wins。客户端没有统计写入接口，房主标记改成可读文字，每位座位只保留一个皇冠计数。旧已结束牌局不追溯，旧进行中手牌结算后计入，完整历史缺失的限制已明确。

实际服务端证据：internal/server/wins_test.go 执行普通弃牌、两手累计、超时、真实皇家同花顺分池、不同主池／边池赢家、同一赢家包揽主池／边池、盲注直接全下、重复读取／同步、动作保存失败及重试、超时保存失败及重试、快照恢复、旧已完成／进行中快照及私有统计隔离。

实际浏览器证据：scripts/compact_ui_check.cjs 使用真实独立内存服务，核对每次完整手牌的服务器计数；皇冠数量与房主文字、刷新、明确退出再入座的计数保留、新房间零次均通过，并回归固定动作、抽屉手势、金额预设、短全下、聊天／置顶及320/390/768/1440px布局。scripts/mobile_table_check.cjs 在另一独立服务实际完成6/8/9人全下摊牌，检查320/390/600px计数角标、玩家内容和中央3+2公共牌／结算互不重叠；查看 .scratch/wins-mobile-review 的截图。

实际持久化证据：临时、隔离 PostgreSQL 17 数据库和独立8094房间服务执行 .scratch/wins-postgres-check.cjs seed/verify，以真实会话完成弃牌结算后停止进程，使用同一数据库启动新进程。两名玩家原会话与精确计数恢复、已完成手牌不重复累计、单皇冠显示均通过；测试数据库与临时服务随后清理。未对真实移动设备、读屏软件、公网语音或OAuth追加专项验收。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T13:38:58.273127Z",
      "codeCommit": "f38e725aaf83a9e5ad0a60f5c28a83acd3eec739",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "table": "e96bd4eaea04d28654ef9780283969aadccbcd31a3fbca6747fddfd3c956d4d4",
        "server": "4447eb533b012b3989f3a0925b6f149c7a865f1c7f74673f4c6c3ed66912b570",
        "store": "08d87a2ddb0e2e4d8fca70147e54eb95e0e0b58ae54a66f1c97e82e030940f2f"
      },
      "planFingerprint": "b84edeee26c91c6fdc076d48ebb48b33b464f37be0e2a158e694f3d467af6d56"
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
      "at": "2026-10-01T13:38:58.907830Z",
      "codeCommit": "f38e725aaf83a9e5ad0a60f5c28a83acd3eec739",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "table": "e96bd4eaea04d28654ef9780283969aadccbcd31a3fbca6747fddfd3c956d4d4",
        "server": "4447eb533b012b3989f3a0925b6f149c7a865f1c7f74673f4c6c3ed66912b570",
        "store": "08d87a2ddb0e2e4d8fca70147e54eb95e0e0b58ae54a66f1c97e82e030940f2f"
      },
      "planFingerprint": "b84edeee26c91c6fdc076d48ebb48b33b464f37be0e2a158e694f3d467af6d56"
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
      "at": "2026-10-01T13:39:01.664252Z",
      "codeCommit": "f38e725aaf83a9e5ad0a60f5c28a83acd3eec739",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "table": "e96bd4eaea04d28654ef9780283969aadccbcd31a3fbca6747fddfd3c956d4d4",
        "server": "4447eb533b012b3989f3a0925b6f149c7a865f1c7f74673f4c6c3ed66912b570",
        "store": "08d87a2ddb0e2e4d8fca70147e54eb95e0e0b58ae54a66f1c97e82e030940f2f"
      },
      "planFingerprint": "b84edeee26c91c6fdc076d48ebb48b33b464f37be0e2a158e694f3d467af6d56"
    }
  ],
  "codeCommit": "f38e725aaf83a9e5ad0a60f5c28a83acd3eec739",
  "delivery": {
    "status": "not_released",
    "notes": "本地 Docker app 已更新至当前代码，http://localhost:8080/healthz 为200，HTML载入 index-Ca6RKlir.js 与 index-sldYBx-t.css。原 PostgreSQL 数据保留。隔离测试数据库及8092/8093/8094临时服务已清理。未发布公网。"
  }
}
```
