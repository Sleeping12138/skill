---
name: project-onboarding
description: >-
  Use when the user asks to quickly understand and document an existing Git repository,
  then publish eight concise onboarding documents to Lark/Feishu Wiki.
disable-model-invocation: true
argument-hint: >-
  [无参数] / [publish] → 生成并发布；[publish <wiki-url>] → 发布到指定节点；
  [local] → 只生成详细本地材料；[update] → 重生成并覆盖飞书节点。
---

# project-onboarding —— 新项目快速上手

目标是让新人通过飞书文档快速明白“这是什么项目、代码在哪、大致怎么运行、从哪里开始”。详细事实保留在 Git 中，飞书发布稿是面向阅读者的精炼二次改写，不直接搬运长文。

## 核心规则

1. 无参数、`publish` 和 `update` 默认发布；只有 `local` 不写飞书。
2. Git `docs/` 是事实源；飞书只做 Git → Lark 单向覆盖。
3. 根据仓库实际类型和能力讲解，不套固定业务模板，不虚构 API、数据库、Worker、UI 或部署结构。
4. 文档先说人话，再给项目中的小例子，最后补充必要的文件路径。
5. 发布前只运行一次轻量确定性验证；不做字数、图数、七问、证据密度、远端全文回读或 receipt 硬门禁。
6. 只读目标仓库源码，只写 `docs/codebase/` 和 `docs/onboarding/`；秘密值不得进入文档、命令输出或飞书。

## 固定产物

保留两个上游 Skill 生成的 8 份详细事实源：

- `docs/codebase/STACK.md`
- `docs/codebase/STRUCTURE.md`
- `docs/codebase/ARCHITECTURE.md`
- `docs/codebase/CONVENTIONS.md`
- `docs/codebase/INTEGRATIONS.md`
- `docs/codebase/TESTING.md`
- `docs/codebase/CONCERNS.md`
- `docs/onboarding/ARCHITECTURE_DEEP_DIVE.md`

非 `local` 模式再生成 8 份精炼飞书源文档和对应净化投影，映射见 [references/lark-publishing.md](references/lark-publishing.md)。不再生成 `PROJECT_GUIDE.md`、`.onboarding-profile.json` 或 `.newcomer-review.json`。

## 执行流程

### Phase 0：前置检查

1. 确认当前目录在 Git 工作树内，读取 `AGENTS.md`、`CLAUDE.md`、`CONTRIBUTING*` 等仓库约束。
2. 确认 `acquire-codebase-knowledge` 和 `doc-and-modernize` 可用。
3. 非 `local` 模式按 `lark-shared` 仅做一次认证/权限检查；结果在发布阶段复用。权限不足不影响本地文档生成。

### Phase 1：生成 7 份代码库事实

调用 `acquire-codebase-knowledge` 完整生成 `docs/codebase/` 下的 7 份文档。不自行复制它的扫描逻辑。未知事实明确写 `TODO` / `UNKNOWN` / `ASK MAINTAINER`。

### Phase 2：生成架构深读

调用 `doc-and-modernize` 的 Documentation Mode，要求最终完整文件固定为 `docs/onboarding/ARCHITECTURE_DEEP_DIVE.md`。只有用户明确要求改造、迁移或重构时才进入 Modernization Mode。

### Phase 3：二次改写为 8 份飞书快速阅读稿

非 `local` 模式执行。逐份阅读对应的详细事实源，重写到 `docs/onboarding/lark/`：

- 每篇以“这部分是做什么的”开头，提炼 4–6 个最值得记住的结论。
- 用通俗语言补足必要背景，说清项目的作用、主要边界、各部分如何配合和新人的下一步；专业术语随用随解释。
- 每篇至少选一个真实、短小的例子，如“修改一个接口时先看哪些文件”，并说明正常结果、常见失败和首个排查入口。
- 只保留少量关键路径，不堆砌源码证据、完整目录或内部实现细节。
- 流程图、时序图能明显降低理解成本时保留；不设总图数限额。规则见 [references/architecture-guide.md](references/architecture-guide.md)。
- 00–06 每篇约 600–900 个中文字，07 约 900–1400 字。这些只是写作参考，不是验收门禁；信息完整性、密度和可读性优先。

不要写 `<!-- diagram-context: after -->` 等机器标记。为兼容旧稿，净化脚本仍会确定性删除已知标记：

```bash
python3 "$SKILL_ROOT/scripts/prepare_lark_publish.py" --repo-root .
```

### Phase 3.5：一次轻量验证

发布前只运行：

```bash
python3 "$SKILL_ROOT/scripts/validate_onboarding.py" \
  --repo-root . \
  --mode lark-ready
```

它只检查：

- 8 份详细事实源非空；
- 8 份飞书源文档和 8 份净化投影非空；
- Mermaid fence 闭合，根指令只为 `flowchart`、`graph` 或 `sequenceDiagram`；
- 禁止 `stateDiagram` / `stateDiagram-v2`，避免飞书 `degrade_code=2107`；
- 无秘密值，净化投影与确定性净化结果一致且无机器标记。

`local` 模式只需把命令的 mode 改为 `local`。不运行 `mmdc`、浏览器渲染、字数/图数验收或模型自评。

### Phase 4：快速发布飞书

非 `local` 且认证有效时，按 [references/lark-publishing.md](references/lark-publishing.md) 发布：

1. 只上传 `docs/onboarding/.lark-publish/` 中的 8 份净化投影。
2. 复用已知节点 token；必要时最多完整查询一次 Wiki 节点。
3. 已有节点整篇覆盖，缺失节点创建；最多四路并发。
4. Mermaid 随文档写入一次导入 Whiteboard。只处理写入响应中的明确错误，不回读全文、不轮询 revision、不导出画板。
5. 网络或限流错误最多重试一次；其他失败直接记录标题和原因。
6. receipt 只是尽力而为的发布记录，不执行发布后验证器，不因 receipt 缺失或不完整重新上传。

## 完成报告

只报告：

- 8 份详细源和 8 份飞书精炼源的路径；
- 轻量验证是否通过；
- 飞书成功链接与失败标题；
- 总耗时，并明确“为提速未执行远端全文回读和严格编辑指标验收”。

## References

| 参考 | 用途 |
|---|---|
| [references/output-contract.md](references/output-contract.md) | 8 份详细源到 8 份精炼稿的改写契约 |
| [references/architecture-guide.md](references/architecture-guide.md) | 可读流程图与飞书 Mermaid 安全子集 |
| [references/lark-publishing.md](references/lark-publishing.md) | 固定 00–07 映射和快速发布流程 |
