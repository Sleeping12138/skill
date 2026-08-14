# 8 份精炼文档的飞书快速发布

## 固定映射

| 飞书标题 | 详细事实源 | 精炼改写源 | 实际上传投影 |
|---|---|---|---|
| 00 技术栈 | `docs/codebase/STACK.md` | `docs/onboarding/lark/00-stack.md` | `docs/onboarding/.lark-publish/00-stack.md` |
| 01 代码结构 | `docs/codebase/STRUCTURE.md` | `docs/onboarding/lark/01-structure.md` | `docs/onboarding/.lark-publish/01-structure.md` |
| 02 系统架构 | `docs/codebase/ARCHITECTURE.md` | `docs/onboarding/lark/02-architecture.md` | `docs/onboarding/.lark-publish/02-architecture.md` |
| 03 开发规范 | `docs/codebase/CONVENTIONS.md` | `docs/onboarding/lark/03-conventions.md` | `docs/onboarding/.lark-publish/03-conventions.md` |
| 04 外部集成 | `docs/codebase/INTEGRATIONS.md` | `docs/onboarding/lark/04-integrations.md` | `docs/onboarding/.lark-publish/04-integrations.md` |
| 05 测试指南 | `docs/codebase/TESTING.md` | `docs/onboarding/lark/05-testing.md` | `docs/onboarding/.lark-publish/05-testing.md` |
| 06 风险与关注 | `docs/codebase/CONCERNS.md` | `docs/onboarding/lark/06-concerns.md` | `docs/onboarding/.lark-publish/06-concerns.md` |
| 07 架构深读 | `docs/onboarding/ARCHITECTURE_DEEP_DIVE.md` | `docs/onboarding/lark/07-architecture-deep-dive.md` | `docs/onboarding/.lark-publish/07-architecture-deep-dive.md` |

8 份飞书稿都是二次改写，包括 07；不要把详细深读原样复制进飞书。00–06 以约 600–900 字的中等篇幅讲清主题，07 以约 900–1400 字串起核心架构；只作写作参考，不做发布门禁。具体取舍见 [output-contract.md](output-contract.md)。

## 准备与唯一发布前验证

```bash
python3 "$SKILL_ROOT/scripts/prepare_lark_publish.py" --repo-root .
python3 "$SKILL_ROOT/scripts/validate_onboarding.py" --repo-root . --mode lark-ready
```

第一条命令生成净化投影，仅用于保证旧版机器标记不会出现在飞书正文中。新稿本身不应生成这些标记。

第二条命令是唯一发布前门禁。不运行内容长度、单篇/总图数、新人七问、章节槽位、证据密度或模型自评。

## 快速幂等发布

1. 复用 Phase 0 的认证结果，不重复探测身份和 scope。
2. 指定 Wiki URL 时以它为根。否则复用唯一明确的 Onboarding 目标；存在多个候选时才请用户选择。
3. 优先复用上次记录的节点 token。token 缺失或明确失效时，完整分页查询 Wiki 节点一次，一次解析全部 8 个标题，禁止逐篇重复搜索。
4. 只从 `.lark-publish/` 整篇写入。不读取旧正文、不做局部 patch；已有节点覆盖，缺失节点创建。
5. 8 个节点以最多四路并发分两批写入。同批调用同时发起后再统一收集结果。
6. Mermaid 随文档写入导入 Whiteboard。不再单独执行 Whiteboard update/export，不为校验而重复上传。
7. 网络瞬时错误或限流可用同一幂等标识重试一次。权限、内容、`degrade_code` 等明确失败不自动改写重发。
8. 写入后不 fetch 全文、不轮询 revision、不重算远端 hash、不运行发布后验证器。

## 轻量发布记录

如果发布工具已返回结果，可尽力而为地写入 `docs/onboarding/.lark-publish-receipt.json`，仅记录：

- `schema_version: 4`
- `verification_level: "write-response"`
- 发布时间和 Wiki 空间/根节点
- 每篇的标题、document token、URL、revision、写入状态、warnings 和 degrade codes
- `remote_readback_performed: false`

receipt 是日志，不是完成条件。不为它计算段落数、图数、Whiteboard 数量或本地/远端哈希；缺少某个非关键字段不得触发读回或重新发布。

## 结果处理

写入响应成功即记录对应链接。失败时只报告失败标题和简短原因，保留其他成功节点。最终说明：“为提速未执行远端全文回读和严格编辑指标验收。”
