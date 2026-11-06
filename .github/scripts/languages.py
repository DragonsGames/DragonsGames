#!/usr/bin/env python3
import json
import os
import urllib.parse
import urllib.request
from collections import Counter
from html import escape

OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER", "DragonsGames")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = "https://api.github.com"
COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Java": "#b07219", "C++": "#f34b7d", "C": "#555555", "C#": "#178600",
    "Rust": "#dea584", "HTML": "#e34c26", "CSS": "#563d7c", "Go": "#00ADD8",
    "Shell": "#89e051", "Dart": "#00B4AB", "Kotlin": "#A97BFF", "PHP": "#4F5D95",
}

def get(url):
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-language-chart"})
    if TOKEN:
        request.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(request) as response:
        return json.load(response)

repos = []
page = 1
while True:
    batch = get(f"{API}/users/{urllib.parse.quote(OWNER)}/repos?type=owner&per_page=100&page={page}")
    repos.extend(repo for repo in batch if not repo.get("fork") and not repo.get("private"))
    if len(batch) < 100:
        break
    page += 1

counts = Counter()
for repo in repos:
    languages = get(repo["languages_url"])
    if languages:
        primary = max(languages, key=languages.get)
        counts[primary] += 1

items = counts.most_common()
if not items:
    items = [("No language data", 1)]
total = sum(value for _, value in items)
visible = items[:6]
if len(items) > 6:
    visible.append(("Other", sum(value for _, value in items[6:])))

width, height = 640, 320
bar_x, bar_y, bar_width, bar_height = 44, 104, 552, 12
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
svg.append('<rect width="640" height="320" rx="8" fill="#0d1117"/>')
svg.append('<text x="44" y="54" fill="#b392ff" font-family="Arial,sans-serif" font-size="22" font-weight="700">Languages by repo count</text>')
svg.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" rx="6" fill="#30363d"/>')
position = bar_x
for language, value in visible:
    segment = bar_width * value / total
    color = COLORS.get(language, "#8b949e")
    svg.append(f'<rect x="{position:.2f}" y="{bar_y}" width="{segment:.2f}" height="{bar_height}" fill="{color}"/>')
    position += segment
for index, (language, value) in enumerate(visible):
    column, row = index % 2, index // 2
    x, y = 44 + column * 280, 150 + row * 34
    color = COLORS.get(language, "#8b949e")
    percent = value * 100 / total
    svg.append(f'<circle cx="{x + 6}" cy="{y - 5}" r="6" fill="{color}"/>')
    svg.append(f'<text x="{x + 20}" y="{y}" fill="#f0f6fc" font-family="Arial,sans-serif" font-size="14">{escape(language)} {percent:.2f}%</text>')
svg.append('<text x="44" y="294" fill="#8b949e" font-family="Arial,sans-serif" font-size="12">Public repositories · updated automatically</text>')
svg.append('</svg>')
os.makedirs("koi", exist_ok=True)
with open("koi/languages.svg", "w", encoding="utf-8") as file:
    file.write("\n".join(svg) + "\n")