# Starred 仓库导出工具 — 使用说明（中文）

本仓库包含用���导出 GitHub 用户 starred 仓库的一套工具，能将 starred 列表导出为带自动推断主题的 JSON，并按主题生成单独的列表，便于备份与分析。

仓库内主要文件

- `export_starred.py` —— 根目录下的 Python 脚本：从 GitHub 抓取某用户的 starred 并导出为 JSON（包含推断主题）。
- `scripts/export_starred.py` —— 可选的脚本副本（与根目录脚本功能一致）。
- `scripts/create_star_lists.js` —— Node.js 脚本：读取导出的 JSON，按推断主题拆分并输出到 `starred_by_topic/` 目录。
- `starred_repos_classified.json` —— 示例导出文件（小样本，便于查看字段格式）。
- `starred_repos_export_pages_7-13.json` —— 会话中已抓取的部分导出（仅 pages 7..13），供审计或临时查看使用。

输出 JSON 格式（schema）

导出文件为一个对象，主要字段：

- `generated_by`: 生成者（字符串）
- `generated_at`: 生成时间（UTC，ISO8601）
- `note`: 说明文字
- `repos`: 仓库数组，数组中每个元素包含：
  - `name`: 仓库名（string）
  - `html_url`: 仓库页面 URL（string）
  - `description`: 仓库描述（string 或 null）
  - `language`: 仓库主要语言（string 或 null）
  - `stargazers_count`: Star 数（integer）
  - `inferred_topics`: 自动推断出的主题数组（array of string）

举例（单个仓库条目）：

```json
{
  "name": "transformers",
  "html_url": "https://github.com/huggingface/transformers",
  "description": "State-of-the-art Natural Language Processing for Pytorch and TensorFlow 2.0",
  "language": "Python",
  "stargazers_count": 161830,
  "inferred_topics": ["Python", "Transformers", "NLP"]
}
```

使用步骤（示例）

1) 准备：建议使用 GitHub 个人访问令牌（Personal Access Token）以增加 API 配额并避免速率限制。
   - 在终端中导出环境变量（Linux/macOS）：

```bash
export GITHUB_TOKEN=ghp_xxx_your_token_here
```

2) 抓取并导出全部 starred：

```bash
python3 export_starred.py --username lqfeng --output starred_repos_full_export.json
```

可选参数：
- `--per-page`：每页抓取数量（最多 100）。
- `--max-pages`：仅抓取指定页数（用于测试）。
- `--token`：可直接通过参数传入 token（否则从环境变量 GITHUB_TOKEN 读取）。

3) 生成按主题拆分的文件（需要 Node.js）：

```bash
node scripts/create_star_lists.js
# 输出目录：starred_by_topic/
```

`starred_by_topic/` 目录将包含每个推断主题对应的 JSON 文件以及 `SUMMARY.json`（统计每个主题的仓库数量）。

主题推断说明

- 主题由脚本中的 heuristics（基于 `language`、`name`、`description` 的关键字匹配）推断，规则位于 `export_starred.py` 内的 `infer_topics()` 函数。
- 当前实现使用了简单的关键字映射，便于快速分类；如需更准确的分类可以替换为基于模型或更完整的关键词表的实现。

已提交的临时导出

- `starred_repos_export_pages_7-13.json`：这是会话期间已抓取到的部分分页（pages 7–13）导出，作为中间备份/审计数据。该文件并非完整导出。

安全与注意事项

- 若导出大量条目或频繁运行，请务必使用带权限的 GITHUB_TOKEN，避免触发未认证速率限制（每小时 60 次请求）。
- 导出文件可能会包含仓库的公开描述，若包含敏感数据（极少见），请在共享前自行审查。

后续选项（你可以让我代为完成）

- 嵌入原始 API 响应：把每个页面的 verbatim JSON 嵌入到 `starred_repos_export_pages_7-13.json`（便于审计）。回复 "嵌入原始响应"。
- 抓取全部并替换：继续抓取用户的全部 starred 页面并生成完整导出，替换仓库中的导出文件（建议提供或��置 GITHUB_TOKEN）。回复 "抓取全部并替换"。
- 自定义主题映射：如果你有想要的主题关键字表或映射规则，我可以修改 `infer_topics()` 并重新生成导出。回复并提供映射规则或示例。

联系与来源

- 本工具和文档由交互式助手协助生成并提交到本仓库（如需变更说明或格式，请直接在聊天中说明）。
