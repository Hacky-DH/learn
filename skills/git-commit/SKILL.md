---
name: git-commit
description: |
  Use when user asks to "commit", "提交", "git commit", "帮我提交",
  "commit当前变更", "创建commit", or otherwise wants to create a git commit
  in this project. Enforces the project's conventional-commit regex and the
  30-word limit on the commit subject.
allowed-tools: Bash, Read
---

# Git Commit Helper

创建符合本项目 commit 规则的 git commit。

## Commit Message 规则

**正则表达式:**
```
^(feat|fix|bugfix|docs|test|refactor|chore|style|revert|perf|model|build)(\(\w+\))?: (?![0-9\s\W]+$)(?!.*[\u4e00-\u9fa5])(?:(?![\u4e00-\u9fa5]\w*)\w+\s+){3,}[\n\d\w\s:/.]*
```

**必须遵守的约束:**

1. **type (必填)**: 必须是以下之一
   - `feat` — 新功能
   - `fix` / `bugfix` — bug 修复
   - `docs` — 文档
   - `test` — 测试
   - `refactor` — 重构
   - `chore` — 杂项
   - `style` — 代码风格
   - `revert` — 回滚
   - `perf` — 性能
   - `model` — 模型相关
   - `build` — 构建

2. **scope (可选)**: `(\w+)` 形式，如 `fix(pipeline):`

3. **冒号后必须一个空格**: `type(scope): message`

4. **正文约束**:
   - 不能全是数字/空格/符号
   - **不能包含任何中文字符**
   - 冒号后至少 **4 个英文单词**（正则 `{3,}` + 后续 token，实操上 subject 至少 4 词最稳）
   - 只能包含 `\d\w\s:/.` 字符（字母数字、空格、冒号、斜杠、点）

5. **单词总数 ≤ 30**（用户要求，不含 type/scope 前缀） 除非用户明确要求字数

## 工作流程

1. 运行 `git status` 查看当前状态
2. 运行 `git diff --cached`（若有已 staged）和 `git diff`（未 staged）查看变更
3. 运行 `git log --oneline -5` 参考仓库 commit 风格
4. 分析变更内容 → 选择合适的 type 和 scope
5. 起草英文 commit message，逐条自检:
   - [ ] type 在白名单中
   - [ ] `type(scope): ` 格式正确（冒号+单空格）
   - [ ] 无中文字符
   - [ ] 字符集在 `[\w\s:/.]` 内
   - [ ] subject 至少 4 个词
   - [ ] 总词数 ≤ 20
6. 若有未 staged 的相关文件，明确告知用户是否需要 `git add`（**不要**默认 `git add -A`，避免误提交秘钥/大文件/日志）
7. 用 HEREDOC 传递 message 创建 commit
8. `git log --oneline -1` 确认成功

## 示例

好的:
```
fix(pipeline): add assertions and stream sync in nest pipeline embedding backward
feat(torch): support micro batch forward backward pipeline for embedding
refactor(ps): migrate npu910 kernels to match npu950 structure
```

不好的:
- `fix: 修复 pipeline bug`  ❌ 含中文
- `fix: bug`  ❌ 词数不足
- `update code`  ❌ 缺少 type
- `feat: add new pipeline feature for micro batch forward backward with proper synchronization and error handling and validation`  ❌ 超过 20 词

## 安全约束

- **不要** `git add -A` / `git add .` — 逐个明确添加相关文件
- **不要** `--amend` / `--no-verify` / `-i` — 除非用户明确要求
- **不要** commit 疑似含秘钥的文件 (`.env`, `credentials.*`)
- **不要** 主动 push — 除非用户明确要求
