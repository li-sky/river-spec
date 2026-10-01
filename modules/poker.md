# RIVER 德州扑克规则模块规格

基线日期：2026-10-01。状态：已实现模块的源码核实基线。本文路径均相对于 RIVER 项目根目录。已确认需求来自用户约定和 [docs/CONTRACT.md](https://github.com/li-sky/river-code/blob/main/docs/CONTRACT.md)；具体算法、数值边界和规则选择另标为当前实现，不能据此推定用户承诺了这些细节。

## 目的与范围

由服务端权威执行 No-Limit Texas Hold’em 现金桌的一手牌，包括发牌、合法行动、轮次推进、牌型判定和虚拟筹码结算。这里的现金桌描述加入和买入方式；筹码没有真实货币价值。本模块不管理账号、房间权限、网络连接、数据库或计时器。

已确认的设计要求是适当解耦判定系统，便于以后增加规则设置，避免过度设计。当前 `Evaluate` 可独立调用，`Hand` 管理下注和结算，`server` 管理房间与通信；尚未实现可选择的规则插件体系。

## 已确认需求与当前规则选择

| 范围 | 基线 |
| --- | --- |
| 玩法 | 已确认：标准无限注德州扑克、现金桌、多人真实对战，服务端决定私牌和行动结果。 |
| 筹码 | 项目基线：使用整数虚拟筹码；一手内发牌和结算须保持筹码守恒。买入及房主在两手之间修改筹码由上层管理。 |
| 行动 | 已确认玩法对应弃牌、过牌、跟注、加注、all-in。当前加注参数表示本轮下注总额，而不是新增筹码数。 |
| 人数 | 当前房间和引擎支持 2～9 名参与者；这是实现范围，不是用户要求无限人数，也不限制下注次数。 |
| 轮次 | 当前顺序为 preflop → flop → turn → river → complete；仅剩一名未弃牌玩家可提前结束。 |
| 单挑 | 当前庄家兼小盲，翻牌前先行动；翻牌后非庄家先行动。多人桌盲注和行动沿座位顺时针推进。 |
| 加注 | 当前完整加注至少等于本轮上一次完整下注或加注增量，初始为大盲。不足该增量仅在用尽筹码时允许。 |
| 重新开放 | 当前规则：短 all-in 不立即重新开放已行动玩家的加注权；累计增量达到该玩家面对的完整增量时重新开放。过牌计入已行动。 |
| 短开注 | 当前规则选择：翻牌后大盲为 10，首次短 all-in 为 5 时，非 all-in 的最小加注总额为 15。先前过牌者仅面对 5 时不能加注。该选择有回归测试，未来变体需显式定义。 |
| 无可跟注对手 | 当前仅剩一名有筹码玩家时，只保留其面对对手未跟注下注的决定；不允许向全部 all-in 的对手追加无意义加注。其余轮次自动发至结算。 |
| 结算 | 当前退回唯一最高、未被匹配的投入后按投入层级构造边池；弃牌玩家的投入参与底池，但不能获奖。各池独立比较牌型，平分时零头按庄家左侧开始的顺时针获胜座位分配。 |
| 牌型 | 当前从 5～7 张不同牌中枚举最佳五张，比较牌型和踢脚；A2345 计为五高顺子。无抽水。 |

## 当前接口与责任边界

| Go 接口 | 含义 |
| --- | --- |
| `NewHand(number int, dealerSeat int, smallBlind, bigBlind int64, seats []Seat) (*Hand, error)` | 验证参与者、密码学随机洗牌、发两张底牌、支付盲注并确定行动者。`Seat` 包含 `ID`、`Seat`、`Stack`。庄家座位未参与时取其后顺时针参与者。 |
| `(*Hand).Action(playerID, action string, amount int64) error` | 验证当前行动者和动作合法性，再修改状态并推进轮次。动作字符串为 `fold/check/call/raise/allin`。 |
| `(*Hand).AutoAction() error` | 当前行动者能过牌则过牌，否则弃牌；上层负责决定何时调用。 |
| `(*Hand).Finished() bool` | 判断 `Phase == "complete"`。 |
| `(*Hand).View(viewerID string) HandView` | 生成按观看者过滤的客户端投影，不输出牌堆或将来的牌。 |
| `Evaluate(cards []string) (HandRank, error)` | 返回最佳五张牌的可比较分数及中文牌型描述；分数越大越好。 |

引擎只识别参与者 ID，不识别房主、加入者、注册用户或访客。即使调用者是房主，也不能越过行动顺序或查看对手未公开底牌。身份权限、行动令牌和房间准入均由 `server`／`identity` 执行。

`Hand` 的可 JSON 序列化字段包含完整底牌、`Deck`、`DrawIndex` 和加注权判断信息，只可作为私有持久化状态。公开接口必须使用 `HandView`。公开手牌包含 `number/phase/board/pot/dealerSeat/turnSeat/currentBet/minRaise/players/winners`；各玩家投影包含 `id/seat/bet/totalBet/folded/allIn/cards/acted/canRaise`。`deadline` 和 `turnToken` 由上层添加。

`canRaise` 表示有加注权且存在可跟注对手，包括合法的短 all-in；普通加注仍须满足最小增量。它不是绕过 `Action` 验证的授权凭据。

## 状态 安全与错误边界

- `Stack` 是扣除已投入筹码后的余额；`Bet` 是本轮投入，`TotalBet` 是整手投入。轮次改变清零 `Bet`，保留 `TotalBet`。

- 进行中：总筹码 = 所有 `Stack` + 所有 `TotalBet`。完成后：`Stack` 已包含退款和获奖，总筹码仅求和 `Stack`；视图中的 `pot/totalBet` 作为本手记录保留，不得再次加回。

- 当前发牌使用 `crypto/rand` 的 Fisher–Yates 洗牌；翻牌、转牌和河牌前分别烧一张牌。

- 观看者始终可看自己的底牌。摊牌结束后公开未弃牌玩家底牌；弃牌获胜不会公开其他人的底牌，弃牌者底牌不向其他观看者公开。

- 实际 `Phase` 没有单独停留的 `showdown` 状态；摊牌直接结算成 `complete`，通过 `Reveal` 控制公开底牌。契约枚举中的 `showdown` 当前未输出。

- `NewHand` 当前拒绝少于 2 或多于 9 人、重复 ID／座位、空 ID、非 0～8 座位、非法盲注及非正筹码。引擎单人初始筹码上限为 `MaxChips = 10^12`；这是整数计算护栏，上层限制更严格。

- 引擎允许大盲至少等于小盲，上层房间设置要求大盲至少为小盲两倍；两者不是同一个验证层。

- `Action` 在写入状态前拒绝结束后行动、非当前行动者、有下注时过牌、非法加注总额、未开放加注、非 all-in 的不足最小加注及未知动作。错误消息当前为英文，由服务层原样传递的情况存在。

- `Evaluate` 拒绝非 5～7 张输入、重复牌和非法牌字符串；合法格式如 `As`、`Th`、`2c`。

- `Hand` 不自带锁；上层必须串行访问同一手牌。JSON 恢复本身不是对任意输入的完整结构验证器，牌堆和阶段字段假定来自受信任的服务端快照。

## 关键验收场景与测试证据

| 场景 | 对应测试 |
| --- | --- |
| 单挑小盲先行动，大盲保留过牌选择，翻牌后顺序正确；未摊牌私牌隔离 | `TestHeadsUpOrderAndPrivacy` |
| 弃牌直接获胜、未匹配筹码退款、赢家底牌不被强制公开 | `TestFoldAndUnmatchedReturn` |
| 短 all-in 不开放、累计短加注达到完整增量才开放 | `TestShortAllInDoesNotReopenAndCumulativeDoes` |
| 非法最小加注不得修改状态，正常完整加注更新增量 | `TestMinimumRaiseAndAllInValidation` |
| 多层边池独立获奖并退回未跟注投入 | `TestSidePotsAndUncalledReturn` |
| 平局零头按庄家左侧顺时针分配 | `TestSplitOddChipClockwise` |
| 短盲注及无人可继续下注时自动发完；不能向仅剩 all-in 对手加注 | `TestShortBlindsAutomaticRunout`、`TestCannotRaiseAgainstOnlyAllInOpponent` |
| JSON 恢复后行动与最终状态一致、牌堆不重复 | `TestJSONResumeAndDeck` |
| 1,000 局固定种子随机合法行动逐步及结算后保持筹码守恒、无卡住轮次 | `TestRandomLegalHandsConserveChips` |
| 翻牌后短开注、最小完整加注以及过牌者重新开放规则 | `TestPostflopShortOpeningAndCheckedReopening` |
| 牌型、踢脚、A2345、非法牌拒绝及全部 2,598,960 种五张牌的类别数量 | `TestEvaluateCategoriesAndKickers`、`TestEvaluatorRejectsInvalidCards`、`TestFiveCardCategoryCounts` |

上表列出当前源码中的测试覆盖，不代替实际部署验收；整体执行记录见 [docs/VERIFICATION.md](https://github.com/li-sky/river-code/blob/main/docs/VERIFICATION.md)。可在 `backend` 中运行 `go test ./internal/poker`、`go test -race ./internal/poker` 和 `go vet ./internal/poker`。

## 源文件与测试相对路径

- [backend/internal/poker/doc.go](https://github.com/li-sky/river-code/blob/main/backend/internal/poker/doc.go)：模块约束和当前规则选择。

- [backend/internal/poker/engine.go](https://github.com/li-sky/river-code/blob/main/backend/internal/poker/engine.go)：完整手牌状态、行动、轮次、结算及公开投影。

- [backend/internal/poker/evaluator.go](https://github.com/li-sky/river-code/blob/main/backend/internal/poker/evaluator.go)：独立牌型判定。

- [backend/internal/poker/engine_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/poker/engine_test.go)、[backend/internal/poker/evaluator_test.go](https://github.com/li-sky/river-code/blob/main/backend/internal/poker/evaluator_test.go)：引擎与判定测试。

- [backend/internal/server/commands.go](https://github.com/li-sky/river-code/blob/main/backend/internal/server/commands.go)：引擎调用、计时触发、房间筹码同步。

- [docs/CONTRACT.md](https://github.com/li-sky/river-code/blob/main/docs/CONTRACT.md)、[docs/VERIFICATION.md](https://github.com/li-sky/river-code/blob/main/docs/VERIFICATION.md)：接口基线及既有验证记录。

## 已知限制与待实现

仅支持标准 NLHE；短牌、可改变牌型顺序的变体、锦标赛、抽水、真实资金账户和可选规则集未实现。边池仅在结算时内部拆分，公开视图没有逐个边池明细。没有摊牌阶段手动选择亮牌或隐藏牌的流程，也没有独立可暂停的摊牌阶段。持久化边界支持恢复最新手牌状态，不提供完整可回放的逐手历史或审计日志。朋友反馈功能和配置热重载未实现，且不属于本引擎职责。

## 文档与代码入口

[项目文档](https://github.com/li-sky/river-spec) · [代码仓库](https://github.com/li-sky/river-code)。当前源码基线为提交 `4975694`；后续实现变化需同步此规格和验收证据。
