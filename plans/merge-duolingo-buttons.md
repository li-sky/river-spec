# 将立体按钮与手机触觉反馈合入主线

## 元信息

```json
{
  "id": "merge-duolingo-buttons",
  "status": "done",
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

- [x] AC-01: 两仓 main 包含各自功能分支 HEAD，冲突全部解决，最终工作区干净；聊天等主线能力与按钮/触觉反馈共存。
- [x] AC-02: 合并代码 HEAD 的 links/frontend/media 检查通过；隔离预览执行按钮、模拟触觉双人流程及聊天菜单/置顶/撤回回归，记录实际证据和支持范围。

## 任务

- [x] T-01: 提交集成计划，合并代码与规格分支，审阅差异并处理冲突。
- [x] T-02: 针对合并提交完成必要自动检查与真实浏览器兼容性验收，同步长期规格、记录结果并完成计划。

## 审阅结论

2026-10-01 集成目标达成。代码 main 合并提交 5b1751db96b1b5a53fe7b8b2867c2668971dd0e5，规格 main 合并提交 65fb68dbaf9c0a4e6bda9e0989049c4d179b98ed，均无冲突；merge-base --is-ancestor 验证各自功能分支 HEAD 已纳入 main。代码合并提交 SDD footer 固定指向开工计划 8371d5b16dff619622fbd64eb66dd4d68ebe13b1。分支与 worktree 保留。

差异审阅确认新增改动仅为按钮 CSS、Call/Raise/加注确认的颜色类、独立触觉模块和事件接线、触觉测试/媒体脚本/文档映射；没有改动后端、ChatBubble/ChatMessages 或其他主线功能。聊天组件及依赖、长按/右键菜单、置顶/撤回、胜场统计、手机三加二公共牌与座位布局保留。四份页面规格记录当前集成基线；历史分支计划与其证据保持不变。

以当前合并 HEAD 实际执行 links/frontend/media，全部通过：前端 TypeScript/Vite 构建，7 项原有语音测试与 12 项触觉测试。现有 Emoji 大 chunk 的 Vite 提示保留，构建成功。Windows 临时 SDD 适配器只解析 npm.cmd 和 Git Bash 可执行路径，未修改检查工具与固定 argv。

隔离内存服务 localhost:8099 使用当前 main 构建的前端及之前从主线 f740f5c 编译的 river-chat-merge-preview 后端；已确认此次 merge 相对 f740f5c 没有后端改动。不连接真实数据库，也不替换 8080 服务。实际运行一次性 duolingo-buttons-check-merge.cjs、mobile-haptics-check-merge.cjs 及源码 scripts/chat_check.cjs，全部通过。按钮验收覆盖 1440/768/390/320px、真实双人入座/开局/加注/跟注/过牌/弃牌/聊天、圆角/底边/按压/禁用/焦点和减少动态效果；触觉验收以记录器替代马达 API，验证四节奏、金额拖动/限频/端点、取消/隐藏/离开、重复请求和无 API/异常/减少动态效果降级。

聊天回归实际覆盖 Chatscope 气泡、文本转义、复制、Radix 右键/键盘/原生触摸长按、取消/多指、置顶/取消、撤回双端同步/刷新及头像清除、滚动/外部点击/Escape、断线禁用和 1440/390/320px 布局。代理审阅手机聊天与下注截图，确认输入区、置顶区及按钮可见，无横向溢出。截图与临时脚本保存在 .scratch/duolingo-merge-review 和 .scratch/duolingo-chat-merge-review 等目录，未提交生成产物。

实际 Android 马达触感仍待设备调优，不宣称 iPhone 振动可用；本次没有重验真实 PostgreSQL、OAuth 或公网 TURN。临时 8099 服务验收后已停止，原 8098 worktree 预览保留。本次仅合并本地 main，未推送、部署或改动现有 8080 服务。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T14:03:42.264012Z",
      "codeCommit": "5b1751db96b1b5a53fe7b8b2867c2668971dd0e5",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "a5b0600fff2821da6a225f61b19228ea396de368479a9d7989caebbfacc2ff07",
      "specSha256": {
        "entry": "7df346ed8866f9b0c48d6463df559716101e354430fca8d72de385eb3f8c81f3",
        "lobby": "03eb28b7f8a50dd542dfb97f59a487bf13a4cbd5e7c56fc680312bea526cb7ac",
        "table": "060c1fd51edbfebb1eb66c2230989868d6f40916c980b7acfbc4c70b954e3729",
        "shared": "95f0a6b1a787f1baab6f209ee5cfb6046c039eda4b068b910f0ffa0ca5431060"
      },
      "planFingerprint": "ce03f60aee19dd29fa45276d989fce98face924a01ec2d78118a1f912d50f789"
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
      "at": "2026-10-01T14:03:42.855566Z",
      "codeCommit": "5b1751db96b1b5a53fe7b8b2867c2668971dd0e5",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "a5b0600fff2821da6a225f61b19228ea396de368479a9d7989caebbfacc2ff07",
      "specSha256": {
        "entry": "7df346ed8866f9b0c48d6463df559716101e354430fca8d72de385eb3f8c81f3",
        "lobby": "03eb28b7f8a50dd542dfb97f59a487bf13a4cbd5e7c56fc680312bea526cb7ac",
        "table": "060c1fd51edbfebb1eb66c2230989868d6f40916c980b7acfbc4c70b954e3729",
        "shared": "95f0a6b1a787f1baab6f209ee5cfb6046c039eda4b068b910f0ffa0ca5431060"
      },
      "planFingerprint": "ce03f60aee19dd29fa45276d989fce98face924a01ec2d78118a1f912d50f789"
    },
    {
      "check": "media",
      "commands": [
        {
          "argv": [
            "bash",
            "scripts/test-media.sh"
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\river-code",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T14:03:48.460592Z",
      "codeCommit": "5b1751db96b1b5a53fe7b8b2867c2668971dd0e5",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "a5b0600fff2821da6a225f61b19228ea396de368479a9d7989caebbfacc2ff07",
      "specSha256": {
        "entry": "7df346ed8866f9b0c48d6463df559716101e354430fca8d72de385eb3f8c81f3",
        "lobby": "03eb28b7f8a50dd542dfb97f59a487bf13a4cbd5e7c56fc680312bea526cb7ac",
        "table": "060c1fd51edbfebb1eb66c2230989868d6f40916c980b7acfbc4c70b954e3729",
        "shared": "95f0a6b1a787f1baab6f209ee5cfb6046c039eda4b068b910f0ffa0ca5431060"
      },
      "planFingerprint": "ce03f60aee19dd29fa45276d989fce98face924a01ec2d78118a1f912d50f789"
    }
  ],
  "codeCommit": "5b1751db96b1b5a53fe7b8b2867c2668971dd0e5",
  "delivery": {
    "status": "not_released",
    "notes": ""
  }
}
```
