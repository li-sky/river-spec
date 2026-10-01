# 合并三个功能 worktree 到主线

## 元信息

```json
{
  "id": "merge-worktrees",
  "status": "in_progress",
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

- [ ] AC-01: 两仓库 main 均包含三个功能分支 HEAD，工作区干净，无未解决冲突。
- [ ] AC-02: 合并差异保留 UI 可读性、完整 Emoji、置顶消息与当前牌型；后端 test/vet、前端构建和双仓链接通过。
- [ ] AC-03: 在隔离内存服务执行真实桌面/手机双会话的 Emoji 与置顶消息验收，记录实际结果与限制。

## 任务

- [ ] T-01: 核对六个 worktree 的提交和状态，提交集成计划，合并两仓分支并处理冲突。
- [ ] T-02: 审阅合并内容，执行集成验证，记录合并提交和检查证据，完成 SDD 门禁。

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
