#!/usr/bin/env python3
"""Replace shared nav+mobile panel and footer in PCG_*.html from partials/.

Run from repo root: python3 scripts/sync_pcg_partials.py

Edit partials/nav-and-panel.html and partials/footer.html, then run this script
to propagate changes to all PCG_*.html files. Internal links use index.html,
about.html, etc.; rename outputs on deploy if your host expects those names
instead of PCG_*.html.
"""
from __future__ import annotations

import pathlib


def extract_nav_through_panel(text: str) -> tuple[int, int] | None:
    start = text.find('<nav class="nav" id="nav">')
    if start < 0:
        return None
    p = text.find('<div class="nav__panel" id="navPanel">', start)
    if p < 0:
        return None
    i = p + len('<div class="nav__panel" id="navPanel">')
    depth = 1
    while i < len(text) and depth:
        nxt = text.find("<", i)
        if nxt < 0:
            return None
        if text.startswith("</div>", nxt):
            depth -= 1
            i = nxt + 6
            if depth == 0:
                return (start, nxt + 6)
        elif text.startswith("<div", nxt) and not text.startswith("</div>", nxt):
            depth += 1
            i = nxt + 4
        else:
            i = nxt + 1
    return None


def extract_footer_span(text: str) -> tuple[int, int] | None:
    a = text.find("<footer class=\"footer\">")
    b = text.find("</footer>", a)
    if a < 0 or b < 0:
        return None
    return (a, b + len("</footer>"))


def main() -> None:
    root = pathlib.Path(__file__).resolve().parent.parent
    nav_path = root / "partials" / "nav-and-panel.html"
    foot_path = root / "partials" / "footer.html"
    nav_new = nav_path.read_text()
    foot_new = foot_path.read_text()

    for p in sorted(root.glob("PCG_*.html")):
        text = p.read_text()
        nav_span = extract_nav_through_panel(text)
        foot_span = extract_footer_span(text)
        if not nav_span or not foot_span:
            print(f"skip (no nav/footer): {p.name}")
            continue
        new_text = text[: nav_span[0]] + nav_new + text[nav_span[1] : foot_span[0]] + foot_new + text[foot_span[1] :]
        p.write_text(new_text)
        print(f"updated {p.name}")


if __name__ == "__main__":
    main()
