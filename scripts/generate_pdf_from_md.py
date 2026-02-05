from __future__ import annotations

import re
from pathlib import Path


def _wrap_line(line: str, width: int) -> list[str]:
    if len(line) <= width:
        return [line]
    words = line.split()
    if not words:
        return [""]
    out: list[str] = []
    cur = words[0]
    for w in words[1:]:
        if len(cur) + 1 + len(w) <= width:
            cur += " " + w
        else:
            out.append(cur)
            cur = w
    out.append(cur)
    return out


def _escape_pdf_text(s: str) -> str:
    # Escape backslashes and parentheses for PDF string literals.
    return (
        s.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        # Avoid unicode bullets in the PDF content stream
        .replace("•", "*")
    )


def text_to_simple_pdf(text: str, out_path: Path) -> None:
    """
    Minimal PDF generator (no external deps).

    Renders the given text as a monospaced-style document using Helvetica.
    This is intentionally simple but produces a valid PDF.
    """
    # Normalize markdown-ish into readable plain text.
    # Replace common unicode punctuation with ASCII for PDF simplicity.
    text = (
        text.replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2011", "-")
        .replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2026", "...")
        .replace("\u2260", "!=")
        .replace("\u2264", "<=")
        .replace("\u2265", ">=")
        .replace("\u00a0", " ")
        .replace("\u2022", "*")
    )
    lines: list[str] = []
    for raw in text.splitlines():
        if raw.startswith("# "):
            lines.append(raw[2:].strip())
            lines.append("")
            continue
        if raw.startswith("## "):
            lines.append(raw[3:].strip())
            continue
        if raw.startswith("- "):
            lines.append("• " + raw[2:].strip())
            continue
        lines.append(raw.rstrip())

    # Collapse excessive empty lines (keep at most 2).
    cleaned: list[str] = []
    empty = 0
    for ln in lines:
        if ln.strip() == "":
            empty += 1
            if empty <= 2:
                cleaned.append("")
        else:
            empty = 0
            cleaned.append(ln)

    # Wrap and paginate.
    wrap_width = 95
    page_lines = 52
    wrapped: list[str] = []
    for ln in cleaned:
        # Preserve bullets / indentation a little.
        prefix = ""
        m = re.match(r"^(\s+)", ln)
        if m:
            prefix = m.group(1)
        chunks = _wrap_line(ln.strip("\n"), wrap_width)
        if prefix:
            chunks = [prefix + c for c in chunks]
        wrapped.extend(chunks if chunks else [""])

    pages: list[list[str]] = []
    for i in range(0, len(wrapped) or 1, page_lines):
        pages.append(wrapped[i : i + page_lines])
    if not pages:
        pages = [[""]]

    # PDF object builder.
    objects: list[bytes] = []

    def add_obj(data: str) -> int:
        objects.append(data.encode("latin-1"))
        return len(objects)

    # Catalog (1) + Pages (2) + Font (3)
    add_obj("<< /Type /Catalog /Pages 2 0 R >>")
    add_obj("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    # Reserve pages object as object #2 by inserting later
    # (we already added catalog and font, so insert pages next).
    # We must actually ensure object numbers: 1=catalog, 2=pages, 3=font.
    # Current objects: [catalog, font]. Insert pages at index 1.
    pages_obj_placeholder = b"<< /Type /Pages /Kids [] /Count 0 >>"
    objects.insert(1, pages_obj_placeholder)

    # Track page and content objects ids.
    page_obj_ids: list[int] = []
    content_obj_ids: list[int] = []

    def add_stream(stream_text: str) -> int:
        data = stream_text.encode("latin-1")
        obj = f"<< /Length {len(data)} >>\nstream\n".encode("latin-1") + data + b"\nendstream"
        objects.append(obj)
        return len(objects)

    # Create pages.
    for page_lines_list in pages:
        # Build content stream: place each line.
        # Page size: letter-ish 612x792 points; margins 54; line height 13.
        x = 54
        y_start = 760
        line_h = 13
        parts: list[str] = []
        parts.append("BT")
        parts.append("/F1 11 Tf")
        parts.append(f"{x} {y_start} Td")
        for idx, ln in enumerate(page_lines_list):
            if idx > 0:
                parts.append(f"0 {-line_h} Td")
            parts.append(f"({_escape_pdf_text(ln)}) Tj")
        parts.append("ET")
        content_id = add_stream("\n".join(parts))
        content_obj_ids.append(content_id)

        # Page object references font and content.
        page_obj = (
            f"<< /Type /Page /Parent 2 0 R "
            f"/MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )
        objects.append(page_obj.encode("latin-1"))
        page_obj_ids.append(len(objects))

    # Now fill Pages object (#2).
    kids = " ".join([f"{pid} 0 R" for pid in page_obj_ids])
    pages_obj = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_obj_ids)} >>"
    objects[1] = pages_obj.encode("latin-1")

    # Write final PDF with xref.
    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets: list[int] = [0]
    body = bytearray()
    body.extend(header)

    for i, obj in enumerate(objects, start=1):
        offsets.append(len(body))
        body.extend(f"{i} 0 obj\n".encode("latin-1"))
        body.extend(obj)
        body.extend(b"\nendobj\n")

    xref_start = len(body)
    body.extend(f"xref\n0 {len(objects)+1}\n".encode("latin-1"))
    body.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        body.extend(f"{off:010d} 00000 n \n".encode("latin-1"))

    # Trailer
    body.extend(
        (
            f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF\n"
        ).encode("latin-1")
    )

    out_path.write_bytes(bytes(body))


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    md_path = repo / "feb5_sub_report.md"
    pdf_path = repo / "feb5_sub_report.pdf"
    text = md_path.read_text(encoding="utf-8")
    text_to_simple_pdf(text, pdf_path)
    print(f"Wrote {pdf_path}")


if __name__ == "__main__":
    main()

