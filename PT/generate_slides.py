from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
W, H = 1920, 1080

PRIMARY = "#4a154b"
PRIMARY_2 = "#611f69"
CREAM = "#f4ede4"
LAV = "#f9f0ff"
BLUE = "#1264a3"
INK = "#1d1d1d"
MUTE = "#696969"
WHITE = "#ffffff"
GREEN = "#007a5a"
LINE = "#e6e6e6"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "malgunbd.ttf" if bold else "malgun.ttf"
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)


F = {
    "hero": font(86, True),
    "title": font(58, True),
    "h2": font(36, True),
    "h3": font(28, True),
    "body": font(25),
    "body_b": font(25, True),
    "small": font(20),
    "small_b": font(20, True),
    "micro": font(17, True),
}


def cover_bg() -> Image.Image:
    bg_path = ROOT / "ai_background.png"
    if bg_path.exists():
        bg = Image.open(bg_path).convert("RGB")
        scale = max(W / bg.width, H / bg.height)
        bg = bg.resize((int(bg.width * scale), int(bg.height * scale)))
        x = (bg.width - W) // 2
        y = (bg.height - H) // 2
        bg = bg.crop((x, y, x + W, y + H)).filter(ImageFilter.GaussianBlur(1.2))
    else:
        bg = Image.new("RGB", (W, H), CREAM)
    veil = Image.new("RGBA", (W, H), (244, 237, 228, 188))
    bg = Image.alpha_composite(bg.convert("RGBA"), veil)
    return bg


def draw_wrapped(draw: ImageDraw.ImageDraw, xy, text: str, width: int, fnt, fill=INK, gap=10):
    x, y = xy
    lines = []
    for para in text.split("\n"):
        buf = ""
        for ch in para:
            trial = buf + ch
            if draw.textbbox((0, 0), trial, font=fnt)[2] <= width:
                buf = trial
            else:
                if buf:
                    lines.append(buf)
                buf = ch
        if buf:
            lines.append(buf)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += draw.textbbox((0, 0), line, font=fnt)[3] + gap
    return y


def rr(draw, box, fill, outline=None, width=1, radius=24):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow(draw, start, end, fill=PRIMARY, width=6):
    draw.line((start, end), fill=fill, width=width)
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    if abs(dx) >= abs(dy):
        s = 1 if dx >= 0 else -1
        pts = [(x2, y2), (x2 - 26 * s, y2 - 14), (x2 - 26 * s, y2 + 14)]
    else:
        s = 1 if dy >= 0 else -1
        pts = [(x2, y2), (x2 - 14, y2 - 26 * s), (x2 + 14, y2 - 26 * s)]
    draw.polygon(pts, fill=fill)


def slide_base(n: int, title: str, note: str):
    img = cover_bg()
    draw = ImageDraw.Draw(img)
    draw.text((118, 66), f"{n:02d}", font=F["micro"], fill=PRIMARY)
    draw.text((180, 54), title, font=F["title"], fill=INK)
    draw.line((118, 132, 1800, 132), fill=(74, 21, 75, 70), width=2)
    rr(draw, (118, 982, 900, 1034), fill=(255, 255, 255, 230), outline=LINE, radius=26)
    draw.text((148, 994), "발표자 노트", font=F["small_b"], fill=PRIMARY)
    draw.text((304, 994), note, font=F["small"], fill=MUTE)
    return img, draw


def pill(draw, xy, text, fill=PRIMARY, text_fill=WHITE, padx=26):
    x, y = xy
    bbox = draw.textbbox((0, 0), text, font=F["small_b"])
    w, h = bbox[2] + padx * 2, 48
    rr(draw, (x, y, x + w, y + h), fill=fill, radius=24)
    draw.text((x + padx, y + 10), text, font=F["small_b"], fill=text_fill)
    return x + w + 12


def card(draw, box, title, body, accent=PRIMARY):
    rr(draw, box, fill=(255, 255, 255, 238), outline=LINE, radius=28)
    x1, y1, x2, _ = box
    draw.rectangle((x1, y1, x1 + 10, box[3]), fill=accent)
    draw.text((x1 + 36, y1 + 30), title, font=F["h3"], fill=accent)
    draw_wrapped(draw, (x1 + 36, y1 + 82), body, x2 - x1 - 72, F["body"], fill=INK, gap=8)


def slide1():
    img, draw = slide_base(1, "PathFiner AI 소개", "문제 -> 입력 -> 개인화 로드맵")
    draw.text((150, 230), "PathFiner AI", font=F["hero"], fill=PRIMARY)
    draw_wrapped(
        draw,
        (154, 340),
        "취준생을 위한 기업/직무별 면접 대비\n개인 맞춤형 학습 및 준비 로드맵 추천 서비스",
        780,
        F["h2"],
        fill=INK,
        gap=16,
    )
    x = 154
    for t in ["2인 팀 프로젝트", "Vue", "Django REST", "FastAPI", "gpt-5-nano", "GraphRAG"]:
        x = pill(draw, (x, 505), t, fill=PRIMARY if t == "GraphRAG" else LAV, text_fill=WHITE if t == "GraphRAG" else INK, padx=22)

    flow_y = 720
    labels = [("공고", BLUE), ("자소서", PRIMARY_2), ("프로필", GREEN), ("GraphRAG", PRIMARY), ("로드맵", INK)]
    x = 165
    centers = []
    for label, color in labels:
        rr(draw, (x, flow_y, x + 220, flow_y + 110), fill=WHITE, outline=color, width=3, radius=26)
        draw.text((x + 58, flow_y + 36), label, font=F["h3"], fill=color)
        centers.append((x + 220, flow_y + 55))
        x += 300
    for i in range(4):
        arrow(draw, (centers[i][0] + 12, flow_y + 55), (centers[i][0] + 76, flow_y + 55), fill=PRIMARY, width=5)

    rr(draw, (1130, 220, 1748, 580), fill=(255, 255, 255, 230), outline=LINE, radius=30)
    draw.text((1180, 265), "결과 화면의 핵심", font=F["h2"], fill=PRIMARY)
    for i, t in enumerate(["역량 gap", "공부 우선순위", "예상 질문", "답변 방향", "근거와 꼬리질문"]):
        y = 340 + i * 42
        draw.ellipse((1190, y + 8, 1206, y + 24), fill=PRIMARY)
        draw.text((1222, y), t, font=F["body"], fill=INK)
    return img


def slide2():
    img, draw = slide_base(2, "문제 정의 - 준비 방향보다 귀찮은 분석 과정", "반복 비교 · 우선순위 · 누락 위험")
    draw_wrapped(draw, (145, 190), "문제는 정보를 아예 모르는 것이 아니라,\n매번 정보를 비교하고 준비 기준을 다시 만드는 과정입니다.", 820, F["h2"], fill=INK, gap=15)
    cx, cy = 565, 610
    items = [("채용공고\n요구역량", 300, 330), ("자소서\n경험", 750, 330), ("부족 개념\n추출", 845, 650), ("공부\n우선순위", 520, 800), ("예상질문\n생성", 210, 645)]
    for text, x, y in items:
        rr(draw, (x, y, x + 255, y + 125), fill=WHITE, outline=LINE, radius=28)
        draw_wrapped(draw, (x + 38, y + 28), text, 180, F["h3"], fill=PRIMARY, gap=6)
    for _, x, y in items:
        arrow(draw, (x + 128, y + 125), (cx, cy), fill=(74, 21, 75, 130), width=4)
    rr(draw, (430, 520, 700, 700), fill=PRIMARY, radius=90)
    draw.text((473, 568), "반복 분석", font=F["h2"], fill=WHITE)
    draw.text((492, 622), "매 지원마다 재시작", font=F["small"], fill="#d9bdde")
    card(draw, (1130, 230, 1725, 430), "시간이 오래 걸림", "공고 요구사항, 자기소개서, 경험을 매번 수작업으로 대조", BLUE)
    card(draw, (1130, 480, 1725, 680), "깊이 판단이 어려움", "어느 질문에 답할 수 있을 정도로 공부해야 하는지 불명확", PRIMARY)
    card(draw, (1130, 730, 1725, 930), "정보 누락 가능성", "기업, 직무, 역량, 개인 경험 사이의 연결이 약함", GREEN)
    return img


def slide3():
    img, draw = slide_base(3, "해결 방식 - 한 번 입력하면 준비 기준까지 생성", "입력 흐름 · 자동 분석 · 결과 카드")
    draw_wrapped(draw, (145, 178), "기업, 공고, 자기소개서, 면접 유형을 넣으면\n개인화된 학습 방향과 예상 질문까지 한 번에 구성합니다.", 930, F["h2"], fill=INK, gap=15)
    xs = [170, 500, 830, 1160, 1490]
    steps = [("사용자 입력", "기업/공고/자소서\n프로필/면접유형", BLUE), ("Django API", "인증/저장\n분석 요청", PRIMARY), ("GraphRAG", "근거 검색\n관계 구성", GREEN), ("LLM 분석", "gpt-5-nano\n한국어 JSON", PRIMARY_2), ("결과 출력", "로드맵\n질문/근거", INK)]
    for i, (t, b, c) in enumerate(steps):
        x = xs[i]
        rr(draw, (x, 410, x + 260, 590), fill=WHITE, outline=c, width=3, radius=30)
        draw.text((x + 34, 442), t, font=F["h3"], fill=c)
        draw_wrapped(draw, (x + 34, 493), b, 190, F["small"], fill=INK, gap=4)
        if i < len(steps) - 1:
            arrow(draw, (x + 270, 500), (x + 322, 500), fill=PRIMARY, width=5)

    outputs = [
        ("역량 gap", "공고 요구와 내 경험의 차이"),
        ("준비 항목", "개념/프로젝트/답변 우선순위"),
        ("예상 질문", "학습 깊이를 정하는 기준"),
        ("답변 방향", "내 경험을 근거로 답변 구조화"),
        ("근거/꼬리질문", "놓친 연결을 재확인"),
    ]
    for i, (t, b) in enumerate(outputs):
        x = 170 + i * 342
        rr(draw, (x, 735, x + 290, 910), fill=(255, 255, 255, 238), outline=LINE, radius=22)
        draw.text((x + 28, 770), t, font=F["h3"], fill=PRIMARY)
        draw_wrapped(draw, (x + 28, 824), b, 230, F["small"], fill=INK, gap=5)
    return img


def slide4():
    img, draw = slide_base(4, "결과 차별점 - 예상 질문이 학습 깊이의 기준", "경쟁 서비스 비교 · 질문 기반 학습 깊이")
    draw_wrapped(draw, (145, 180), "단순히 '무엇을 공부하라'가 아니라\n'이 질문에 답할 수 있을 정도로'\n준비 기준을 제시합니다.", 1000, F["h2"], fill=INK, gap=15)
    rr(draw, (120, 345, 1800, 785), fill=(255, 255, 255, 240), outline=LINE, radius=28)
    headers = ["서비스 예시", "강점", "PathFiner AI가 보완한 지점"]
    cols = [160, 520, 980]
    for x, h in zip(cols, headers):
        draw.text((x, 385), h, font=F["h3"], fill=PRIMARY)
    rows = [
        ("원티드 AI 면접코칭", "공고 링크 기반 예상 질문,\n답변 피드백", "질문을 학습 로드맵의\n깊이 기준으로 연결"),
        ("사람인 AI 모의면접", "이력서 기반 맞춤 질문,\n꼬리질문/피드백", "면접 연습 전 단계의\n공고-경험 gap 정리"),
        ("하이잡", "공고/직무/경험 기반\n자소서와 면접 지원", "GraphRAG로 기업/직무/경험\n근거 관계를 명시"),
    ]
    y = 455
    for name, strength, diff in rows:
        draw.line((145, y - 24, 1770, y - 24), fill=LINE, width=2)
        draw.text((160, y), name, font=F["body_b"], fill=INK)
        draw_wrapped(draw, (520, y), strength, 360, F["small"], fill=MUTE, gap=4)
        draw_wrapped(draw, (980, y), diff, 650, F["small_b"], fill=PRIMARY, gap=4)
        y += 105
    draw.line((145, y - 24, 1770, y - 24), fill=LINE, width=2)

    rr(draw, (270, 845, 1650, 930), fill=PRIMARY, radius=42)
    draw.text((345, 865), "학습 깊이 기준 =", font=F["h2"], fill=WHITE)
    draw.text((690, 865), "예상 질문에 내 경험으로 답할 수 있는가", font=F["h2"], fill="#f9f0ff")
    draw.text((1340, 796), "출처: 각 서비스 소개 페이지 요약", font=F["small"], fill=MUTE)
    return img


def slide5():
    img, draw = slide_base(5, "왜 GraphRAG인가?", "정보 연결 · 누락 감소 · gpt-5-nano 보완")
    draw_wrapped(draw, (145, 176), "정확한 개인화 추천은 많은 정보를 길게 넣는 것보다\n관계를 놓치지 않고 연결하는 것이 중요합니다.", 920, F["h2"], fill=INK, gap=15)
    graph = {
        "기업": (415, 405, BLUE),
        "직무": (710, 350, PRIMARY),
        "공고": (1000, 430, GREEN),
        "요구역량": (810, 620, PRIMARY_2),
        "개인경험": (520, 720, "#8a6116"),
        "예상질문": (1080, 745, INK),
    }
    edges = [("기업", "직무"), ("직무", "공고"), ("공고", "요구역량"), ("요구역량", "개인경험"), ("요구역량", "예상질문"), ("개인경험", "예상질문"), ("기업", "공고")]
    for a, b in edges:
        x1, y1, _ = graph[a]
        x2, y2, _ = graph[b]
        draw.line((x1, y1, x2, y2), fill=(74, 21, 75, 120), width=5)
    for label, (x, y, c) in graph.items():
        rr(draw, (x - 100, y - 45, x + 100, y + 45), fill=WHITE, outline=c, width=4, radius=45)
        tw = draw.textbbox((0, 0), label, font=F["h3"])[2]
        draw.text((x - tw / 2, y - 20), label, font=F["h3"], fill=c)

    card(draw, (1280, 280, 1740, 455), "단순 SQL DB", "행/열 조회는 빠르지만 관계 맥락을 LLM이 다시 추론해야 함", BLUE)
    card(draw, (1280, 505, 1740, 680), "긴 프롬프트", "정보를 많이 넣어도 중요한 연결이 희석될 수 있음", PRIMARY_2)
    card(draw, (1280, 730, 1740, 905), "GraphRAG", "기업-직무-공고-경험 관계를 근거 단위로 묶어 전달", GREEN)
    rr(draw, (160, 890, 1110, 950), fill=(255, 255, 255, 230), outline=LINE, radius=28)
    draw.text((200, 905), "gpt-5-nano의 한계 + 기존 SQL DB의 맥락 한계 -> GraphRAG로 근거 연결 보완", font=F["small_b"], fill=PRIMARY)
    return img


def slide6():
    img, draw = slide_base(6, "기대 효과", "반복 자동화 · 준비 기준 · 근거 기반 마무리")
    draw_wrapped(draw, (145, 176), "PathFiner AI가 만드는 변화는 '답변 하나'가 아니라\n면접 준비 분석 흐름의 자동화입니다.", 900, F["h2"], fill=INK, gap=15)
    cards = [
        ("반복 분석 감소", "공고 분석, 자소서 비교, 예상 질문 생성을 한 흐름으로 묶음", BLUE),
        ("준비 기준 명확화", "공부 키워드가 아니라 답해야 할 질문 수준으로 목표를 설정", PRIMARY),
        ("근거 누락 감소", "GraphRAG가 기업/직무/공고/경험 관계를 구조적으로 연결", GREEN),
    ]
    for i, (t, b, c) in enumerate(cards):
        x = 150 + i * 575
        rr(draw, (x, 360, x + 500, 620), fill=(255, 255, 255, 242), outline=LINE, radius=32)
        draw.text((x + 36, 400), f"0{i+1}", font=F["h2"], fill=c)
        draw.text((x + 36, 470), t, font=F["h3"], fill=PRIMARY)
        draw_wrapped(draw, (x + 36, 525), b, 410, F["small"], fill=INK, gap=5)

    rr(draw, (150, 720, 1770, 900), fill=PRIMARY, radius=36)
    closing = "PathFiner AI는 단순한 AI 답변 생성 서비스가 아니라, 사용자가 반복해서 수행하던 면접 준비 분석 과정을 자동화하고, 더 많은 근거를 빠짐없이 연결해 개인화된 학습 방향을 추천하는 서비스입니다."
    draw_wrapped(draw, (220, 770), closing, 1480, F["h3"], fill=WHITE, gap=14)
    return img


def main():
    slides = [slide1(), slide2(), slide3(), slide4(), slide5(), slide6()]
    for i, img in enumerate(slides, 1):
        img.convert("RGB").save(ROOT / f"{i:02d}.png", quality=95)
    print("generated", len(slides), "slides in", ROOT)


if __name__ == "__main__":
    main()
