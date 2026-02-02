import os
import re
import requests
from datetime import datetime, timezone

USERNAME = "saccarozo03"
RECENT_REPOS_LIMIT = 5

README_PATH = "README.md"

LAST_UPDATED_START = "<!--LAST_UPDATED-->"
LAST_UPDATED_END = "<!--/LAST_UPDATED-->"

RECENT_START = "<!--RECENT_REPOS_START-->"
RECENT_END = "<!--RECENT_REPOS_END-->"

def replace_between(text: str, start: str, end: str, new_content: str) -> str:
    pattern = re.compile(rf"({re.escape(start)})(.*?)(\s*{re.escape(end)})", re.DOTALL)
    return pattern.sub(rf"\1{new_content}\3", text)

def fetch_recent_repos(username: str, limit: int):
    url = f"https://api.github.com/users/{username}/repos"
    params = {"sort": "pushed", "direction": "desc", "per_page": str(limit)}

    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    r = requests.get(url, params=params, headers=headers, timeout=20)
    r.raise_for_status()

    repos = [repo for repo in r.json() if not repo.get("fork")]
    return repos[:limit]

def build_recent_repos_block(repos):
    lines = []
    for repo in repos:
        name = repo["name"]
        url = repo["html_url"]
        desc = repo.get("description") or ""
        lang = repo.get("language") or ""
        stars = repo.get("stargazers_count", 0)

        lines.append(f"- **[{name}]({url})** — {desc}  \n  _{lang} • ★ {stars}_")

    return "\n" + "\n".join(lines) + "\n"

def main():
    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    readme = replace_between(readme, LAST_UPDATED_START, LAST_UPDATED_END, today)

    repos = fetch_recent_repos(USERNAME, RECENT_REPOS_LIMIT)
    block = build_recent_repos_block(repos)
    readme = replace_between(readme, RECENT_START, RECENT_END, block)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    main()
