# 压缩牌桌信息密度与固定行动栏

## 元信息

```json
{
  "id": "compact-table-ui",
  "status": "done",
  "specs": [
    "table",
    "shared",
    "server"
  ],
  "risk": "ui",
  "checks": [
    "links",
    "frontend",
    "backend"
  ]
}
```

## 问题与目标

用户通过两张手机截图指出房间页重复导航、等待卡片、常驻加注控件与说明文字占用过多空间。目标是紧凑房间顶栏、左右抽屉、始终显示的四按钮操作底栏与加注弹窗。

## 预期行为与范围

房间页顶栏左侧为抽屉按钮，房间名下两行显示盲注及连接/可见性，右侧为无设置标的头像、分享、暂离/返回、退出房间、玩法简介。管理和语音收进左侧抽屉，聊天从右侧划出，支持边缘滑动打开及反向关闭，保留键盘焦点和 Escape。删除牌桌下方发牌/筹码宣传条。固定底栏始终显示 Call、Raise、Check、Fold，不合法或未轮到时禁用；等待/开局为一行，底牌保持可见且预留底栏高度。Raise 打开滑块和数字输入弹窗，25/50/75% 为底池比例的加注，限制至合法范围，All-in 设置最高金额；短筹码全下和未重开加注遵循现有服务端权限。新增本人 sitout 布尔命令保留座位/筹码并跳过下一手，当前手继续正常行动；不改变结算或行动令牌。完成本地验证与双仓提交，不推送生产。

## 验收场景

- [x] AC-01: 桌面、390px、320px 顶栏无横向溢出，房间信息和全部入口可见；底栏滚动后仍显示四个动作且无独立 All-in。
- [x] AC-02: 左右抽屉方向正确，点击/滑动/遮罩/Escape 可开关，焦点恢复；聊天消息与置顶功能可用。
- [x] AC-03: 真实双人牌局验证跟注、过牌、弃牌、普通加注和短全下；百分比、输入边界、过期行动关闭弹窗及等待状态正确。
- [x] AC-04: 暂离保留座位与筹码、排除下一手，恢复重新参与；旁观者不能暂离，进行中暂离不改变本手。
- [x] AC-05: 后端 test/vet、前端构建与 links 检查通过，长期规格与契约同步并记录实际证据。

## 任务

- [x] T-01: 实现紧凑顶栏、可滑动抽屉、固定四动作底栏和加注弹窗。
- [x] T-02: 实现并验证本人暂离/恢复，保留服务端权限及牌局边界。
- [x] T-03: 实际浏览器验证、多端截图审阅、同步规格、执行 SDD 收尾。

## 审阅结论

差异审阅完成：房间导航、底栏和抽屉仅改变展示与操作入口；Raise 仍提交服务端整数总额／allin 和最新 turnToken，服务端继续校验 canRaise。sitout 仅修改本人既有快照标记，当前手保持不变。

- AC-01：真实 Chrome 在 1440、768、390、320px 检查顶栏、按钮几何及页面宽度。手机顶栏约 101px；四按钮固定，主要动作高度约 52px，导航图标 44px。九人桌可滚到底，底栏动态预留空间；未宣称九人手机桌无需滚动。
- AC-02：点击左菜单、右聊天及模拟 TouchEvent 边缘滑动开关通过；Escape 返回原按钮焦点。右侧聊天有界全屏高度，发送及房主置顶后另一会话可读取，访客无取消权限。目视检查左右抽屉和金额弹窗截图。滑动为浏览器触摸事件模拟，未运行实体手机或系统边缘手势专项验证。
- AC-03：独立内存服务 localhost:8092 上真实双人牌局完成普通加注、Call、Check、Fold、All-in 和 30 总额短全下；25/50/75% 限制金额正确，小数及超额禁用，滑块键盘加一，过期行动关闭弹窗。localhost:8093 以 800ms WebSocket 下游延迟检查提交等待期间四按钮禁用，状态更新恢复；显式关闭测试 WebSocket 并模拟离线后禁用，恢复网络重连正常。九人头像在四种宽度无相交，本人筹码滚到底不被底栏遮挡，无 pageerror。
- AC-04：双浏览器实际暂离／恢复保留座位与筹码，房主不足两人不可开局；进行中暂离不更换行动令牌。服务端测试补充快照、他人目标忽略、旁观者拒绝和保存失败不广播。
- AC-05：最终 SDD links、frontend、backend 的已提交 HEAD 证据见下方。截图位于源码仓库外的 .scratch/compact-ui-review，延迟代理同在 .scratch，未提交生成物、会话或真实牌局资料；脚本源码 scripts/compact_ui_check.cjs 可复用。浏览器服务使用内存存储，未扩大为真实 PostgreSQL 故障、公网语音、OAuth 或实体软键盘验收。

开发验收通过；完成本机 localhost:8080 的 Docker 更新与健康检查，数据库容器／卷保持原样；未推送或发布生产。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 1,
      "at": "2026-10-01T12:51:44.344974Z",
      "codeCommit": "23f4a521d52202e871c1a2e28a3729d7bd7e4938",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8a72903ba1fe915e4bf77976b65999f5f0ca78116a28383376282d07433e5d38",
      "specSha256": {
        "table": "3bda6208c337d56086f6b63ade34012b7caccb1d3f24d86a500317cb2a877e96",
        "shared": "9ef17ee80cd4ee91b9e65955ab590c575e4666ba8e50a030c32676b12eb925da",
        "server": "af66fec9b7c3054acf997733a57b659ec36a1cdaba698d03f36df5531835f3c6"
      },
      "planFingerprint": "35c368d825a2ec95b0b9d823a9fecd5f90953b8d49045be764b3fd39cf37d6a4"
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
      "at": "2026-10-01T12:51:44.606276Z",
      "codeCommit": "23f4a521d52202e871c1a2e28a3729d7bd7e4938",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8a72903ba1fe915e4bf77976b65999f5f0ca78116a28383376282d07433e5d38",
      "specSha256": {
        "table": "3bda6208c337d56086f6b63ade34012b7caccb1d3f24d86a500317cb2a877e96",
        "shared": "9ef17ee80cd4ee91b9e65955ab590c575e4666ba8e50a030c32676b12eb925da",
        "server": "af66fec9b7c3054acf997733a57b659ec36a1cdaba698d03f36df5531835f3c6"
      },
      "planFingerprint": "35c368d825a2ec95b0b9d823a9fecd5f90953b8d49045be764b3fd39cf37d6a4"
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
      "at": "2026-10-01T12:51:49.539729Z",
      "codeCommit": "23f4a521d52202e871c1a2e28a3729d7bd7e4938",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8a72903ba1fe915e4bf77976b65999f5f0ca78116a28383376282d07433e5d38",
      "specSha256": {
        "table": "3bda6208c337d56086f6b63ade34012b7caccb1d3f24d86a500317cb2a877e96",
        "shared": "9ef17ee80cd4ee91b9e65955ab590c575e4666ba8e50a030c32676b12eb925da",
        "server": "af66fec9b7c3054acf997733a57b659ec36a1cdaba698d03f36df5531835f3c6"
      },
      "planFingerprint": "35c368d825a2ec95b0b9d823a9fecd5f90953b8d49045be764b3fd39cf37d6a4"
    },
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T12:52:03.489870Z",
      "codeCommit": "23f4a521d52202e871c1a2e28a3729d7bd7e4938",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "table": "3bda6208c337d56086f6b63ade34012b7caccb1d3f24d86a500317cb2a877e96",
        "shared": "9ef17ee80cd4ee91b9e65955ab590c575e4666ba8e50a030c32676b12eb925da",
        "server": "af66fec9b7c3054acf997733a57b659ec36a1cdaba698d03f36df5531835f3c6"
      },
      "planFingerprint": "35c368d825a2ec95b0b9d823a9fecd5f90953b8d49045be764b3fd39cf37d6a4"
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
      "at": "2026-10-01T12:52:04.048785Z",
      "codeCommit": "23f4a521d52202e871c1a2e28a3729d7bd7e4938",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "table": "3bda6208c337d56086f6b63ade34012b7caccb1d3f24d86a500317cb2a877e96",
        "shared": "9ef17ee80cd4ee91b9e65955ab590c575e4666ba8e50a030c32676b12eb925da",
        "server": "af66fec9b7c3054acf997733a57b659ec36a1cdaba698d03f36df5531835f3c6"
      },
      "planFingerprint": "35c368d825a2ec95b0b9d823a9fecd5f90953b8d49045be764b3fd39cf37d6a4"
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
      "at": "2026-10-01T12:52:09.000117Z",
      "codeCommit": "23f4a521d52202e871c1a2e28a3729d7bd7e4938",
      "codeClean": true,
      "toolSha256": "10aeba2e58796ab1873aca85c59ecdbfb001bdd2cb50bd1d89d0d53ff03280d3",
      "supportSha256": {
        "scripts/test_sdd.py": "eaa18e458a0f3ae9921bb76d3ef1e8d61f91abc732c9e938bab3610e168de75b"
      },
      "specMapSha256": "8e87e6639ba8df0e31d770d69c7a469f97e16e6e5b1720a6ec8ead7545a96522",
      "specSha256": {
        "table": "3bda6208c337d56086f6b63ade34012b7caccb1d3f24d86a500317cb2a877e96",
        "shared": "9ef17ee80cd4ee91b9e65955ab590c575e4666ba8e50a030c32676b12eb925da",
        "server": "af66fec9b7c3054acf997733a57b659ec36a1cdaba698d03f36df5531835f3c6"
      },
      "planFingerprint": "35c368d825a2ec95b0b9d823a9fecd5f90953b8d49045be764b3fd39cf37d6a4"
    }
  ],
  "codeCommit": "23f4a521d52202e871c1a2e28a3729d7bd7e4938",
  "delivery": {
    "status": "not_released",
    "notes": "本机 localhost:8080 Docker 已重建，应用与数据库健康，保留原数据库卷。未推送或发布生产。"
  }
}
```
