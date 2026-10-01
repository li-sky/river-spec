# 建立 RIVER 轻量 SDD 工作流

## 元信息

```json
{
  "id": "sdd-workflow",
  "status": "done",
  "specs": [
    "workflow"
  ],
  "risk": "tooling",
  "checks": [
    "links",
    "sdd"
  ]
}
```

## 问题与目标

现有模块和页面文档主要记录现有实现，缺少可执行的变更流程。用户要求先完成 SDD 工作流，并参考 Warp 的可编辑计划、任务跟踪、差异审阅和实际验证方式。

建立一个开发者与代理都能使用的轻量流程，把长期规格、每次改进的计划、实现任务、验证结果和两个仓库的提交关联起来。

## 预期行为与范围

每次改进只建立一份 Markdown 计划；长期规格继续按后端模块和前端页面维护。计划描述问题、目标、范围、验收场景、任务、审阅和验证记录。

提供 new、check、start、run、finish 命令，支持风险对应的固定检查。完成时核对人工验收项、检查结果、当前代码提交、工作区和需求指纹，避免复用失效证据。代码仓库提供调用入口，默认使用同级规格仓库。

两个仓库保留独立提交历史：代码提交引用先前的规格计划提交，最终计划记录代码提交与验证证据。开发完成不代表已部署，发布状态单独保存。

本次只完善开发工作流、脚本和文档，不修改扑克规则或游戏交互；朋友反馈入口、统一热重载与自动发布仍是后续范围。

## 验收场景

- [x] AC-01: 开发者能够通过代码仓库入口生成一个独立计划，补充预期后开启，并查看明确的检查结果；重复名称和非法路径不能覆盖文件。
- [x] AC-02: 缺失必需检查、检查失败、未完成验收项或缺少明确审阅时，计划不能标为开发完成。
- [x] AC-03: 修改需求、受影响规格、检查工具或代码提交后，旧验证证据不能用于完成；未提交代码不能完成。
- [x] AC-04: 有效计划、已确认的验收项及当前成功证据能够完成，保留代码提交；发布状态仍为未发布，不自动推送或部署。
- [x] AC-05: 工作流、模板、双仓规则及源码映射相互一致，全部对应文档和源码链接可以在本地核对，实际代码提交通过固定链接关联计划。

## 任务

- [x] T-01: 文档代理负责 workflow.md 与 templates/plan.md，记录单计划流程、阶段门槛、风险检查和双仓提交关联；集成人核对命令协议。
- [x] T-02: 工具代理负责 scripts/sdd.py，集成人负责代码仓库 scripts/sdd.sh；共同核对参数、路径和状态接口。
- [x] T-03: 工具代理负责 scripts/test_sdd.py，审阅代理只读验证失败门槛、过期证据和合法闭环，集成人执行最终测试。
- [x] T-04: 集成人从真实仓库执行本计划检查，审阅实际差异并记录可复核结果。
- [x] T-05: 集成人同步 README、AGENTS.md、规格索引和映射，并提交双仓改动。

## 审阅结论

审阅通过，本次目标已达成。工具代理实现 CLI 和隔离测试，文档代理维护流程与模板，只读审阅代理核对完成门槛；集成人核对双仓差异并在真实仓库执行检查。

- AC-01：代码入口从 /tmp 成功生成临时计划，真实计划通过 check/start；重复名称、非法 slug 和未填写需求被拒绝，临时计划已清理。
- AC-02/03：2026-10-01 最终运行 19 项标准库测试全部通过。实际未完成计划也被 finish 拒绝。隔离场景验证缺失或失败检查、最新失败、未勾选验收、待审阅、未提交代码、不同 HEAD，以及需求、规格、工具、测试和映射变化使证据失效；还验证零测试、残缺命令证据、取消状态、路径越界和并发人工编辑保护。
- AC-04：隔离场景验证合法 start/run/finish 完整闭环、代码提交保留、发布状态保持 not_released；本计划在补记真实验收后执行同一 finish 门槛。脚本没有推送或部署操作。
- AC-05：真实 links 检查通过；两仓映射一致，全部对应规格和源码路径存在。代码提交 fac8dc51e28a1611524b32febeb5c492dd28a25e 的 SDD-Plan footer 固定引用规格提交 0e81a558895e6a3d94e67974716fc2833494598d 中的本计划。最终代码 worktree 清洁，run 记录具体命令、当前代码提交及内容指纹。

本次差异限于工作流、调用入口和文档；没有修改产品行为，因此不把既有产品构建、PostgreSQL 或多人浏览器的历史结果作为本次重测。完成门槛由本地 CLI 和开发约定落实，尚未配置 GitHub 服务端强制合并检查。朋友反馈入口、统一热重载和试玩发布仍需后续计划。

## 验证记录

```json
{
  "runs": [
    {
      "check": "links",
      "commands": [],
      "exitCode": 0,
      "at": "2026-10-01T09:18:54.345218Z",
      "codeCommit": "fac8dc51e28a1611524b32febeb5c492dd28a25e",
      "codeClean": true,
      "toolSha256": "92eaeb143234befefb3f05aa58cfa120cbbdf2ec973c8f18ff1d8e9c94dae768",
      "supportSha256": {
        "scripts/test_sdd.py": "6db367b3d51bc2c7a8142d458cd1485237e005eb635af00984aeaeff837e788e"
      },
      "specMapSha256": "c469a7dd671df04b4fdc0613126136510526adb7276b36fd18bee0c11d17d6bc",
      "specSha256": {
        "workflow": "b62a399f729f49019ff5ed06ab31b59b0014f71c418b5ad98440c70424751e36"
      },
      "planFingerprint": "c1d6dee33a99a1fdd7566d1ab325675373a1c2c709e0f4ed9156768fc38d55ef"
    },
    {
      "check": "sdd",
      "commands": [
        {
          "argv": [
            "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            "scripts",
            "-p",
            "test_sdd.py"
          ],
          "cwd": "/workspace/river-spec",
          "exitCode": 0
        }
      ],
      "exitCode": 0,
      "at": "2026-10-01T09:18:54.384034Z",
      "codeCommit": "fac8dc51e28a1611524b32febeb5c492dd28a25e",
      "codeClean": true,
      "toolSha256": "92eaeb143234befefb3f05aa58cfa120cbbdf2ec973c8f18ff1d8e9c94dae768",
      "supportSha256": {
        "scripts/test_sdd.py": "6db367b3d51bc2c7a8142d458cd1485237e005eb635af00984aeaeff837e788e"
      },
      "specMapSha256": "c469a7dd671df04b4fdc0613126136510526adb7276b36fd18bee0c11d17d6bc",
      "specSha256": {
        "workflow": "b62a399f729f49019ff5ed06ab31b59b0014f71c418b5ad98440c70424751e36"
      },
      "planFingerprint": "c1d6dee33a99a1fdd7566d1ab325675373a1c2c709e0f4ed9156768fc38d55ef"
    }
  ],
  "codeCommit": "fac8dc51e28a1611524b32febeb5c492dd28a25e",
  "delivery": {
    "status": "not_released",
    "notes": "本次建立开发工作流，不部署游戏版本。"
  }
}
```
