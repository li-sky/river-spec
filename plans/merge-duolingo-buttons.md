# 将立体按钮与手机触觉反馈合入主线

## 元信息

```json
{
  "id": "merge-duolingo-buttons",
  "status": "in_progress",
  "specs": [
    "entry",
    "lobby",
    "table",
    "shared"
  ],
  "risk": "media",
  "checks": [
    "links",
    "frontend",
    "media"
  ]
}
```

## 问题与目标

用户要求将当前 worktree 的立体按钮与手机触觉反馈合入主线。代码功能分支 feat/duolingo-buttons 为 356cf3f，规格 plan/duolingo-buttons 为 0ea4851；代码 main 当前 f740f5c、规格 main 当前 5e64842，均已集成新的聊天气泡与消息菜单且工作区干净。

## 预期行为与范围

将两个功能分支的提交历史合入各自本地 main，保留已有聊天气泡、右键/长按菜单、置顶/撤回、胜场及移动布局。审阅冲突并组合两侧内容。验证合并 HEAD 的前端构建、媒体测试、双仓链接及隔离服务的按钮、模拟触觉与聊天兼容性。仅合并本地主线，不推送或部署现有 8080 服务；保留功能分支与 worktree。真实手机马达手感、iPhone 不支持 Vibration API 的限制保持原记录。

## 验收场景

- [ ] AC-01: 两仓 main 包含各自功能分支 HEAD，冲突全部解决，最终工作区干净；聊天等主线能力与按钮/触觉反馈共存。
- [ ] AC-02: 合并代码 HEAD 的 links/frontend/media 检查通过；隔离预览执行按钮、模拟触觉双人流程及聊天菜单/置顶/撤回回归，记录实际证据和支持范围。

## 任务

- [ ] T-01: 提交集成计划，合并代码与规格分支，审阅差异并处理冲突。
- [ ] T-02: 针对合并提交完成必要自动检查与真实浏览器兼容性验收，同步长期规格、记录结果并完成计划。

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
