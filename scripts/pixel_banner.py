"""Generate assets/pixel-banner.svg: the name drawn in pixels on a dot grid.

Pixels drop in one by one, a red scan line sweeps across, and a few cells twinkle.
Pure SVG + CSS animation, so it renders inside a README <img>. Standard library only.
"""

from pathlib import Path

FONT = {
    "J": ["..XXX", "...X.", "...X.", "...X.", "X..X.", "X..X.", ".XX.."],
    "A": [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "T": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
    "I": ["XXX", ".X.", ".X.", ".X.", ".X.", ".X.", "XXX"],
    "N": ["X...X", "XX..X", "X.X.X", "X.X.X", "X..XX", "X...X", "X...X"],
    "P": ["XXXX.", "X...X", "X...X", "XXXX.", "X....", "X....", "X...."],
    "D": ["XXXX.", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXX."],
    "E": ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "XXXXX"],
    "Y": ["X...X", "X...X", ".X.X.", "..X..", "..X..", "..X..", "..X.."],
    " ": ["..", "..", "..", "..", "..", "..", ".."],
}

W, H = 1200, 300
CELL = 14
BG, DOT, FG, RED = "#080606", "#2a2221", "#ede7df", "#e0263f"


def main() -> None:
    text = "JATIN PANDEY"
    cols = sum(len(FONT[c][0]) + 1 for c in text) - 1
    x0 = (W - cols * CELL) // 2
    y0 = 70
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" shape-rendering="crispEdges">',
        "<style>",
        ".p{animation:cycle 8s steps(1) infinite}",
        "@keyframes cycle{0%{opacity:0;transform:translateY(-14px)}3%{opacity:.6;transform:translateY(-6px)}6%,100%{opacity:1;transform:none}}",
        ".w{animation:wave 3.2s ease-in-out infinite}",
        "@keyframes wave{0%,70%,100%{fill:#ede7df}80%{fill:#e0263f}}",
        ".cur{animation:blink 1s steps(1) infinite}",
        "@keyframes blink{50%{opacity:0}}",
        ".scan{animation:scan 4s linear infinite}",
        "@keyframes scan{0%{transform:translateX(-80px)}100%{transform:translateX(1280px)}}",
        ".tw{animation:tw 2.4s ease-in-out infinite}",
        "@keyframes tw{0%,100%{opacity:0}50%{opacity:1}}",
        "@media (prefers-reduced-motion:reduce){.p,.w{animation:none;opacity:1}.scan,.tw,.cur{animation:none;opacity:0}}",
        "</style>",
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        '<defs><pattern id="d" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<rect x="10" y="10" width="2" height="2" fill="{DOT}"/></pattern></defs>',
        f'<rect width="{W}" height="{H}" fill="url(#d)"/>',
    ]
    for i, (cx, cy) in enumerate([(98, 54), (1100, 76), (230, 252), (1012, 230), (560, 32), (760, 270), (54, 186)]):
        out.append(f'<rect class="tw" x="{cx}" y="{cy}" width="6" height="6" fill="{RED}" style="animation-delay:{i * 0.37:.2f}s"/>')

    n = 0
    cx = x0
    for ch in text:
        glyph = FONT[ch]
        for gy, row in enumerate(glyph):
            for gx, c in enumerate(row):
                if c != "X":
                    continue
                x = cx + gx * CELL
                # Drop-in order follows reading order; the colour wave follows x position.
                drop = 0.012 * n
                wave = (x - x0) / (cols * CELL) * 1.6
                out.append(
                    f'<g class="p" style="animation-delay:{drop:.3f}s"><rect class="w" x="{x}" y="{y0 + gy * CELL}" '
                    f'width="{CELL - 2}" height="{CELL - 2}" fill="{FG}" style="animation-delay:{wave:.3f}s"/></g>'
                )
                n += 1
        cx += (len(glyph[0]) + 1) * CELL

    # Blinking pixel cursor after the name.
    out.append(f'<rect class="cur" x="{cx}" y="{y0 + 5 * CELL}" width="{CELL - 2}" height="{2 * CELL - 2}" fill="{RED}"/>')
    out.append(f'<rect class="scan" x="0" y="{y0 - 6}" width="6" height="{7 * CELL + 12}" fill="{RED}" opacity=".85"/>')
    out.append(
        f'<text x="{W // 2}" y="{y0 + 7 * CELL + 52}" text-anchor="middle" fill="#9a918a" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="16" letter-spacing="4">'
        "AI &amp; FULL-STACK DEVELOPER · CTF GRINDER · LOCAL-FIRST EVERYTHING</text>"
    )
    out.append("</svg>")
    path = Path(__file__).resolve().parent.parent / "assets" / "pixel-banner.svg"
    path.write_text("\n".join(out))
    print(f"wrote {path} ({n} pixels)")


if __name__ == "__main__":
    main()
