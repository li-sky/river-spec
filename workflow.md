# RIVER SDD 开发与朋友试玩迭代流程

RIVER 使用参考 Warp 工作方式的长期模块/页面规格，以及每次变更一份 `plans/<slug>.md`。规格保存已确认需求与当前基线，计划保存本次目标、预期行为、任务、验收及证据；不使用 OpenSpec 四文件结构，也不要求安装 Warp 或 OpenSpec。

本仓库的 SDD 执行工具管理计划与检查证据。产品内反馈入口、统一开发启动、安全热重载、试玩版本提醒和自动发布仍属后续方案，不能因为工具能执行检查就登记为已实现。

## 双仓库与术语

[river-spec](https://github.com/li-sky/river-spec) 保存长期规格、计划、映射与 SDD 工具；[river-code](https://github.com/li-sky/river-code) 保存产品源码、测试、构建和部署。默认把两仓库检出为同级目录 `river-spec/`、`river-code/`；其他布局使用 `--code-dir` 显式指定。

先读 [README](README.md) 与 [spec-map.json](spec-map.json)，用映射 key 找到模块/页面及源码。系统本身的配置称“配置”；用户和房间的选择称“设置”。host 是房主，guest 是加入房间的人；访客身份、旁观状态分别描述。

需求与代码冲突时先核对用户已确认意图，不能把源码缺陷写成既定需求。分清“已实现”“测试源码有覆盖”“本次实际验收通过”“后续计划”；分享文档链接与授予仓库访问权限是独立操作。

## 一次新改进，按五步完成

以下示例在 `river-spec/` 根目录执行，计划涉及牌桌 UI。`table` 是现有映射 key；其他模块可重复传入 `--spec`。slug 使用稳定的简短标识，创建后不要随意改名。

### 1. 建立计划并写清验收

```bash
python3 scripts/sdd.py new table-action-label --title "说明牌桌行动按钮的金额" --spec table --risk ui
```

编辑生成的 `plans/table-action-label.md`，填写问题与目标、预期行为与范围、AC 验收场景及 T 任务，替换这些部分的 TODO。只在计划描述预期，先保留长期规格的实际基线，避免未实现的行为被读者当作事实。复杂变化写清失败边界、接口、权限、兼容性和恢复结果；小文案无需增加镜像实现的测试。

### 2. 校验、开工，先提交计划

```bash
python3 scripts/sdd.py check plans/table-action-label.md
python3 scripts/sdd.py start plans/table-action-label.md
git add plans/table-action-label.md
git commit -m "plan: describe table action labels"
git rev-parse HEAD
```

`check` 校验计划结构、映射、风险及检查要求，不代替运行产品检查。`start` 将有效 draft 计划转为 in_progress。两者要求需求、范围、AC/T 文本不再是占位；审阅结论可以仍为 TODO/待审阅，验证记录可以为空。记录此时规格仓库的提交 SHA，用于下一步代码提交的 footer。这里是对已授权工作的具体化，不要求每个任务重新询问用户批准。

### 3. 按计划实现并提交代码

代理读取相关规格与代码后实现。多代理分工必须明确文件所有权、共享接口与依赖；避免同时修改同一文件；root 负责合并接口、检查行为和最终集成。规则、权限、私牌隔离、断线恢复及存储变化要设计能发现错误的验收，不能仅添加重复实现的测试。

代码提交使用固定格式的 footer，链接到**开工时已提交**的计划版本。将下方 `<spec-commit>` 替换为步骤 2 的真实 SHA：

```text
SDD-Plan: https://github.com/li-sky/river-spec/blob/<spec-commit>/plans/table-action-label.md
```

提交代码前可先运行检查；`run` 允许代码工作区有改动，但会记录 `codeClean=false`，这类结果不能作为 finish 证据。代码正式提交后必须针对该 HEAD 重新运行需要的检查。

### 4. 实际验收、更新基线，运行检查

按 AC 观察行为并记录证据，完成的 AC/T 才勾选。CLI 不会自动判断人工场景通过：例如手机竖屏、多人语音、断线恢复或权限边界，需要人或执行代理实际验证并说明条件和结果。外部场景尚未验证就保留未完成，不用构建成功替代。

实现完成后同步对应长期规格、契约和必要映射中的源码基线，再运行全部必需检查。以 UI 示例：

```bash
python3 scripts/sdd.py run plans/table-action-label.md --check links --check frontend
```

可省略 `--check` 运行计划所列检查，或重复参数选择固定 profile；不能把任意 shell 命令写入计划要求 CLI 执行。必要时添加其他检查，同时保留风险等级的最低要求。修改长期规格后必须重跑需要的检查，旧规格内容的验证证据不能用于收尾。

### 5. 审阅、完成计划，独立决定发布

在“审阅结论”补记差异审阅、实际 AC 证据、限制及明确结论，确认 AC/T 全部完成，然后执行：

```bash
python3 scripts/sdd.py finish plans/table-action-label.md
git add plans/table-action-label.md pages/03-table.sdd.md spec-map.json
git commit -m "spec: complete table action labels"
```

`finish` 通过完成门禁后才将状态改为 done；最终规格提交保存更新后的基线、运行证据及计划。示例中 `git add` 应按真实改动选择文件。done 表示开发与验收完成，**不是已发布**；工具不会自动部署或向朋友发送通知。实际发布另行执行既定部署流程，在计划 `delivery` 记录真实发布状态、版本和说明。

## 计划结构与状态

模板：[templates/plan.md](templates/plan.md)。单个 Markdown 保留以下标题及两个 JSON fenced block：

| 部分 | 必须记录的内容 |
| --- | --- |
| `## 元信息` | `{id,status,specs,risk,checks}`；id 与 slug 对应；specs 为映射 key 列表 |
| `## 问题与目标` | 触发条件、实际行为、影响与目标 |
| `## 预期行为与范围` | 可观察结果、接口/权限边界、影响范围和不包含的内容 |
| `## 验收场景` | `- [ ] AC-01: ...`，每条稳定编号与可验证预期 |
| `## 任务` | `- [ ] T-01: ...`，每条稳定编号与工作内容；多代理明确文件和接口 |
| `## 审阅结论` | 完工时明确说明是否达成目标、证据、差异与剩余限制 |
| `## 验证记录` | `{runs:[],codeCommit:"",delivery:{status:"not_released",notes:""}}`；由 run 写入检查记录 |

新建计划保留 TODO 提示，不能直接视为可开工。`check/start/run` 拒绝必要需求文本的占位；审阅和空证据在这三个阶段允许，`finish` 才要求完备。手工复制模板时还需填写真实 id、规格 key、risk 和 checks，建议使用 `new` 自动生成元信息。

状态为 `draft`、`in_progress`、`done`、`cancelled`。计划取消时手工填写 cancelled 并在审阅结论说明原因；取消不意味着验收通过。done 与发布状态相互独立，未发布的完工计划保持 `delivery.status=not_released`。变更发布状态必须来自真实发布结果。

## CLI 与最低检查

工具入口是 `python3 scripts/sdd.py`，只用 Python 标准库；Go、npm 等仍是产品检查所需的外部环境。`new <slug> --title <标题> --spec <key> [--spec <key> ...] --risk <等级>` 创建计划。`check/start/run/finish <plan路径>` 默认使用同级 `river-code`，也可添加 `--code-dir /绝对路径/river-code`。`run` 可用重复 `--check <名称>` 选择检查。

| 固定 profile | 执行范围 |
| --- | --- |
| `links` | 检查双仓库本地链接、规格映射及相应源码路径 |
| `sdd` | SDD 工具自身单元测试 |
| `backend` | 后端 `go test` 与 `go vet` |
| `frontend` | 前端 `npm run build` |
| `media` | 产品的 `scripts/test-media.sh` |

| 风险等级 | 最低检查 |
| --- | --- |
| `docs` | links |
| `tooling` | links、sdd |
| `ui` | links、frontend |
| `rules`、`service`、`storage` | links、backend |
| `media` | links、frontend、media |

risk 描述本次变化实际风险，不为少运行命令把行为变化标成 docs。单次跨 UI、规则和媒体时在 checks 加入额外 profile，满足所有受影响能力；这些命令也不能替代实际人工或外部验收。小文案 docs 风险只要求 links，不强加前后端全量检查或重复实现的测试。

## 验证证据与完成门禁

每次 run 保存所选 profile 的命令参数、工作目录、退出码、UTC 时间，以及 `codeCommit`、`codeClean`、工具 `toolSha256`、对应规格的 `specSha256` 和 `planFingerprint`。验证记录顶层 `codeCommit` 指向被检查的代码提交；不要手工伪造 pass、hash 或命令结果。

finish 同时要求：AC/T 全部为 `[x]`、审阅结论明确、每个必需检查的**最新**记录通过；记录对应当前代码 HEAD，代码工作区 clean；工具 hash、计划关联规格 hash、计划需求 fingerprint 均与当前内容一致。后一次失败不能被更早的成功覆盖；缺检查、过期证据或尚未提交的代码都需修正并重新检查。

需求指纹用于使旧证据失效：改变问题、目标、预期行为、验收/任务文本及相关要求后，不能沿用旧结果。仅状态变化、checkbox 勾选和审阅补记不改变需求指纹，运行证据追加也不应使证据自我失效。修改工具或关联规格同样需要重跑。验收记录只保存脱敏后的条件和结果，不保存底牌、牌堆、cookie、加入密码、令牌、TURN 凭据或语音数据。

## 双仓库提交关系

1. 规格仓库先提交计划，获得 `spec-start`。
2. 代码提交用 `SDD-Plan` footer 链接 `spec-start` 的计划；代码仓库获得 `code-change`。
3. 更新长期规格并在 run 中固定 `code-change`，finish 后提交规格得到 `spec-done`。

纯文档变更没有产品代码改动时，保留当前代码 HEAD 供 links 证据固定，不制造空代码提交。

这样代码指向先前存在的计划，最终计划和基线指向已完成的代码，无需让两个仓库的最新 SHA 彼此递归。不要为把 footer 改成 `spec-done` 而反复 amend 代码再重做规格提交；已完工后出现新的变更时建立新的计划。运行证据绑定的是被检查的代码内容和规格内容，不是要求两仓库最新提交同时引用彼此。

## 后续计划：朋友边玩边反馈

现在可以由维护者**手工**把朋友意见整理进计划的问题与目标；没有产品反馈入口、自动入库、自动创建计划或自动执行反馈内容。反馈文本是不可信输入，不赋予其代理执行、发布或外部操作权限。

后续独立计划可以实现轻量反馈入口与维护列表，记录问题/建议、页面尺寸、版本、房间和手牌标识及公开阶段；不自动采集底牌、牌堆、语音、Cookie 或任何密钥。主动上传截图需要单独隐私设计，画面可能包含自己的底牌。最小范围为提交、查看、状态与版本关联，不增加复杂工单系统。

验收应包含两位朋友在真实牌桌提交意见、维护者选取一条后建立计划、实际改进并验收、试玩者更新后看到变化且身份/房间保留。SDD 工具现有的计划能力只覆盖维护者手工整理后的流程。

## 后续计划：开发与稳定试玩环境

开发环境使用已有 Vite HMR 调 UI，后端单独运行；开发数据库与稳定试玩数据库分开。稳定试玩使用 HTTPS 与固定域名，不受未验证的源码保存影响。统一开发命令、版本提醒和受控后端重启仍需要独立计划、实现及验收。

计划中的更新提示应允许玩家在适当时机刷新，不能在操作中反复强制刷新。会话和房间恢复复用已有能力，语音需要明确重新加入。每个试玩版本应能追溯代码提交、计划、部署结果和回滚条件。

## 后续计划：安全重载与发布边界

| 变化 | 待设计/验收的生效边界 |
| --- | --- |
| 样式和前端交互 | 开发环境已有 HMR；稳定试玩发布后提示刷新仍待实现 |
| HTTP 或房间服务 | 验证协议兼容与持久化后受控重启，客户端重连并检查恢复 |
| 下注和结算规则 | 当前手完成后暂停下一手，发布新规则再恢复；不得中途切换 |
| 数据库结构 | 兼容迁移、备份、回滚条件和实际恢复验证 |
| 系统配置 | 明确具体配置需重启或下一手生效；尚无通用配置热加载 |

当前服务启动脚本只构建并启动；Go 文件保存不自动安全重载。已有快照恢复不等于完整热更新协议。后续计划应验证更新期间不会重复行动/结算，失败时能回退兼容版本并恢复房间。自动发布、手牌边界发布和自动通知均未由 SDD CLI 实现。
