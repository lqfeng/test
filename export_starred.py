#!/usr/bin/env python3
"""
export_starred.py

Fetch a user's starred GitHub repositories and export them to a JSON file
with inferred topics (based on language + name + description).

Usage:
  - set GITHUB_TOKEN environment variable to increase rate limits and access private repos if permitted
  - python3 export_starred.py --username lqfeng --output starred_repos_classified.json

Output JSON format:
  {
    "generated_by": "<user>",
    "generated_at": "ISO8601 UTC",
    "note": "...",
    "repos": [
      {
        "name": "repo-name",
        "html_url": "https://github.com/owner/repo",
        "description": "...",
        "language": "Python",
        "stargazers_count": 1234,
        "inferred_topics": ["Python","NLP"]
      },
      ...
    ]
  }
"""

from __future__ import annotations
import os
import sys
import time
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests

GITHUB_API = "https://api.github.com"


def infer_topics(repo: Dict[str, Any]) -> List[str]:
    """Infer simple topics from language, name and description."""
    topics = set()
    language = (repo.get('language') or '').strip()
    if language:
        topics.add(language)

    text = ' '.join(filter(None, [repo.get('name',''), repo.get('description','') or ''])).lower()

    # keyword -> topic mapping (heuristic)
    keyword_map = {
        'nlp': 'NLP', 'natural language': 'NLP', 'token': 'NLP',
        'transformer': 'NLP', 'bert': 'NLP', 'gpt': 'NLP',
        'llm': 'LLM', 'chat': 'Chatbot', 'chatbot': 'Chatbot', 'agent': 'Agent',
        'prompt': 'Prompt Engineering', 'prompting': 'Prompt Engineering',
        'tokenizer': 'Tokenizer', 'tokeniser': 'Tokenizer', 'tokenization': 'Tokenizer',
        'dataset': 'Dataset', 'corpus': 'Dataset',
        'vision': 'Computer Vision', 'image': 'Computer Vision', 'segmentation':'Computer Vision',
        'speech': 'Speech', 'asr': 'Speech', 'tts': 'Speech',
        'diffusion': 'Diffusion', 'stable-diffusion': 'Diffusion',
        'rl': 'Reinforcement Learning', 'reinforcement': 'Reinforcement Learning',
        'docker': 'DevOps', 'kubernetes': 'DevOps',
        'cli': 'CLI', 'tool': 'Tooling',
        'web': 'Web', 'react': 'Frontend', 'vue': 'Frontend',
        'android': 'Android', 'ios': 'iOS', 'macos': 'macOS',
        'security': 'Security', 'blockchain': 'Blockchain',
        'database': 'Database', 'sql': 'Database', 'nosql': 'Database', 'vector': 'Vector DB',
        'quantization': 'Model Compression', 'pruning': 'Model Compression', 'distillation': 'Model Compression',
        'huggingface': 'Hugging Face', 'transformers': 'Transformers',
    }

    for k, topic in keyword_map.items():
        if k in text:
            topics.add(topic)

    if not topics:
        topics.add('Misc')

    return sorted(topics)


def fetch_starred(username: str, token: Optional[str] = None, per_page: int = 100, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch starred repos for a user, paginating until no results or max_pages reached."""
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'

    repos: List[Dict[str, Any]] = []
    page = 1
    while True:
        params = {'per_page': per_page, 'page': page}
        url = f"{GITHUB_API}/users/{username}/starred"
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 401:
            raise SystemExit('Unauthorized: invalid or missing token')
        if resp.status_code != 200:
            raise SystemExit(f'Failed to fetch page {page}: {resp.status_code} {resp.text}')

        page_items = resp.json()
        if not isinstance(page_items, list):
            raise SystemExit(f'Unexpected response format for page {page}: {page_items}')

        if not page_items:
            break

        repos.extend(page_items)
        print(f'Fetched page {page}, {len(page_items)} items (total {len(repos)})')

        page += 1
        if max_pages and page > max_pages:
            break

        time.sleep(0.1)

    return repos


def build_export(repos_raw: List[Dict[str, Any]]) -> Dict[str, Any]:
    out_repos = []
    for r in repos_raw:
        item = {
            'name': r.get('name'),
            'html_url': r.get('html_url'),
            'description': r.get('description'),
            'language': r.get('language'),
            'stargazers_count': r.get('stargazers_count', 0),
            'inferred_topics': infer_topics(r),
        }
        out_repos.append(item)

    payload = {
        'generated_by': os.getenv('USER', 'export_starred.py'),
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'note': 'Exported starred repositories with inferred topics. See README.md for schema and usage.',
        'repos': out_repos,
    }
    return payload


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser(description='Export GitHub starred repos to classified JSON')
    p.add_argument('--username', '-u', required=True, help='GitHub username to fetch starred repos for')
    p.add_argument('--output', '-o', default='starred_repos_classified.json', help='Output JSON path')
    p.add_argument('--per-page', type=int, default=100, help='Results per page (max 100)')
    p.add_argument('--max-pages', type=int, default=None, help='Maximum number of pages to fetch (for testing)')
    p.add_argument('--token', '-t', default=None, help='GitHub token (optional). Can also use GITHUB_TOKEN env var')
    args = p.parse_args(argv)

    token = args.token or os.getenv('GITHUB_TOKEN')

    print(f'Fetching starred repos for user: {args.username}')
    repos_raw = fetch_starred(args.username, token=token, per_page=args.per_page, max_pages=args.max_pages)
    export = build_export(repos_raw)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(export, f, indent=2, ensure_ascii=False)

    print(f'Wrote {len(export["repos"])} items to {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
