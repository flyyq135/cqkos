#!/usr/bin/env python3
"""Generate three Chongqing real-estate talking-head cover templates."""

from __future__ import annotations

import argparse
import random
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


W, H = 1080, 1440
NAVY = (8, 35, 68)
NAVY2 = (11, 55, 94)
NAVY3 = (3, 22, 45)
GOLD = (229, 173, 86)
GOLD2 = (248, 206, 137)
ORANGE = (210, 91, 25)
CREAM = (248, 242, 230)
WHITE = (255, 255, 255)
GRAY = (94, 107, 123)
RISK_TERMS = [
    "必涨",
    "稳赚",
    "抄底",
    "闭眼买",
    "内部房源",
    "学区承诺",
    "制造焦虑",
    "零首付",
    "首付贷",
    "经营贷",
    "包成交",
    "捡漏",
    "大降价",
]


def find_font(light: bool = False) -> str:
    candidates = [
        "/System/Library/Fonts/STHeiti Light.ttc" if light else "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for item in candidates:
        if Path(item).exists():
            return item
    raise FileNotFoundError("No Chinese-capable font found. Install a CJK font or run on macOS.")


FONT = find_font(False)
FONT_LIGHT = find_font(True)


def f(size: int, light: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_LIGHT if light else FONT, size)


def parse_tags(raw: str, fallback: list[str]) -> list[str]:
    if not raw:
        return fallback[:3]
    tags = [t.strip() for t in re.split(r"[,，、|｜]", raw) if t.strip()]
    return (tags or fallback)[:3]


def sanitize_filename(text: str) -> str:
    text = re.sub(r"[\\/:*?\"<>|\s]+", "", text)
    return text[:40] or "封面"


def check_risk_text(*parts: str) -> None:
    text = "\n".join(parts)
    found = [term for term in RISK_TERMS if term in text]
    if found:
        raise ValueError(f"封面文字包含高风险表达：{', '.join(found)}")


def text_center(draw: ImageDraw.ImageDraw, box, text: str, font, fill) -> None:
    x, y, w, h = box
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x + (w - tw) / 2, y + (h - th) / 2 - 4), text, font=font, fill=fill)


def draw_fit_text(draw: ImageDraw.ImageDraw, xy, text: str, max_width: int, size: int, fill, min_size: int = 54) -> None:
    current = size
    font = f(current)
    while current > min_size:
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            break
        current -= 4
        font = f(current)
    draw.text(xy, text, font=font, fill=fill)


def draw_shadow_text(
    draw: ImageDraw.ImageDraw,
    xy,
    text: str,
    font,
    fill,
    stroke_fill=(0, 0, 0),
    stroke_width: int = 0,
    shadow=(0, 0, 0, 120),
    shadow_offset=(5, 8),
) -> None:
    x, y = xy
    if shadow:
        draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=shadow, stroke_width=stroke_width, stroke_fill=stroke_fill)
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


def draw_fit_shadow_text(draw: ImageDraw.ImageDraw, xy, text: str, max_width: int, size: int, fill, min_size: int = 54, stroke_width: int = 0) -> None:
    current = size
    font = f(current)
    while current > min_size:
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
        if bbox[2] - bbox[0] <= max_width:
            break
        current -= 4
        font = f(current)
    draw_shadow_text(draw, xy, text, font, fill, stroke_fill=NAVY3, stroke_width=stroke_width)


def shadow_round_rect(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1, shadow=True) -> None:
    x1, y1, x2, y2 = box
    if shadow:
        draw.rounded_rectangle((x1 + 10, y1 + 14, x2 + 10, y2 + 14), radius=radius, fill=(0, 0, 0, 80))
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_city_arc(draw: ImageDraw.ImageDraw, img: Image.Image, box=(0, 80, 455, 1050)) -> None:
    x1, y1, x2, y2 = box
    mask = Image.new("L", (W, H), 0)
    m = ImageDraw.Draw(mask)
    m.rounded_rectangle((x1 - 220, y1, x2 + 115, y2), radius=260, fill=255)
    m.rectangle((0, y1, x2 - 120, y2), fill=255)
    bg = Image.new("RGBA", (W, H), (226, 231, 231, 255))
    b = ImageDraw.Draw(bg)
    for i in range(24):
        bx = 20 + i * 24
        h = 90 + (i % 7) * 22
        b.rectangle((bx, 360 - h, bx + 20, 700), fill=(166, 178, 183, 155))
    b.rectangle((0, 510, x2, 720), fill=(205, 215, 211, 135))
    for i in range(28):
        bx = 12 + i * 20
        b.ellipse((bx, 660 + (i % 4) * 14, bx + 56, 720 + (i % 5) * 16), fill=(121, 145, 115, 155))
    b.line((0, 640, x2, 520), fill=(175, 186, 191, 180), width=8)
    img.paste(bg, (0, 0), mask)
    draw.arc((x1 - 220, y1, x2 + 115, y2), start=265, end=95, fill=GOLD2, width=7)


def draw_chart_background(draw: ImageDraw.ImageDraw) -> None:
    base_y = 1180
    for i in range(22):
        x = 565 + i * 26
        h = 35 + i * 8 + (i % 4) * 15
        draw.rectangle((x, base_y - h, x + 14, base_y), fill=(16, 79, 132, 120))
    pts = [(560, 1150), (625, 1115), (690, 1160), (755, 1110), (825, 1135), (900, 1085), (985, 1035), (1060, 930)]
    draw.line(pts, fill=GOLD2, width=3)
    for x, y in pts:
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=GOLD2)


def draw_grid(draw: ImageDraw.ImageDraw, color) -> None:
    for i in range(-200, W + 300, 90):
        draw.line([(i, 0), (i + 500, H)], fill=color, width=1)
    for j in range(80, H, 110):
        draw.line([(0, j), (W, j + random.randint(-20, 20))], fill=color, width=1)
    points = [(650, 220), (750, 300), (700, 420), (850, 560), (790, 700), (930, 830)]
    draw.line(points, fill=(58, 125, 174), width=5)
    for point in points[::2]:
        draw.ellipse((point[0] - 10, point[1] - 10, point[0] + 10, point[1] + 10), fill=GOLD)


def draw_map_header(draw: ImageDraw.ImageDraw, region: str) -> None:
    for i in range(475, 1050, 54):
        draw.line((i, 70, i + 260, 270), fill=(36, 77, 107, 95), width=2)
    for y in range(70, 295, 48):
        draw.line((480, y, 1040, y + 35), fill=(36, 77, 107, 85), width=2)
    draw.line((725, 90, 920, 120, 940, 250, 720, 280, 660, 170, 725, 90), fill=GOLD2, width=3)
    draw.ellipse((795, 128, 845, 178), fill=GOLD2)
    draw.ellipse((812, 142, 828, 158), fill=NAVY)
    draw.text((520, 130), f"{region}西站", font=f(23), fill=(226, 231, 238))
    draw.text((570, 205), f"{region}站", font=f(23), fill=(226, 231, 238))


def portrait_image(path: str | None, size: tuple[int, int]) -> Image.Image | None:
    if not path:
        return None
    img_path = Path(path).expanduser()
    if not img_path.exists():
        raise FileNotFoundError(f"人物照片不存在：{img_path}")
    img = Image.open(img_path).convert("RGBA")
    img = ImageOps.exif_transpose(img)
    img.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas.alpha_composite(img, ((size[0] - img.width) // 2, size[1] - img.height))
    return canvas


def draw_portrait(draw, x=75, y=560, scale=1.0, dark=(20, 38, 58), portrait: Image.Image | None = None, base: Image.Image | None = None):
    if portrait and base:
        base.alpha_composite(portrait, (int(x - 20 * scale), int(y - 275 * scale)))
        return
    draw.ellipse((x + 95 * scale, y - 260 * scale, x + 285 * scale, y - 70 * scale), fill=(29, 38, 49))
    draw.rounded_rectangle((x + 115 * scale, y - 75 * scale, x + 265 * scale, y + 10 * scale), radius=int(35 * scale), fill=(29, 38, 49))
    draw.polygon(
        [(x + 30 * scale, y + 15 * scale), (x + 185 * scale, y - 30 * scale), (x + 345 * scale, y + 15 * scale), (x + 405 * scale, y + 515 * scale), (x - 40 * scale, y + 515 * scale)],
        fill=dark,
    )
    draw.polygon([(x + 160 * scale, y), (x + 205 * scale, y + 220 * scale), (x + 245 * scale, y)], fill=WHITE)
    draw.polygon([(x + 193 * scale, y + 25 * scale), (x + 218 * scale, y + 25 * scale), (x + 228 * scale, y + 210 * scale), (x + 180 * scale, y + 210 * scale)], fill=GOLD)
    draw.line((x + 30 * scale, y + 105 * scale, x + 185 * scale, y + 10 * scale), fill=(43, 75, 107), width=max(1, int(5 * scale)))
    draw.line((x + 345 * scale, y + 105 * scale, x + 225 * scale, y + 10 * scale), fill=(43, 75, 107), width=max(1, int(5 * scale)))


def bottom_bar(draw, account_line: str, bg=(4, 28, 55)) -> None:
    draw.rectangle((0, H - 135, W, H), fill=bg)
    draw.text((72, H - 90), "◎", font=f(40), fill=GOLD)
    draw.text((128, H - 88), account_line, font=f(46), fill=WHITE)


def save_cover1(args, portrait, out_dir: Path) -> Path:
    img = Image.new("RGBA", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    for radius in range(980, 200, -80):
        draw.ellipse((-420, 150 - radius // 5, 560 + radius, 920 + radius // 4), outline=(16, 62, 99), width=2)
    draw_grid(draw, (28, 75, 113))
    draw_map_header(draw, args.region)
    draw_city_arc(draw, img, (0, 105, 470, 1115))
    draw_chart_background(draw)
    draw_portrait(draw, 48, 640, 1.35, portrait=portrait, base=img)
    shadow_round_rect(draw, (430, 315, 1048, 455), radius=26, fill=GOLD2, outline=(255, 224, 164), width=2)
    text_center(draw, (430, 315, 618, 140), args.region, f(92), NAVY)
    draw_fit_shadow_text(draw, (420, 470), args.data_title, 610, 128, WHITE, min_size=78, stroke_width=3)
    draw.polygon([(440, 650), (1035, 650), (1005, 735), (410, 735)], fill=GOLD2)
    text_center(draw, (440, 650, 565, 85), args.data_subtitle, f(60), NAVY)
    y = 765
    for index, tag in enumerate(parse_tags(args.data_tags, ["去化9个月", "参考价15993/㎡", "商业兑现85%+"])):
        shadow_round_rect(draw, (455, y, 1002, y + 118), radius=18, fill=(246, 247, 248), outline=(228, 231, 235), width=2)
        shadow_round_rect(draw, (478, y + 17, 600, y + 101), radius=16, fill=NAVY2, outline=(236, 218, 180), width=2, shadow=False)
        icon = "↗" if index == 0 else ("¥" if index == 1 else "▢")
        text_center(draw, (478, y + 17, 122, 84), icon, f(48), GOLD2)
        draw.text((635, y + 28), tag, font=f(48), fill=ORANGE if index != 0 else NAVY)
        y += 148
    bottom_bar(draw, args.account_line)
    out = out_dir / f"01-数据判断型-{sanitize_filename(args.region + args.data_title)}.png"
    img.convert("RGB").save(out)
    return out


def save_cover2(args, portrait, out_dir: Path) -> Path:
    img = Image.new("RGBA", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    for i in range(0, W, 80):
        draw.arc((i - 400, 60, i + 500, 900), start=15, end=195, fill=(231, 221, 205), width=2)
    shadow_round_rect(draw, (105, 70, 995, 205), radius=26, fill=ORANGE, outline=(225, 117, 54), width=2, shadow=False)
    text_center(draw, (105, 70, 890, 135), args.region, f(112), WHITE)
    draw_fit_shadow_text(draw, (95, 220), args.question_title, 900, 132, ORANGE, min_size=76, stroke_width=0)
    shadow_round_rect(draw, (315, 398, 1012, 492), radius=16, fill=NAVY, outline=NAVY, width=1)
    text_center(draw, (315, 398, 697, 94), args.question_subtitle, f(58), WHITE)
    draw.rounded_rectangle((255, 510, 570, 850), radius=160, fill=(232, 224, 207, 135))
    draw.text((325, 750), args.region, font=f(34), fill=NAVY)
    draw.ellipse((385, 786, 428, 829), fill=ORANGE)
    draw.ellipse((398, 799, 415, 816), fill=WHITE)
    draw_portrait(draw, 65, 800, 1.08, dark=(21, 45, 75), portrait=portrait, base=img)
    icons = ["⌂", "◎", "↗"]
    y = 560
    for index, tag in enumerate(parse_tags(args.question_tags, ["自住舒适线", "通勤半径线", "未来流通线"])):
        shadow_round_rect(draw, (500, y, 1018, y + 130), radius=20, fill=WHITE, outline=NAVY, width=3)
        draw.ellipse((532, y + 26, 606, y + 100), fill=NAVY)
        text_center(draw, (525, y + 28, 70, 70), icons[index % len(icons)], f(35), GOLD)
        draw.text((650, y + 35), tag, font=f(50), fill=NAVY)
        draw.rounded_rectangle((934, y + 38, 982, y + 86), radius=7, outline=ORANGE, width=4)
        draw.line((944, y + 62, 959, y + 78, 978, y + 42), fill=ORANGE, width=6)
        y += 150
    shadow_round_rect(draw, (285, 1120, 815, 1185), radius=22, fill=(247, 227, 195), outline=None, shadow=False)
    text_center(draw, (285, 1120, 530, 65), args.question_small_tag, f(40), NAVY)
    draw.line((410, 1055, 920, 1210), fill=(110, 134, 163), width=3)
    for x, label in [(450, "150万"), (610, "180万"), (760, "220万"), (900, "300万+")]:
        yy = 1130 + int((x - 450) * 0.25)
        draw.rectangle((x - 42, yy, x + 42, 1275), fill=(232, 214, 183, 165))
        draw.ellipse((x - 10, yy - 10, x + 10, yy + 10), fill=ORANGE if label == "220万" else WHITE, outline=NAVY, width=3)
        draw.text((x - 35, yy - 44), label, font=f(24), fill=ORANGE if label == "220万" else GRAY)
    bottom_bar(draw, args.account_line)
    out = out_dir / f"02-客户问题型-{sanitize_filename(args.region + args.question_title)}.png"
    img.convert("RGB").save(out)
    return out


def save_cover3(args, portrait, out_dir: Path) -> Path:
    img = Image.new("RGBA", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    draw_grid(draw, (25, 77, 116))
    shadow_round_rect(draw, (48, 40, 910, 220), radius=24, fill=GOLD2, outline=(255, 225, 160), width=3)
    text_center(draw, (48, 40, 862, 180), args.region, f(132), NAVY)
    draw_fit_shadow_text(draw, (75, 235), args.field_title, 930, 128, WHITE, min_size=74, stroke_width=2)
    text_center(draw, (245, 382, 590, 70), args.field_subtitle, f(56), GOLD2)
    x = 70
    for tag in parse_tags(args.field_tags, ["轨道路径", "商业半径", "挂牌结构"]):
        shadow_round_rect(draw, (x, 470, x + 285, 540), radius=18, fill=(20, 65, 101), outline=GOLD, width=2, shadow=False)
        text_center(draw, (x, 470, 285, 70), tag, f(38), WHITE)
        x += 315
    shadow_round_rect(draw, (55, 575, 585, 1120), radius=28, fill=(11, 54, 76), outline=GOLD, width=3)
    for radius in [120, 210, 310, 410]:
        draw.ellipse((120 - radius // 2, 710 - radius // 2, 120 + radius * 1.7, 710 + radius * 1.7), outline=(42, 111, 139), width=2)
    points = [(145, 960), (260, 840), (360, 885), (470, 740)]
    draw.line(points, fill=GOLD, width=8)
    for point in points:
        draw.ellipse((point[0] - 16, point[1] - 16, point[0] + 16, point[1] + 16), fill=WHITE)
    draw.text((250, 935), args.region, font=f(54), fill=GOLD)
    shadow_round_rect(draw, (610, 610, 1025, 1118), radius=20, fill=WHITE, outline=(220, 220, 220), width=2)
    text_center(draw, (650, 635, 335, 56), args.field_small_tag, f(34), NAVY)
    y = 725
    for tag in parse_tags(args.field_tags, ["轨道路径", "商业半径", "挂牌结构"]):
        draw.rounded_rectangle((650, y, 985, y + 95), radius=15, fill=(241, 244, 247))
        draw.text((700, y + 28), tag, font=f(42), fill=NAVY)
        draw.text((900, y + 24), "→", font=f(46), fill=GOLD)
        y += 125
    draw_portrait(draw, 840, 1050, 0.38, dark=(16, 38, 64), portrait=portrait, base=img)
    bottom_bar(draw, args.account_line)
    out = out_dir / f"03-实地验证型-{sanitize_filename(args.region + args.field_title)}.png"
    img.convert("RGB").save(out)
    return out


def save_contact_sheet(files: list[Path], out_dir: Path) -> Path:
    thumbs = []
    for path in files:
        img = Image.open(path).convert("RGB")
        img.thumbnail((300, 400), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (330, 455), WHITE)
        canvas.paste(img, ((330 - img.width) // 2, 10))
        ImageDraw.Draw(canvas).text((18, 420), path.stem, font=f(16), fill=(0, 0, 0))
        thumbs.append(canvas)
    sheet = Image.new("RGB", (330 * len(thumbs), 455), (240, 240, 240))
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, (index * 330, 0))
    out = out_dir / "封面模板三件套总览.png"
    sheet.save(out)
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成重庆房产口播封面三件套")
    parser.add_argument("--region", required=True, help="区域/板块名，如中央公园")
    parser.add_argument("--account-line", help="底部账号行；默认 {region}买房参谋｜XX")
    parser.add_argument("--output-dir", default="封面模板", help="输出目录")
    parser.add_argument("--portrait", help="人物照片路径，可选")
    parser.add_argument("--seed", type=int, default=8)
    parser.add_argument("--data-title", default="进入筛选期")
    parser.add_argument("--data-subtitle", default="现在怎么看")
    parser.add_argument("--data-tags", default="去化9个月,参考价15993/㎡,商业兑现85%+")
    parser.add_argument("--question-title", default="220万怎么选")
    parser.add_argument("--question-subtitle", default="先定路径，再看房")
    parser.add_argument("--question-tags", default="自住舒适线,通勤半径线,未来流通线")
    parser.add_argument("--question-small-tag", default="预算｜产品｜片区")
    parser.add_argument("--field-title", default="核心区怎么分")
    parser.add_argument("--field-subtitle", default="别只看板块名")
    parser.add_argument("--field-tags", default="轨道路径,商业半径,挂牌结构")
    parser.add_argument("--field-small-tag", default="实地验证｜板块对比")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    args.account_line = args.account_line or f"{args.region}买房参谋｜XX"
    check_risk_text(
        args.region,
        args.account_line,
        args.data_title,
        args.data_subtitle,
        args.data_tags,
        args.question_title,
        args.question_subtitle,
        args.question_tags,
        args.field_title,
        args.field_subtitle,
        args.field_tags,
    )
    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    portrait = portrait_image(args.portrait, (420, 790)) if args.portrait else None
    files = [
        save_cover1(args, portrait, out_dir),
        save_cover2(args, portrait, out_dir),
        save_cover3(args, portrait, out_dir),
    ]
    files.append(save_contact_sheet(files, out_dir))
    for file in files:
        print(file)


if __name__ == "__main__":
    main()
