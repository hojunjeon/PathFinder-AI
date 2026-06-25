from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

EXPECTED_COLORS = ["#faf8f6", "#f24b35", "#111111", "#fff0eb"]
DISALLOWED_PRIMARY = ["#07111f", "#63e1f2", "#7df1c9"]


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def evaluate(path: Path) -> dict:
    html = path.read_text(encoding="utf-8")
    low = html.lower()
    soup = BeautifulSoup(html, "html.parser")
    css = "\n".join(tag.get_text(" ", strip=False) for tag in soup.find_all("style")).lower()
    visible_text = " ".join(soup.stripped_strings)
    words = re.findall(r"[0-9a-zA-Z가-힣]+", visible_text)
    paragraphs = [re.findall(r"[0-9a-zA-Z가-힣]+", p.get_text(" ", strip=True)) for p in soup.find_all("p")]
    paragraph_avg = sum(map(len, paragraphs)) / max(1, len(paragraphs))
    headings = [re.findall(r"[0-9a-zA-Z가-힣]+", h.get_text(" ", strip=True)) for h in soup.find_all(re.compile(r"^h[1-3]$"))]
    heading_max = max((len(h) for h in headings), default=0)
    svg_count = len(soup.find_all("svg"))
    visual_cards = len(soup.select(".poster-frame, .story-visual, .output-card, .pathi-band, .value-icon"))
    aria_count = len(soup.select("[aria-label], [aria-labelledby], [role='img']"))
    media_queries = css.count("@media")
    css_vars = len(set(re.findall(r"--[a-z0-9-]+\s*:", css)))
    external_assets = re.findall(r"(?:src|href)=[\"']https?://", low)

    brand_parts = {
        "warm_off_white": 4 if EXPECTED_COLORS[0] in css else 0,
        "orange_primary": 5 if EXPECTED_COLORS[1] in css else 0,
        "black_typography": 4 if EXPECTED_COLORS[2] in css else 0,
        "peach_support": 3 if EXPECTED_COLORS[3] in css else 0,
        "avoids_previous_neon_dark": 4 if not any(color in css for color in DISALLOWED_PRIMARY) else 0,
    }
    brand_score = sum(brand_parts.values())

    visual_parts = {
        "inline_svg_assets": min(8, svg_count * 0.8),
        "visual_modules": min(6, visual_cards * 0.6),
        "poster_ratio": 3 if "aspect-ratio: 16" in css or "aspect-ratio:16" in css else 0,
        "pathi_repetition": 3 if low.count("#pathi") + low.count('href="#pathi"') >= 3 else 0,
    }
    visual_score = round(sum(visual_parts.values()), 1)

    text_parts = {
        "total_text_under_650_words": 7 if len(words) <= 650 else max(0, 7 - (len(words) - 650) / 100),
        "short_paragraphs": 7 if paragraph_avg <= 28 else max(0, 7 - (paragraph_avg - 28) / 4),
        "short_headings": 3 if heading_max <= 12 else max(0, 3 - (heading_max - 12) / 3),
        "clear_cta_copy": 3 if "분석 시작" in visible_text or "로드맵 만들기" in visible_text else 0,
    }
    text_score = round(sum(text_parts.values()), 1)

    access_parts = {
        "korean_lang": 2 if soup.html and soup.html.get("lang") == "ko" else 0,
        "viewport": 2 if soup.find("meta", attrs={"name": "viewport"}) else 0,
        "semantic_main": 2 if soup.find("main") else 0,
        "skip_link": 2 if soup.select_one(".skip-link") else 0,
        "aria_coverage": min(5, aria_count * 0.35),
        "focus_visible": 3 if "focus-visible" in css else 0,
        "reduced_motion": 2 if "prefers-reduced-motion" in css else 0,
        "meaningful_title": 2 if soup.title and len(soup.title.get_text(strip=True)) >= 10 else 0,
    }
    access_score = round(sum(access_parts.values()), 1)

    implementation_parts = {
        "responsive_breakpoints": min(6, media_queries * 1.5),
        "design_tokens": min(5, css_vars * 0.35),
        "self_contained": 3 if not external_assets else 0,
        "route_ctas": 2 if "/analyze/new" in html else 0,
        "no_javascript_dependency": 2 if not soup.find("script", src=True) else 0,
        "print_rules": 2 if "@media print" in css else 0,
    }
    implementation_score = round(sum(implementation_parts.values()), 1)

    total = round(brand_score + visual_score + text_score + access_score + implementation_score, 1)
    return {
        "file": str(path),
        "score": clamp(total),
        "metrics": {
            "word_count": len(words),
            "paragraph_average_words": round(paragraph_avg, 1),
            "max_heading_words": heading_max,
            "svg_count": svg_count,
            "visual_modules": visual_cards,
            "aria_markers": aria_count,
            "media_queries": media_queries,
            "css_variables": css_vars,
            "external_assets": len(external_assets),
        },
        "categories": {
            "brand_alignment": {"score": brand_score, "max": 20, "parts": brand_parts},
            "visual_storytelling": {"score": visual_score, "max": 20, "parts": visual_parts},
            "text_economy": {"score": text_score, "max": 20, "parts": text_parts},
            "accessibility": {"score": access_score, "max": 20, "parts": access_parts},
            "implementation": {"score": implementation_score, "max": 20, "parts": implementation_parts},
        },
        "passed": total >= 90,
    }


if __name__ == "__main__":
    results = [evaluate(Path(arg)) for arg in sys.argv[1:]]
    print(json.dumps(results, ensure_ascii=False, indent=2))
