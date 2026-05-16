import io
import re
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors


def _clean_markdown(text: str) -> str:
    """Strip markdown symbols for plain text output."""
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`{3}.*?\n(.*?)`{3}", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"`(.*?)`", r"\1", text)
    return text.strip()


def generate_txt(user_input: str, app_type: str, response: str) -> bytes:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = (
        f"AI Software Architect — Generated Blueprint\n"
        f"{'=' * 50}\n"
        f"Date       : {timestamp}\n"
        f"App Type   : {app_type}\n"
        f"Idea       : {user_input[:200]}{'...' if len(user_input) > 200 else ''}\n"
        f"{'=' * 50}\n\n"
    )
    body = _clean_markdown(response)
    return (header + body).encode("utf-8")


def generate_pdf(user_input: str, app_type: str, response: str) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        "BPTitle",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=4,
    )
    style_meta = ParagraphStyle(
        "BPMeta",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#666666"),
        spaceAfter=2,
    )
    style_h2 = ParagraphStyle(
        "BPH2",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=14,
        spaceAfter=4,
        borderPad=0,
    )
    style_code = ParagraphStyle(
        "BPCode",
        parent=styles["Code"],
        fontSize=8,
        leading=12,
        backColor=colors.HexColor("#f4f4f4"),
        leftIndent=8,
        rightIndent=8,
        spaceBefore=4,
        spaceAfter=4,
        fontName="Courier",
    )
    style_body = ParagraphStyle(
        "BPBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        spaceAfter=4,
    )
    style_bullet = ParagraphStyle(
        "BPBullet",
        parent=style_body,
        leftIndent=14,
        bulletIndent=4,
        spaceAfter=2,
    )

    story = []

    # Header
    timestamp = datetime.now().strftime("%B %d, %Y – %H:%M")
    story.append(Paragraph("AI Software Architect", style_title))
    story.append(Paragraph(f"Generated: {timestamp}", style_meta))
    story.append(Paragraph(f"Type: {app_type}", style_meta))
    story.append(Spacer(1, 4))
    story.append(
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc"))
    )
    story.append(Spacer(1, 6))

    idea_preview = user_input[:300] + ("..." if len(user_input) > 300 else "")
    story.append(Paragraph(f"<b>Idea:</b> {idea_preview}", style_body))
    story.append(Spacer(1, 10))

    # Parse and render markdown sections
    in_code_block = False
    code_lines = []

    def flush_code():
        if code_lines:
            code_text = "<br/>".join(
                ln.replace(" ", "&nbsp;").replace("<", "&lt;").replace(">", "&gt;")
                for ln in code_lines
            )
            story.append(Paragraph(code_text, style_code))
            code_lines.clear()

    for line in response.split("\n"):
        if line.startswith("```"):
            if in_code_block:
                flush_code()
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if line.startswith("## "):
            section = line[3:].strip()
            story.append(Paragraph(section, style_h2))
            story.append(
                HRFlowable(
                    width="100%", thickness=0.5, color=colors.HexColor("#dddddd")
                )
            )

        elif line.startswith("### "):
            story.append(Paragraph(line[4:].strip(), styles["Heading3"]))

        elif re.match(r"^[-*]\s+", line):
            content = re.sub(r"^[-*]\s+", "", line)
            content = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", content)
            story.append(Paragraph(f"• {content}", style_bullet))

        elif re.match(r"^\d+\.\s+", line):
            content = re.sub(r"^\d+\.\s+", "", line)
            content = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", content)
            story.append(Paragraph(f"• {content}", style_bullet))

        elif line.strip():
            line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
            line = re.sub(r"`(.*?)`", r"<font name='Courier'>\1</font>", line)
            story.append(Paragraph(line, style_body))

        else:
            story.append(Spacer(1, 5))

    flush_code()

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
