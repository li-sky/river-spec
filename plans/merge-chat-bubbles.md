# 合入聊天气泡与消息菜单 worktree

## 元信息

```json
{
  "id": "merge-chat-bubbles",
  "status": "in_progress",
  "specs": [
    "server",
    "store",
    "table",
    "shared"
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

用户确认将已完成的聊天气泡 worktree 合入 main。代码功能提交 215a1fd3a20f596e96d52533c7c2b839a8187c27，规格分支 b071e87878d5844df45c6f00152450a1ccd955d0；当前代码 main f38e725、规格 main 98f8357，均无未提交改动。

## 预期行为与范围

将两仓 feat/chat-bubbles 合入各自本地 main，保留 main 的房间胜场持久化与单一皇冠、手机座位和公共牌布局。复用 Chatscope 气泡与 Radix 右键/长按菜单的行为、复制/置顶/本人两分钟撤回和服务端权限不变。解决冲突时组合两侧行为与规格，不覆盖主线新能力。安装锁定依赖，以合并 HEAD 验证 test/vet、前端 build、双仓 links 和隔离服务上的双浏览器聊天/置顶验收。仅本地合并，不推送或部署；保留原功能计划的分支验收记录。

## 验收场景

- [ ] AC-01: 两仓 main 包含聊天分支提交，合并无未解决冲突；差异审阅确认聊天菜单/撤回与胜场/单皇冠共存，主线手机布局保留。
- [ ] AC-02: 合并 HEAD 的后端 test/vet、前端 build 与 links 通过；隔离服务双会话验证右键/长按、复制/置顶/撤回及手机布局，置顶回归通过。

## 任务

- [ ] T-01: root 提交集成计划并合并两仓，解决冲突并审阅主线兼容性。
- [ ] T-02: root 安装锁定依赖、以合并代码运行必要检查与双浏览器验收，记录最终合并 SHA 和开发完成/未部署状态。
- [ ] T-03: root 完成 SDD 计划并提交规格，确认两仓 main 工作区清洁。

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
