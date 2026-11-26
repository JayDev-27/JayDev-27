"""Generate an up-to-date streak stats SVG from live GitHub contributions (including private)."""

import datetime
from pathlib import Path
import re
import sys
import urllib.request

owner = sys.argv[1] if len(sys.argv) > 1 else "JayDev-27"
today = datetime.date.today()

all_days = {}
first_active_date = None

for year in range(2019, today.year + 1):
    url = f"https://github.com/users/{owner}/contributions?from={year}-01-01&to={year}-12-31"
    html = urllib.request.urlopen(url, timeout=20).read().decode("utf-8")
    days = re.findall(
        r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="(contribution-day-component-[^"]+)"[^>]*data-level="(\d+)"',
        html,
    )
    tips = dict(re.findall(r'for="(contribution-day-component-[^"]+)"[^>]*>([^<]+)<', html))
    for date_str, cid, _lvl in days:
        tip = tips.get(cid, "")
        m = re.match(r"^(\d+)\s+contribution", tip)
        cnt = int(m.group(1)) if m else 0
        all_days[date_str] = cnt
        if cnt > 0 and (first_active_date is None or date_str < first_active_date):
            first_active_date = date_str

today_str = today.isoformat()
sorted_dates = sorted(d for d in all_days if d <= today_str)
total_contributions = sum(all_days[d] for d in sorted_dates)

# Longest streak
cur = 0
cur_start = ""
longest = 0
longest_range = ("", "")
for d in sorted_dates:
    if all_days[d] > 0:
        if cur == 0:
            cur_start = d
        cur += 1
        if cur > longest:
            longest = cur
            longest_range = (cur_start, d)
    else:
        cur = 0

# Current streak ending today (or yesterday if no commits yet today)
end_idx = len(sorted_dates) - 1
while end_idx > 0 and all_days[sorted_dates[end_idx]] == 0 and sorted_dates[end_idx] == today_str:
    end_idx -= 1

c_streak = 0
c_end = sorted_dates[end_idx] if sorted_dates else today_str
c_start = c_end
i = end_idx
while i >= 0 and all_days[sorted_dates[i]] > 0:
    c_start = sorted_dates[i]
    c_streak += 1
    i -= 1


def fmt_short(iso_str: str) -> str:
    d = datetime.date.fromisoformat(iso_str)
    return d.strftime("%b %-d")


def fmt_full(iso_str: str) -> str:
    d = datetime.date.fromisoformat(iso_str)
    return d.strftime("%b %-d, %Y")


total_range = f"{fmt_full(first_active_date)} - Present" if first_active_date else "Present"
curr_range = f"{fmt_short(c_start)} - {fmt_short(c_end)}" if c_streak > 0 else "No active streak"
long_range = f"{fmt_short(longest_range[0])} - {fmt_short(longest_range[1])}" if longest > 0 else "-"

svg = f"""<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'
        style='isolation: isolate' viewBox='0 0 495 195' width='495px' height='195px' direction='ltr'>
    <style>
        @keyframes currstreak {{
            0% {{ font-size: 3px; opacity: 0.2; }}
            80% {{ font-size: 34px; opacity: 1; }}
            100% {{ font-size: 28px; opacity: 1; }}
        }}
        @keyframes fadein {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
    </style>
    <defs>
        <clipPath id='outer_rectangle'>
            <rect width='495' height='195' rx='4.5'/>
        </clipPath>
        <mask id='mask_out_ring_behind_fire'>
            <rect width='495' height='195' fill='white'/>
            <ellipse id='mask-ellipse' cx='247.5' cy='32' rx='13' ry='18' fill='black'/>
        </mask>
    </defs>
    <g clip-path='url(#outer_rectangle)'>
        <g style='isolation: isolate'>
            <rect stroke='#000000' stroke-opacity='0' fill='#080606' rx='4.5' x='0.5' y='0.5' width='494' height='194'/>
        </g>
        <g style='isolation: isolate'>
            <line x1='165' y1='28' x2='165' y2='170' vector-effect='non-scaling-stroke' stroke-width='1' stroke='#2a1517' stroke-linejoin='miter' stroke-linecap='square' stroke-miterlimit='3'/>
            <line x1='330' y1='28' x2='330' y2='170' vector-effect='non-scaling-stroke' stroke-width='1' stroke='#2a1517' stroke-linejoin='miter' stroke-linecap='square' stroke-miterlimit='3'/>
        </g>
        <g style='isolation: isolate'>
            <g transform='translate(82.5, 48)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#ede7df' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='700' font-size='28px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.6s'>
                    {total_contributions:,}
                </text>
            </g>
            <g transform='translate(82.5, 84)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#b9b1a8' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='400' font-size='14px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.7s'>
                    Total Contributions
                </text>
            </g>
            <g transform='translate(82.5, 114)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#7d756e' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='400' font-size='12px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.8s'>
                    {total_range}
                </text>
            </g>
        </g>
        <g style='isolation: isolate'>
            <g transform='translate(247.5, 108)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#e0263f' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='700' font-size='14px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.9s'>
                    Current Streak
                </text>
            </g>
            <g transform='translate(247.5, 145)'>
                <text x='0' y='21' stroke-width='0' text-anchor='middle' fill='#7d756e' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='400' font-size='12px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 0.9s'>
                    {curr_range}
                </text>
            </g>
            <g mask='url(#mask_out_ring_behind_fire)'>
                <circle cx='247.5' cy='71' r='40' fill='none' stroke='#e0263f' stroke-width='5' style='opacity: 0; animation: fadein 0.5s linear forwards 0.4s'></circle>
            </g>
            <g transform='translate(247.5, 19.5)' stroke-opacity='0' style='opacity: 0; animation: fadein 0.5s linear forwards 0.6s'>
                <path d='M -12 -0.5 L 15 -0.5 L 15 23.5 L -12 23.5 L -12 -0.5 Z' fill='none'/>
                <path d='M 1.5 0.67 C 1.5 0.67 2.24 3.32 2.24 5.47 C 2.24 7.53 0.89 9.2 -1.17 9.2 C -3.23 9.2 -4.79 7.53 -4.79 5.47 L -4.76 5.11 C -6.78 7.51 -8 10.62 -8 13.99 C -8 18.41 -4.42 22 0 22 C 4.42 22 8 18.41 8 13.99 C 8 8.6 5.41 3.79 1.5 0.67 Z M -0.29 19 C -2.07 19 -3.51 17.6 -3.51 15.86 C -3.51 14.24 -2.46 13.1 -0.7 12.74 C 1.07 12.38 2.9 11.53 3.92 10.16 C 4.31 11.45 4.51 12.81 4.51 14.2 C 4.51 16.85 2.36 19 -0.29 19 Z' fill='#e0263f' stroke-opacity='0'/>
            </g>
            <g transform='translate(247.5, 48)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#ede7df' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='700' font-size='28px' font-style='normal' style='animation: currstreak 0.6s linear forwards'>
                    {c_streak}
                </text>
            </g>
        </g>
        <g style='isolation: isolate'>
            <g transform='translate(412.5, 48)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#ede7df' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='700' font-size='28px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 1.2s'>
                    {longest}
                </text>
            </g>
            <g transform='translate(412.5, 84)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#b9b1a8' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='400' font-size='14px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 1.3s'>
                    Longest Streak
                </text>
            </g>
            <g transform='translate(412.5, 114)'>
                <text x='0' y='32' stroke-width='0' text-anchor='middle' fill='#7d756e' stroke='none' font-family='"Segoe UI", Ubuntu, sans-serif' font-weight='400' font-size='12px' font-style='normal' style='opacity: 0; animation: fadein 0.5s linear forwards 1.4s'>
                    {long_range}
                </text>
            </g>
        </g>
    </g>
</svg>
"""

out_path = Path(__file__).resolve().parents[1] / "assets" / "streak-stats.svg"
out_path.write_text(svg, encoding="utf-8")
print(f"Wrote {out_path}: total={total_contributions:,} ({total_range}), curr={c_streak} ({curr_range}), longest={longest} ({long_range})")
