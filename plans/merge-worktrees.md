# 合并三个功能 worktree 到主线

## 元信息

```json
{
  "id": "merge-worktrees",
  "status": "done",
  "specs": [
    "identity",
    "poker",
    "server",
    "store",
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

用户要求将已完成的多个 worktree 合并进主线。代码与规格各有完整 Emoji、房主置顶消息、当前可见手牌牌型三个分支；主线已有房间可见性与游戏 UI 可读性改进。目标是在保留各功能的前提下完成双仓库 main 集成。

## 预期行为与范围

依次合入 codex/all-emoji、feat/host-pin-message、feat/current-hand-rank 的完整提交历史与对应长期规格。冲突逐段核对，保留 main 的 UI 与已有功能，以及新分支的权限、持久化、私牌隔离和响应式显示。运行后端 test/vet、前端构建、双仓链接及可用的置顶和 Emoji 浏览器集成检查。仅合并本地主线，不推送或部署，不删除 worktree。

## 验收场景

- [x] AC-01: 两仓库 main 均包含三个功能分支 HEAD，工作区干净，无未解决冲突。
- [x] AC-02: 合并差异保留 UI 可读性、完整 Emoji、置顶消息与当前牌型；后端 test/vet、前端构建和双仓链接通过。
- [x] AC-03: 在隔离内存服务执行真实桌面/手机双会话的 Emoji 与置顶消息验收，记录实际结果与限制。

## 任务

- [x] T-01: 核对六个 worktree 的提交和状态，提交集成计划，合并两仓分支并处理冲突。
- [x] T-02: 审阅合并内容，执行集成验证，记录合并提交和检查证据，完成 SDD 门禁。

## 审阅结论

集成目标达成。代码 main 依次产生合并提交 f2bab83（Emoji）、06f2ed4（置顶）、8bdbd38（当前牌型），规格 main 对应合并提交 28adce7、ee375d5、5f864c8。六个分支 HEAD 均被保留为 main 祖先，原 worktree 保留且干净。原主线 UI 提交 3fb5101 和房间可见性提交 92c1891 均保留。

冲突逐段审阅：App.tsx 同时保留 seatPosition、行动等待反馈、聊天可访问性关联和 EmojiChoices/置顶状态；样式删除旧 Emoji 网格但保留主线手机字号与响应式布局；契约和验证文档保留三个功能段落。牌桌规格保留主线 1180px 手机/平板底牌布局，补入当前牌型说明，不沿用独立分支旧 sticky 布局描述。服务端权限、置顶快照保存/回滚及 currentHand 的个性化私牌过滤均与功能分支一致，没有新增产品行为。历史功能计划的检查证据保持原样，本计划记录集成后证据。

AC-02：当前代码 main 的后端 go test ./...、go vet ./...、前端 npm run build 和双仓链接通过。包括置顶权限/持久化/回滚、Emoji 保存边界、当前牌型阶段推进与私牌隔离测试。前端完整 Emoji 懒加载 chunk 的 Vite 体积提示与功能分支一致，构建成功。

AC-03：用当前 main 编译临时执行文件，运行隔离内存服务 http://localhost:8095，未连接现有数据库或替换现有服务。实际执行 scripts/pin_check.cjs 与 scripts/emoji_check.cjs 均通过：桌面 1440×1000、手机 390×844 及房主 390×667 置顶/替换/取消、guest 只读、两端广播、刷新、文本转义、聊天滚动和输入区可用；完整 Emoji 的 3931 个序列符合 API 上限、懒加载、中文搜索、分类和肤色、焦点恢复、双端定向反应、复杂头像保存/刷新/清除及权限/断线保护通过。执行代理查看手机置顶与 Emoji 截图，确认弹窗与聊天输入区没有横向溢出；截图与临时编译产物仅保存 .scratch/merge-review 等隔离目录，不提交。当前牌型的本次证据为后端回归测试与合并差异审阅，没有声称重跑其浏览器牌局验收。真实 PostgreSQL、OAuth、公网 TURN 未在本次重验。未推送、未部署，验收服务结束后停止。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T11:48:11.014696Z",
      "codeCommit": "8bdbd3850d0aaad6efb47053bc22ea77daa1e81c",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "identity": "193b1e1e592e45dcca05e611cfe117bdebe001ff561db00a34a40b87b39a25da",
        "poker": "715b97dc171c5739d8142aabefb62c8571a03306f98d01876e65397eda3953e1",
        "server": "935a4b71b3736d8e45b88ad52a0284af2507a3876e65d9e9efaf61c5fafc3a46",
        "store": "14bb0d8a90eb4bf336d8d66f0225f86e3e782ada61fdb639fbf57b8bcea351dd",
        "shared": "1873beed62c047383ab2f701dbbd0b63797a469e82c8267958f05fea3cd5e71e",
        "table": "e1d6d81e9b021167d35543b020a9bd11c9420ff0e55b855faf3fafc25a764659"
      },
      "planFingerprint": "8424e4955621fc05ead7db4dbb2db3e58a6b62bf3670c6ddb9cf6d3c2340962b"
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
      "at": "2026-10-01T11:48:11.644094Z",
      "codeCommit": "8bdbd3850d0aaad6efb47053bc22ea77daa1e81c",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "identity": "193b1e1e592e45dcca05e611cfe117bdebe001ff561db00a34a40b87b39a25da",
        "poker": "715b97dc171c5739d8142aabefb62c8571a03306f98d01876e65397eda3953e1",
        "server": "935a4b71b3736d8e45b88ad52a0284af2507a3876e65d9e9efaf61c5fafc3a46",
        "store": "14bb0d8a90eb4bf336d8d66f0225f86e3e782ada61fdb639fbf57b8bcea351dd",
        "shared": "1873beed62c047383ab2f701dbbd0b63797a469e82c8267958f05fea3cd5e71e",
        "table": "e1d6d81e9b021167d35543b020a9bd11c9420ff0e55b855faf3fafc25a764659"
      },
      "planFingerprint": "8424e4955621fc05ead7db4dbb2db3e58a6b62bf3670c6ddb9cf6d3c2340962b"
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
      "at": "2026-10-01T11:48:15.531514Z",
      "codeCommit": "8bdbd3850d0aaad6efb47053bc22ea77daa1e81c",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "identity": "193b1e1e592e45dcca05e611cfe117bdebe001ff561db00a34a40b87b39a25da",
        "poker": "715b97dc171c5739d8142aabefb62c8571a03306f98d01876e65397eda3953e1",
        "server": "935a4b71b3736d8e45b88ad52a0284af2507a3876e65d9e9efaf61c5fafc3a46",
        "store": "14bb0d8a90eb4bf336d8d66f0225f86e3e782ada61fdb639fbf57b8bcea351dd",
        "shared": "1873beed62c047383ab2f701dbbd0b63797a469e82c8267958f05fea3cd5e71e",
        "table": "e1d6d81e9b021167d35543b020a9bd11c9420ff0e55b855faf3fafc25a764659"
      },
      "planFingerprint": "8424e4955621fc05ead7db4dbb2db3e58a6b62bf3670c6ddb9cf6d3c2340962b"
    },
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T11:50:17.493208Z",
      "codeCommit": "8bdbd3850d0aaad6efb47053bc22ea77daa1e81c",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "identity": "193b1e1e592e45dcca05e611cfe117bdebe001ff561db00a34a40b87b39a25da",
        "poker": "715b97dc171c5739d8142aabefb62c8571a03306f98d01876e65397eda3953e1",
        "server": "935a4b71b3736d8e45b88ad52a0284af2507a3876e65d9e9efaf61c5fafc3a46",
        "store": "14bb0d8a90eb4bf336d8d66f0225f86e3e782ada61fdb639fbf57b8bcea351dd",
        "shared": "1873beed62c047383ab2f701dbbd0b63797a469e82c8267958f05fea3cd5e71e",
        "table": "e1d6d81e9b021167d35543b020a9bd11c9420ff0e55b855faf3fafc25a764659"
      },
      "planFingerprint": "8424e4955621fc05ead7db4dbb2db3e58a6b62bf3670c6ddb9cf6d3c2340962b"
    }
  ],
  "codeCommit": "8bdbd3850d0aaad6efb47053bc22ea77daa1e81c",
  "delivery": {
    "status": "not_released",
    "notes": ""
  }
}
```
