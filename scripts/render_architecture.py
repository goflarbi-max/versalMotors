"""Render the documented VersalMotors architecture as a portable PNG."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "screenshots" / "architecture.png"


def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = ["arialbd.ttf", "Arial Bold.ttf"] if bold else ["arial.ttf", "Arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _centered_text(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str) -> None:
    font = _font(23, bold=True)
    lines = text.split("\n")
    spacing = 5
    heights = [draw.textbbox((0, 0), line, font=font)[3] for line in lines]
    total = sum(heights) + spacing * (len(lines) - 1)
    y = box[1] + (box[3] - box[1] - total) / 2
    for line, height in zip(lines, heights):
        bounds = draw.textbbox((0, 0), line, font=font)
        width = bounds[2] - bounds[0]
        draw.text((box[0] + (box[2] - box[0] - width) / 2, y), line, fill="#10243E", font=font)
        y += height + spacing


def render() -> Path:
    width, height = 2400, 690
    image = Image.new("RGB", (width, height), "#F7FAFC")
    draw = ImageDraw.Draw(image)
    draw.text((70, 38), "VersalMotors business intelligence architecture", fill="#10243E", font=_font(38, bold=True))

    labels = [
        "Raw CSV\ndata",
        "Audited\ncleaning",
        "DuckDB",
        "Analytics &\ninsight engine",
        "Evidence\nobjects",
        "AI tools &\nguardrails",
        "Streamlit\npages",
        "Management",
    ]
    colors = ["#DCEBFA", "#D9F1E3", "#FFF1CC", "#E7E1FA", "#D9EFF2", "#FBE1E7", "#DCEBFA", "#D9F1E3"]
    left, top, box_w, box_h, gap = 65, 230, 245, 155, 47
    boxes = []
    for index, (label, color) in enumerate(zip(labels, colors)):
        x1 = left + index * (box_w + gap)
        box = (x1, top, x1 + box_w, top + box_h)
        boxes.append(box)
        draw.rounded_rectangle(box, radius=20, fill=color, outline="#315B7D", width=3)
        _centered_text(draw, box, label)
        if index:
            previous = boxes[index - 1]
            y = top + box_h // 2
            draw.line((previous[2] + 7, y, box[0] - 13, y), fill="#315B7D", width=5)
            draw.polygon([(box[0] - 13, y - 10), (box[0] - 13, y + 10), (box[0], y)], fill="#315B7D")

    caption = "Quality flags and deterministic fallback remain visible to the dashboard; Gemini is optional."
    draw.text((70, 510), caption, fill="#315B7D", font=_font(27))
    draw.rounded_rectangle((70, 570, 2330, 635), radius=15, fill="#FFFFFF", outline="#9DB4C8", width=2)
    draw.text((100, 587), "Raw data → governed processing → traceable evidence → management decision support", fill="#10243E", font=_font(25, bold=True))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, format="PNG", optimize=True)
    return OUTPUT


if __name__ == "__main__":
    print(render())
