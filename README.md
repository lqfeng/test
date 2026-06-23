# Starred Repos Export — README

This repository includes utilities to export a user's GitHub starred repositories into a classified JSON, infer simple topics, and produce per-topic lists.

Files added to this repository
- export_starred.py — (root) Python script that fetches a user's starred repos and exports a JSON with inferred topics.
- scripts/export_starred.py — (optional) previously created script under scripts/ (if present, you can use either).
- scripts/create_star_lists.js — Node script that reads the exported JSON and writes per-topic JSON files into `starred_by_topic/`.
- starred_repos_classified.json — example/sample export (small set for review).
- starred_repos_export_pages_7-13.json — partial raw export collected during an assistant session (pages 7..13).

JSON schema (output from export_starred.py)
- generated_by: string
- generated_at: ISO8601 timestamp (UTC)
- note: string
- repos: array of repository objects
  - name: string
  - html_url: string
  - description: string or null
  - language: string or null
  - stargazers_count: integer
  - inferred_topics: array of strings (heuristic topics inferred from language/name/description)

How to run

1) (Recommended) Use a GitHub token to increase rate limits.

Linux / macOS example:

```bash
export GITHUB_TOKEN=ghp_xxx...
python3 export_starred.py --username lqfeng --output starred_repos_full_export.json
```

You can also run the script under `scripts/` if you prefer that copy:

```bash
GITHUB_TOKEN=... python3 scripts/export_starred.py --username lqfeng --output starred_repos_full_export.json
```

2) Generate per-topic lists (Node.js required)

```bash
node scripts/create_star_lists.js
# output directory: starred_by_topic/
```

Notes and next steps
- star pages in GitHub are paginated. The assistant previously collected pages 7..13 and saved them to `starred_repos_export_pages_7-13.json` as a partial export. Use the Python script to fetch the complete list.
- The topic inference is heuristic and intentionally simple. Modify `infer_topics()` in export_starred.py to customize the mapping rules or to use a more advanced NLP approach.
- If you want the assistant to embed verbatim raw API responses (full arrays for each page) into the repo file, request "embed raw responses" and it will add them to `starred_repos_export_pages_7-13.json`.

Contact / Attribution
- Generated and added by a GitHub Copilot assistant during an interactive session.
