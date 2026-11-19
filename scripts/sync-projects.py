"""Refresh the published project cards from GitHub's public repository list."""

import html
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import quote

owner = sys.argv[1]
pages = json.loads(subprocess.check_output([
    "gh", "api", f"users/{quote(owner, safe='')}/repos?per_page=100",
    "--paginate", "--slurp",
]))
repos = sorted(
    (repo for page in pages for repo in page
     if not repo["private"] and repo["name"].casefold() != owner.casefold()),
    key=lambda repo: (-repo["stargazers_count"], repo["name"].casefold()),
)

cards = []
for repo in repos:
    url = html.escape(repo["html_url"], quote=True)
    name = html.escape(repo["name"])
    description = html.escape(repo["description"] or repo["language"] or "GitHub repository")
    stars = repo["stargazers_count"]
    cards.append(
        f'<td width="50%" valign="top"><strong><a href="{url}">{name}</a></strong>'
        f'<br>{description}<br><a href="{url}/stargazers">★ {stars:,}</a></td>'
    )

rows = [
    "<tr>" + "".join(cards[index:index + 2]) + "</tr>"
    for index in range(0, len(cards), 2)
]
table = "\n".join(["<table>", *rows, "</table>"]) if rows else "No public projects yet."

readme = Path(__file__).resolve().parents[1] / "README.md"
start = "<!-- projects:start -->"
end = "<!-- projects:end -->"
content = readme.read_text()
if content.count(start) != 1 or content.count(end) != 1 or content.index(start) > content.index(end):
    raise SystemExit("Expected one ordered pair of project markers.")
before, _, rest = content.partition(start)
_, _, after = rest.partition(end)
updated = f"{before}{start}\n\n{table}\n\n{end}{after}"
if updated != content:
    readme.write_text(updated)
