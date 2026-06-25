"""
evaluate_ex2.py — PathFinder AI ex2 홈페이지 평가기
실제 Pathi 캐릭터(파란 후드티 늑대) 컬러 팔레트 기준
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

# 실제 Pathi 공식 블루 팔레트 (pathi_detail.png 기준)
EXPECTED_COLORS = [
    "#2563eb",   # Pathi 메인 블루 (후드티)
    "#dbeafe",   # Pathi 라이트 블루
    "#f8fafc",   # 배경 크림 화이트
    "#1e293b",   # 다크 잉크
]
# Apple DESIGN.md 추가 요구 (Action Blue)
APPLE_BLUE = "#0066cc"

DISALLOWED_COLORS = ["#f24b35", "#63e1f2", "#7df1c9"]  # 주황색 UI 금지


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
    # pathi 이미지 사용 여부 (실제 PNG 파일 참조)
    pathi_img_count = low.count("pathi.png") + low.count("pathi_detail.png")
    # 파란색 CTA (Apple Action Blue 또는 Pathi Blue)
    blue_cta = 1 if (APPLE_BLUE in css or "#2563eb" in css or "#0066cc" in css) else 0

    # ── 1. 브랜드 정렬 (20점) ─────────────────────────
    brand_parts = {
        "pathi_blue_primary":    5 if EXPECTED_COLORS[0] in css else 0,   # #2563eb
        "pathi_light_blue":      3 if EXPECTED_COLORS[1] in css else 0,   # #dbeafe
        "cream_background":      4 if EXPECTED_COLORS[2] in css else 0,   # #f8fafc
        "dark_ink":              4 if EXPECTED_COLORS[3] in css else 0,   # #1e293b
        "no_orange_ui":          4 if not any(c in css for c in DISALLOWED_COLORS) else 0,
    }
    brand_score = sum(brand_parts.values())

    # ── 2. 시각적 스토리텔링 (20점) ──────────────────
    visual_parts = {
        "pathi_image_used":    min(6, pathi_img_count * 3),           # 실제 이미지 2회 이상
        "visual_modules":      min(6, visual_cards * 0.6),            # CSS 모듈 ≥10
        "poster_ratio":        3 if ("aspect-ratio: 16" in css or "aspect-ratio:16" in css) else 0,
        "inline_svgs":         min(5, svg_count * 0.55),              # SVG 일러스트 보조
    }
    visual_score = round(sum(visual_parts.values()), 1)

    # ── 3. 텍스트 경제 (20점) ────────────────────────
    text_parts = {
        "total_words_under_650":  7 if len(words) <= 650 else max(0, 7 - (len(words) - 650) / 100),
        "short_paragraphs":       7 if paragraph_avg <= 28 else max(0, 7 - (paragraph_avg - 28) / 4),
        "short_headings":         3 if heading_max <= 12 else max(0, 3 - (heading_max - 12) / 3),
        "clear_cta_copy":         3 if ("분석 시작" in visible_text or "로드맵 만들기" in visible_text) else 0,
    }
    text_score = round(sum(text_parts.values()), 1)

    # ── 4. 접근성 (20점) ─────────────────────────────
    access_parts = {
        "korean_lang":       2 if soup.html and soup.html.get("lang") == "ko" else 0,
        "viewport":          2 if soup.find("meta", attrs={"name": "viewport"}) else 0,
        "semantic_main":     2 if soup.find("main") else 0,
        "skip_link":         2 if soup.select_one(".skip-link") else 0,
        "aria_coverage":     min(5, aria_count * 0.35),
        "focus_visible":     3 if "focus-visible" in css else 0,
        "reduced_motion":    2 if "prefers-reduced-motion" in css else 0,
        "meaningful_title":  2 if soup.title and len(soup.title.get_text(strip=True)) >= 10 else 0,
    }
    access_score = round(sum(access_parts.values()), 1)

    # ── 5. 구현 품질 (20점) ──────────────────────────
    impl_parts = {
        "responsive_breakpoints": min(6, media_queries * 1.5),
        "design_tokens":          min(5, css_vars * 0.35),
        "self_contained":         3 if not external_assets else 0,
        "route_ctas":             2 if "/analyze/new" in html else 0,
        "no_external_scripts":    2 if not soup.find("script", src=True) else 0,
        "print_rules":            2 if "@media print" in css else 0,
    }
    impl_score = round(sum(impl_parts.values()), 1)

    total = round(brand_score + visual_score + text_score + access_score + impl_score, 1)
    return {
        "file": str(path),
        "score": clamp(total),
        "metrics": {
            "word_count": len(words),
            "paragraph_avg_words": round(paragraph_avg, 1),
            "max_heading_words": heading_max,
            "svg_count": svg_count,
            "visual_modules": visual_cards,
            "aria_markers": aria_count,
            "media_queries": media_queries,
            "css_variables": css_vars,
            "external_assets": len(external_assets),
            "pathi_img_references": pathi_img_count,
        },
        "categories": {
            "brand_alignment":     {"score": brand_score,  "max": 20, "parts": brand_parts},
            "visual_storytelling": {"score": visual_score, "max": 20, "parts": visual_parts},
            "text_economy":        {"score": text_score,   "max": 20, "parts": text_parts},
            "accessibility":       {"score": access_score, "max": 20, "parts": access_parts},
            "implementation":      {"score": impl_score,   "max": 20, "parts": impl_parts},
        },
        "passed": total >= 90,
    }


if __name__ == "__main__":
    results = [evaluate(Path(arg)) for arg in sys.argv[1:]]
    print(json.dumps(results, ensure_ascii=False, indent=2))
