# 完整 Emoji 选择与发送

## 元信息

```json
{
  "id": "all-emoji",
  "status": "done",
  "specs": [
    "shared",
    "identity",
    "server"
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

用户要求从网上选择公共组件，让表情发送不再限于当前固定的八个 Emoji。头像保存最多 8 个码点的限制会拒绝含肤色的亲吻等组合 Emoji，需要同时兼容完整序列。

## 预期行为与范围

使用兼容 React 19 的 emoji-picker-react，两个表情弹窗共享选择器，支持中文搜索、全分类、肤色与最近使用。组件按需加载、数据随构建提供，发送原始 Unicode 字符。保持系统/房间开关、断线禁用、限流与清除语义；身份保存上限与现有 WS 一致为 16 码点/64 字节，保留 CR/LF/NUL 拒绝。覆盖组件当前数据集，系统字体可能影响新 Emoji 和旗帜显示。本次使用独立代码和规格 worktree，保留并行分支；不部署。

## 验收场景

- [x] AC-01: 电脑与手机弹窗可搜索八个预设之外的 Emoji、切换分类和肤色；无横向溢出，关闭后焦点合理，首次打开按需加载。
- [x] AC-02: 两端实际观察定向反应和复杂肤色组合头像；刷新仍保留头像，清除为空；开关关闭或断线不允许发送/清除。
- [x] AC-03: 后端测试确认复杂序列经 SetEmoji 和 PATCH 保存；超过 16 码点/64 字节与 CR/LF/NUL 仍拒绝，空值可清除。
- [x] AC-04: 差异审阅、links、后端测试/vet 和前端构建通过；同步长期规格、契约与组件来源。

## 任务

- [x] T-01: 在独立 worktree 接入并复用中文选择器，删除旧网格和限制列表，保留交互权限边界。
- [x] T-02: 修正身份层长度限制并验证真实保存与非法输入边界。
- [x] T-03: 用隔离本地服务验收电脑/手机和两端消息，完成规格、组件来源和固定提交证据。

## 审阅结论

执行代理已审阅代码差异并检查手机/桌面截图。两个弹窗复用 emoji-picker-react 4.22.3，中文数据随构建、按需加载；混合肤色从实际点击元素读取完整序列，避免第三方回调重选肤色，关闭后恢复入口焦点。身份层上限与 WS 一致，清除仍允许空值，没有放宽开关、限流或控制字符边界。

AC-01/02：对隔离、内存仓储的 Go 服务 localhost:18081 运行 scripts/emoji_check.cjs，实际 Chrome 两会话（1440×1000、390×844）通过首次打开才加载、中文搜索海豚/亲吻、旗帜分类、肤色选择、无横向溢出、Esc 与焦点恢复、定向飞行 Emoji、10 码点混合肤色头像及刷新读取/清除、另一端撤销权限和 WS 断线禁用。截图位于本机临时目录 river-emoji-artifacts，未提交生成产物；代理已观察搜索和布局。组件数据含 3931 个基础/变体序列，实际遍历最大 10 码点/35 字节，无超过 API 上限的序列。

AC-03：实际运行 go test ./...，TestEmojiSequencesAndLimits 覆盖 SetEmoji/PATCH 的复杂序列、旗帜、清除、边界以及超长/CR/LF/NUL 拒绝后原值保持。AC-04：最终固定提交的 links、go test ./...、go vet ./...、npm run build 均通过，最终提交上的浏览器验收再次通过；SDD 记录见下方，代码提交为 0e8d22b6a6708aaf0777586a8bee305ce8b4f7da。

使用独立 code/spec worktree 的 codex/all-emoji 分支，保留并行主工作区。未部署、未合并。原生字符显示依赖系统字体；数据覆盖范围随组件版本。Vite 对完整选择器约 550 KB（gzip 138 KB）的独立懒加载 chunk 有体积提示，不影响构建与首屏按需加载。真实 PostgreSQL 和生产环境未在本次重验。Windows SDD 使用已有临时 npm.exe 启动器透传实际 npm CLI 参数和退出码，GO_BIN 指向本机真实 Go 编译器。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T11:23:33.696456Z",
      "codeCommit": "0e8d22b6a6708aaf0777586a8bee305ce8b4f7da",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "shared": "ff13244ebe02d7cc6e4c451f592f1c7161d0169e22d8bc369095ba4e49647088",
        "identity": "193b1e1e592e45dcca05e611cfe117bdebe001ff561db00a34a40b87b39a25da",
        "server": "cec4b48d49916caedcf5f335e5d137f6e46b7a149d0351fa899a3762fa62da6d"
      },
      "planFingerprint": "81b9abd9b2804ec9d52c59630be38f3d8b15025f83b6d31ac54807828beddb69"
    },
    {
      "check": "backend",
      "commands": [
        {
          "argv": [
            "C:/Users/s-k-y/AppData/Local/Temp/river-go-tools/go/bin/go.exe",
            "version"
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\emoji\\river-code\\backend",
          "exitCode": 0
        },
        {
          "argv": [
            "C:/Users/s-k-y/AppData/Local/Temp/river-go-tools/go/bin/go.exe",
            "test",
            "./..."
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\emoji\\river-code\\backend",
          "exitCode": 0
        },
        {
          "argv": [
            "C:/Users/s-k-y/AppData/Local/Temp/river-go-tools/go/bin/go.exe",
            "vet",
            "./..."
          ],
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\emoji\\river-code\\backend",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T11:23:34.259617Z",
      "codeCommit": "0e8d22b6a6708aaf0777586a8bee305ce8b4f7da",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "shared": "ff13244ebe02d7cc6e4c451f592f1c7161d0169e22d8bc369095ba4e49647088",
        "identity": "193b1e1e592e45dcca05e611cfe117bdebe001ff561db00a34a40b87b39a25da",
        "server": "cec4b48d49916caedcf5f335e5d137f6e46b7a149d0351fa899a3762fa62da6d"
      },
      "planFingerprint": "81b9abd9b2804ec9d52c59630be38f3d8b15025f83b6d31ac54807828beddb69"
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
          "cwd": "C:\\Users\\s-k-y\\Personal-Project\\river\\.worktrees\\emoji\\river-code\\frontend",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T11:23:35.904759Z",
      "codeCommit": "0e8d22b6a6708aaf0777586a8bee305ce8b4f7da",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "shared": "ff13244ebe02d7cc6e4c451f592f1c7161d0169e22d8bc369095ba4e49647088",
        "identity": "193b1e1e592e45dcca05e611cfe117bdebe001ff561db00a34a40b87b39a25da",
        "server": "cec4b48d49916caedcf5f335e5d137f6e46b7a149d0351fa899a3762fa62da6d"
      },
      "planFingerprint": "81b9abd9b2804ec9d52c59630be38f3d8b15025f83b6d31ac54807828beddb69"
    }
  ],
  "codeCommit": "0e8d22b6a6708aaf0777586a8bee305ce8b4f7da",
  "delivery": {
    "status": "not_released",
    "notes": ""
  }
}
```
