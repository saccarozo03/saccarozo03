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

QUOTE_START = "<!--DAILY_QUOTE_START-->"
QUOTE_END = "<!--DAILY_QUOTE_END-->"

def replace_between(text, start, end, new_content):
    pattern = re.compile(rf"({re.escape(start)})(.*?)(\s*{re.escape(end)})", re.DOTALL)
    return pattern.sub(rf"\1{new_content}\3", text)

def fetch_recent_repos(username, limit):
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

FUNNY_QUOTES = [
    ("It works on my machine.", "Every Developer Ever"),
    ("99 little bugs in the code. Take one down, patch it around... 127 little bugs in the code.", "The Developer's Anthem"),
    ("I don't always test my code, but when I do, I do it in production.", "Senior Dev Energy"),
    ("Debugging is like being the detective in a crime movie where you are also the murderer.", "Filipe Fortes"),
    ("A QA engineer walks into a bar. Orders 1 beer. Orders 0 beers. Orders 99999 beers. Orders -1 beers. Orders NULL beers. The bar bursts into flames.", "Anonymous QA"),
    ("It's not a bug — it's an undocumented feature.", "Every Programmer, Ever"),
    ("Why do Java developers wear glasses? Because they don't C#.", "Dad Joke Dept."),
    ("There are only 10 types of people: those who understand binary and those who don't.", "Binary Philosopher"),
    ("Weeks of coding can save you hours of planning.", "Anonymous"),
    ("Always code as if the guy maintaining your code is a violent psychopath who knows where you live.", "John Woods"),
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("The best thing about a boolean is even if you are wrong, you are only off by a bit.", "Anonymous"),
    ("Code never lies, comments sometimes do.", "Ron Jeffries"),
    ("If debugging is removing bugs, then programming must be putting them in.", "Edsger Dijkstra"),
    ("Stack Overflow is down. I have no idea what to do.", "Every Developer, 2013"),
    ("My code doesn't work. I have no idea why. My code works. I have no idea why.", "Anonymous"),
    ("The DevOps engineer said: 'Works on my container.'", "Modern Developer"),
    ("I don't fix bugs. I create new features called 'unexpected behavior'.", "Me, 2AM"),
    ("Given enough coffee and Stack Overflow, any bug can be copy-pasted away.", "Dev Philosophy"),
    ("Dear past me: the bug is on line 47. You're welcome. Dear future me: I'm sorry.", "Every Developer"),
    ("Documentation is like a love letter to your future self. I never write love letters.", "Lazy Dev"),
    ("I wrote clean code once. Then I added 'just one quick fix'.", "Famous Last Words"),
    ("The code works. Nobody knows why. Do not touch it. Ever.", "Production Comment #1"),
    ("pip install sanity — ERROR: No matching distribution found.", "Terminal at 3AM"),
    ("sudo make me a sandwich. ERROR: permission denied. sudo sudo make me a sandwich.", "Linux Wisdom"),
]


def fetch_daily_quote():
    today = datetime.now(timezone.utc)
    index = (today.year * 366 + today.timetuple().tm_yday) % len(FUNNY_QUOTES)
    return FUNNY_QUOTES[index]

def build_quote_block(content, author):
    return (
        "\n"
        '<div align="center">\n'
        '<table><tr><td align="center" width="680">\n'
        "<br/>\n"
        '<img src="https://img.shields.io/badge/C%C3%A2u%20B%E1%BB%B1a%20H%C3%B4m%20Nay-1a1a2e?style=flat-square&logo=bookstack&logoColor=7eb3ff" />'
        "<br/><br/>\n"
        f"<i>\u275d {content} \u275e</i>\n"
        "<br/><br/>\n"
        f"<b>\u2014 {author}</b>\n"
        "<br/><br/>\n"
        "</td></tr></table>\n"
        "</div>\n"
    )

def main():
    with open(README_PATH, "r", encoding="utf-8") as f:
        readme = f.read()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    readme = replace_between(readme, LAST_UPDATED_START, LAST_UPDATED_END, today)

    repos = fetch_recent_repos(USERNAME, RECENT_REPOS_LIMIT)
    recent_block = build_recent_repos_block(repos)
    readme = replace_between(readme, RECENT_START, RECENT_END, recent_block)

    content, author = fetch_daily_quote()
    quote_block = build_quote_block(content, author)
    readme = replace_between(readme, QUOTE_START, QUOTE_END, quote_block)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    main()
