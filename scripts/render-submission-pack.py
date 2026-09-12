from __future__ import annotations

import html
import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image
from weasyprint import HTML


PACK_TITLE = "TACATDP Integrated M&E System and Monitoring Tool"
PDF_NAME = "TACATDP-Integrated-ME-System-Submission-Pack.pdf"
HTML_NAME = "TACATDP-Integrated-ME-System-Submission-Pack.html"
DOCX_NAME = "TACATDP-Integrated-ME-System-Submission-Pack.docx"
DOCUMENTS = [
    "01-system-stages-report.md",
    "02-dashboard-interface-screenshot-note.md",
    "03-user-manual.md",
    "04-sop-draft.md",
    "05-annex-index.md",
]


def inline_markup(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def render_table(lines: list[str]) -> str:
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells):
            continue
        rows.append(cells)

    if not rows:
        return ""

    head, body = rows[0], rows[1:]
    out = ["<table><thead><tr>"]
    out.extend(f"<th>{inline_markup(cell)}</th>" for cell in head)
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>")
        out.extend(f"<td>{inline_markup(cell)}</td>" for cell in row)
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def markdown_to_html(markdown: str) -> str:
    out: list[str] = []
    paragraph: list[str] = []
    table: list[str] = []
    ul_open = False
    ol_open = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{inline_markup(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_table() -> None:
        nonlocal table
        if table:
            out.append(render_table(table))
            table = []

    def close_lists() -> None:
        nonlocal ul_open, ol_open
        if ul_open:
            out.append("</ul>")
            ul_open = False
        if ol_open:
            out.append("</ol>")
            ol_open = False

    for raw in markdown.splitlines():
        line = raw.rstrip()

        if line.startswith("|"):
            flush_paragraph()
            close_lists()
            table.append(line)
            continue

        flush_table()

        if not line.strip():
            flush_paragraph()
            close_lists()
            continue

        image_match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip())
        if image_match:
            flush_paragraph()
            close_lists()
            alt, src = image_match.groups()
            out.append(
                f'<figure><img src="{html.escape(src)}" alt="{html.escape(alt)}">'
                f"<figcaption>{html.escape(alt)}</figcaption></figure>"
            )
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading_match:
            flush_paragraph()
            close_lists()
            level = min(len(heading_match.group(1)), 4)
            out.append(f"<h{level}>{inline_markup(heading_match.group(2))}</h{level}>")
            continue

        bullet_match = re.match(r"^\s*-\s+(.*)$", line)
        if bullet_match:
            flush_paragraph()
            if not ul_open:
                close_lists()
                out.append("<ul>")
                ul_open = True
            out.append(f"<li>{inline_markup(bullet_match.group(1))}</li>")
            continue

        number_match = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if number_match:
            flush_paragraph()
            if not ol_open:
                close_lists()
                out.append("<ol>")
                ol_open = True
            out.append(f"<li>{inline_markup(number_match.group(1))}</li>")
            continue

        paragraph.append(line.strip())

    flush_table()
    flush_paragraph()
    close_lists()
    return "\n".join(out)


def markdown_to_blocks(markdown: str) -> list[tuple[str, object]]:
    blocks: list[tuple[str, object]] = []
    paragraph: list[str] = []
    table: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(("p", " ".join(paragraph)))
            paragraph = []

    def flush_table() -> None:
        nonlocal table
        if table:
            rows = []
            for row in table:
                cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
                if all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells):
                    continue
                rows.append(cells)
            if rows:
                blocks.append(("table", rows))
            table = []

    for raw in markdown.splitlines():
        line = raw.rstrip()

        if line.startswith("|"):
            flush_paragraph()
            table.append(line)
            continue

        flush_table()

        if not line.strip():
            flush_paragraph()
            continue

        image_match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip())
        if image_match:
            flush_paragraph()
            alt, src = image_match.groups()
            blocks.append(("image", (alt, src)))
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading_match:
            flush_paragraph()
            blocks.append(("h", (min(len(heading_match.group(1)), 3), heading_match.group(2))))
            continue

        bullet_match = re.match(r"^\s*-\s+(.*)$", line)
        if bullet_match:
            flush_paragraph()
            blocks.append(("li", bullet_match.group(1)))
            continue

        number_match = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if number_match:
            flush_paragraph()
            blocks.append(("li", number_match.group(1)))
            continue

        quote_match = re.match(r"^\s*>\s+(.*)$", line)
        if quote_match:
            flush_paragraph()
            blocks.append(("quote", quote_match.group(1)))
            continue

        paragraph.append(line.strip())

    flush_table()
    flush_paragraph()
    return blocks


CSS = """
@page {
  size: A4;
  margin: 18mm 16mm 18mm 16mm;
  @bottom-left {
    content: "TACATDP Integrated M&E System";
    font-size: 8pt;
    color: #6B7280;
  }
  @bottom-right {
    content: "Page " counter(page) " of " counter(pages);
    font-size: 8pt;
    color: #6B7280;
  }
}
body {
  font-family: "Inter", "Roboto", "DejaVu Sans", Arial, sans-serif;
  color: #17211C;
  font-size: 10.2pt;
  line-height: 1.5;
}
.cover {
  min-height: 180mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-left: 8px solid #064E3B;
  padding-left: 18mm;
}
.cover h1 {
  font-size: 28pt;
  line-height: 1.15;
  margin: 0 0 8mm 0;
  color: #064E3B;
}
.cover p {
  font-size: 13pt;
  color: #64706A;
  margin: 0 0 3mm 0;
}
.document {
  break-before: page;
}
h1 {
  color: #064E3B;
  font-size: 22pt;
  line-height: 1.2;
  margin: 0 0 8mm 0;
  border-bottom: 1px solid #E3E8E5;
  padding-bottom: 4mm;
}
h2 {
  color: #064E3B;
  font-size: 14pt;
  margin: 8mm 0 3mm 0;
}
h3 {
  color: #15803D;
  font-size: 11.5pt;
  margin: 6mm 0 2mm 0;
}
p {
  margin: 0 0 3.5mm 0;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin: 4mm 0 6mm 0;
  font-size: 8.8pt;
}
th {
  background: #EAF7EE;
  color: #064E3B;
  text-align: left;
  font-weight: 700;
}
th, td {
  border: 1px solid #E3E8E5;
  padding: 2.2mm 2.5mm;
  vertical-align: top;
}
tr {
  break-inside: avoid;
}
ul, ol {
  margin: 0 0 4mm 6mm;
  padding: 0;
}
li {
  margin-bottom: 1.5mm;
}
code {
  font-family: "DejaVu Sans Mono", monospace;
  font-size: 8.5pt;
  background: #F5F7F6;
  padding: 0.4mm 1mm;
  border-radius: 2mm;
}
figure {
  margin: 5mm 0 8mm 0;
  break-inside: avoid;
}
img {
  width: 100%;
  max-height: 170mm;
  object-fit: contain;
  border: 1px solid #E3E8E5;
  border-radius: 3mm;
}
figcaption {
  margin-top: 2mm;
  color: #64706A;
  font-size: 8.5pt;
}
"""


def build_html(base: Path) -> str:
    body = [
        "<!doctype html><html><head><meta charset='utf-8'>",
        f"<title>{html.escape(PACK_TITLE)}</title>",
        f"<style>{CSS}</style></head><body>",
        "<section class='cover'>",
        f"<h1>{html.escape(PACK_TITLE)}</h1>",
        "<p>Prototype status, dashboard evidence, user manual, SOP draft, and annex index</p>",
        "<p>27 August 2026</p>",
        "</section>",
    ]

    for document in DOCUMENTS:
        body.append("<section class='document'>")
        body.append(markdown_to_html((base / document).read_text(encoding="utf-8")))
        body.append("</section>")

    body.append("</body></html>")
    return "\n".join(body)


def clean_text(text: str) -> str:
    return re.sub(r"`([^`]+)`", r"\1", re.sub(r"\*\*([^*]+)\*\*", r"\1", text))


def w_text(text: str) -> str:
    return escape(clean_text(text))


def w_paragraph(text: str = "", style: str | None = None, italic: bool = False) -> str:
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    run_props = "<w:rPr><w:i/></w:rPr>" if italic else ""
    return f"<w:p>{style_xml}<w:r>{run_props}<w:t xml:space=\"preserve\">{w_text(text)}</w:t></w:r></w:p>"


def w_page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def w_table(rows: list[list[str]]) -> str:
    output = [
        "<w:tbl>",
        "<w:tblPr>",
        '<w:tblStyle w:val="TableGrid"/>',
        '<w:tblW w:w="0" w:type="auto"/>',
        "</w:tblPr>",
    ]
    for row_index, row in enumerate(rows):
        output.append("<w:tr>")
        for cell in row:
            shade = '<w:shd w:fill="EAF7EE"/>' if row_index == 0 else ""
            bold_start = "<w:b/>" if row_index == 0 else ""
            output.append(
                "<w:tc>"
                f'<w:tcPr><w:tcW w:w="2400" w:type="dxa"/>{shade}</w:tcPr>'
                f'<w:p><w:r><w:rPr>{bold_start}</w:rPr><w:t>{w_text(cell)}</w:t></w:r></w:p>'
                "</w:tc>"
            )
        output.append("</w:tr>")
    output.append("</w:tbl>")
    return "".join(output)


def image_extent(path: Path, max_width_inches: float = 6.3, max_height_inches: float = 4.2) -> tuple[int, int]:
    with Image.open(path) as img:
        width, height = img.size
    ratio = min(max_width_inches / width, max_height_inches / height)
    emu_per_px = 914400
    return int(width * ratio * emu_per_px), int(height * ratio * emu_per_px)


def w_image(relationship_id: str, image_name: str, cx: int, cy: int) -> str:
    alt = escape(image_name)
    return f"""
<w:p>
  <w:r>
    <w:drawing>
      <wp:inline distT="0" distB="0" distL="0" distR="0">
        <wp:extent cx="{cx}" cy="{cy}"/>
        <wp:effectExtent l="0" t="0" r="0" b="0"/>
        <wp:docPr id="{relationship_id.removeprefix('rId')}" name="{alt}"/>
        <wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>
        <a:graphic>
          <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
            <pic:pic>
              <pic:nvPicPr>
                <pic:cNvPr id="0" name="{alt}"/>
                <pic:cNvPicPr/>
              </pic:nvPicPr>
              <pic:blipFill>
                <a:blip r:embed="{relationship_id}"/>
                <a:stretch><a:fillRect/></a:stretch>
              </pic:blipFill>
              <pic:spPr>
                <a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
                <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
              </pic:spPr>
            </pic:pic>
          </a:graphicData>
        </a:graphic>
      </wp:inline>
    </w:drawing>
  </w:r>
</w:p>
"""


def render_docx(base: Path) -> Path:
    output = base / DOCX_NAME
    media: list[tuple[str, Path]] = []
    body: list[str] = [
        w_paragraph(PACK_TITLE, "Title"),
        w_paragraph("Prototype status, dashboard evidence, user manual, SOP draft, and annex index", "Subtitle"),
        w_paragraph("27 August 2026"),
    ]

    for document_index, document in enumerate(DOCUMENTS, start=1):
        body.append(w_page_break())
        for kind, value in markdown_to_blocks((base / document).read_text(encoding="utf-8")):
            if kind == "h":
                level, text = value  # type: ignore[misc]
                body.append(w_paragraph(str(text), f"Heading{level}"))
            elif kind == "p":
                body.append(w_paragraph(str(value)))
            elif kind == "quote":
                body.append(w_paragraph(str(value), italic=True))
            elif kind == "li":
                body.append(w_paragraph(f"• {value}"))
            elif kind == "table":
                body.append(w_table(value))  # type: ignore[arg-type]
            elif kind == "image":
                alt, src = value  # type: ignore[misc]
                image_path = base / str(src)
                relationship_id = f"rId{10 + len(media)}"
                media_name = f"image{len(media) + 1}{image_path.suffix.lower()}"
                cx, cy = image_extent(image_path)
                media.append((media_name, image_path))
                body.append(w_image(relationship_id, str(alt), cx, cy))
                body.append(w_paragraph(str(alt), italic=True))

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document
  xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
  xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
  xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
  xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
  <w:body>
    {''.join(body)}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1021" w:right="907" w:bottom="1021" w:left="907" w:header="708" w:footer="708" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>
"""
    relationships = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]
    for index, (media_name, _) in enumerate(media, start=10):
        relationships.append(
            f'<Relationship Id="rId{index}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
            f'Target="media/{media_name}"/>'
        )
    relationships.append("</Relationships>")

    content_types = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Default Extension="jpg" ContentType="image/jpeg"/>',
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>',
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>',
        "</Types>",
    ]
    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:sz w:val="21"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:color w:val="064E3B"/><w:sz w:val="44"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:rPr><w:color w:val="64706A"/><w:sz w:val="26"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:rPr><w:b/><w:color w:val="064E3B"/><w:sz w:val="34"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:rPr><w:b/><w:color w:val="064E3B"/><w:sz w:val="28"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:rPr><w:b/><w:color w:val="15803D"/><w:sz w:val="24"/></w:rPr></w:style>
  <w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:color="E3E8E5"/><w:left w:val="single" w:sz="4" w:color="E3E8E5"/><w:bottom w:val="single" w:sz="4" w:color="E3E8E5"/><w:right w:val="single" w:sz="4" w:color="E3E8E5"/><w:insideH w:val="single" w:sz="4" w:color="E3E8E5"/><w:insideV w:val="single" w:sz="4" w:color="E3E8E5"/></w:tblBorders></w:tblPr></w:style>
</w:styles>
"""

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", "\n".join(content_types))
        docx.writestr(
            "_rels/.rels",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
""",
        )
        docx.writestr("word/document.xml", document_xml)
        docx.writestr("word/styles.xml", styles_xml)
        docx.writestr("word/_rels/document.xml.rels", "\n".join(relationships))
        for media_name, image_path in media:
            docx.write(image_path, f"word/media/{media_name}")

    return output


def render_pack(base: Path) -> Path:
    output = base / PDF_NAME
    html_output = base / HTML_NAME
    html_document = build_html(base)
    html_output.write_text(html_document, encoding="utf-8")
    HTML(string=html_document, base_url=str(base)).write_pdf(output)
    render_docx(base)
    return output


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: render-submission-pack.py <submission-pack-dir>", file=sys.stderr)
        return 2

    output = render_pack(Path(sys.argv[1]).resolve())
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
