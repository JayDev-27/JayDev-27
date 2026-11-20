"""Refresh the published project badges from GitHub's public repository list."""

import html
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import quote, urlencode

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

badges = []
for repo in repos:
    url = html.escape(repo["html_url"], quote=True)
    name = repo["name"]
    query = urlencode({
        "style": "flat-square",
        "logo": "github",
        "labelColor": "555",
        "color": "c41226",
        "label": name.upper(),
    })
    badge = f"https://img.shields.io/github/stars/{quote(repo['full_name'], safe='/')}?{query}"
    alt = html.escape(f"{name} GitHub stars", quote=True)
    badges.append(f'<a href="{url}"><img src="{html.escape(badge, quote=True)}" alt="{alt}"></a>')

group = "\n".join(['<div align="center">', *badges, '</div>']) if badges else "No public projects yet."

readme = Path(__file__).resolve().parents[1] / "README.md"
start = "<!-- projects:start -->"
end = "<!-- projects:end -->"
content = readme.read_text()
if content.count(start) != 1 or content.count(end) != 1 or content.index(start) > content.index(end):
    raise SystemExit("Expected one ordered pair of project markers.")
before, _, rest = content.partition(start)
_, _, after = rest.partition(end)
updated = f"{before}{start}\n\n{group}\n\n{end}{after}"
if updated != content:
    readme.write_text(updated)
