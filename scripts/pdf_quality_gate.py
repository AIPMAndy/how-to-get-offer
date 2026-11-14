#!/usr/bin/env python3
"""Independent PDF QA: structure, text, links, full-page raster contact sheets.

All pages are rendered and included in review sheets. This is an automated
preflight and visual-review artifact, NOT a claim of completed human visual QA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageOps


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", default="pdf/how-to-get-offer-guide.pdf")
    parser.add_argument("--edition", default="pdf/edition.json")
    parser.add_argument("--out", default="artifacts/pdf-qa")
    args = parser.parse_args()

    pdf = Path(args.pdf)
    edition = Path(args.edition)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    warnings: list[str] = []
    if not pdf.exists() or not edition.exists():
        raise SystemExit("PDF or edition.json missing")
    version = json.loads(edition.read_text(encoding="utf-8"))
    if version.get("chapters") != 44 or version.get("tasks") != 100:
        errors.append("Edition chapter/task counts are not the expected 44/100")
    if len(version.get("source_sha256", "")) != 64:
        errors.append("Edition source_sha256 is missing or malformed")

    doc = fitz.open(pdf)
    count = doc.page_count
    if doc.is_encrypted or count < 45:
        errors.append(f"Unexpected PDF encryption or page count: {count}")
    toc = doc.get_toc()
    if len(toc) < 40:
        errors.append(f"Too few navigable outline entries: {len(toc)}")
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    all_text: list[str] = []
    bounds_issues: list[dict] = []
    blanks: list[int] = []
    link_types: dict[str, int] = {}
    invalid_links: list[dict] = []
    all_thumbnails: list[Image.Image] = []

    for page_index, page in enumerate(doc):
        pnum = page_index + 1
        text = page.get_text("text", sort=True)
        all_text.append(text)
        if len(text.strip()) < 12:
            blanks.append(pnum)
        for block in page.get_text("blocks"):
            if len(block) < 7 or block[6] != 0:
                continue
            x0, y0, x1, y1 = block[:4]
            if min(x0, y0) < -5 or x1 > page.rect.width + 5 or y1 > page.rect.height + 5:
                bounds_issues.append({"page": pnum, "bbox": [round(v, 1) for v in (x0,y0,x1,y1)]})
        for link in page.get_links():
            kind = link.get("kind")
            key = str(kind)
            link_types[key] = link_types.get(key, 0) + 1
            if kind == fitz.LINK_URI:
                uri = str(link.get("uri", ""))
                if not uri.startswith(("https://", "http://", "mailto:")):
                    invalid_links.append({"page": pnum, "url": uri})
            if kind == fitz.LINK_GOTO:
                dest = link.get("page", -1)
                if not isinstance(dest, int) or not (0 <= dest < count):
                    invalid_links.append({"page": pnum, "destination": dest})
        # Rasterize EVERY page; archival PNG contact sheets are part of CI artifact.
        pix = page.get_pixmap(matrix=fitz.Matrix(0.55, 0.55), alpha=False)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        thumb = ImageOps.contain(im, (340, 478), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (356, 510), "#eef2f6")
        tile.paste(thumb, ((356 - thumb.width)//2, 9))
        ImageDraw.Draw(tile).text((12, 486), f"PAGE {pnum:03d}", fill="#2b3b50")
        all_thumbnails.append(tile)

    aggregate = "\n".join(all_text)
    for term in ("AIPMAndy", "metaver.vip", "a6no1.cn", "100 项任务"):
        if term not in aggregate:
            errors.append(f"Required visible text missing: {term}")
    if len(aggregate) < 20000:
        errors.append("Extractable text unexpectedly short")
    if invalid_links:
        errors.append(f"Invalid PDF hyperlinks: {invalid_links[:5]}")
    if bounds_issues:
        warnings.append(f"{len(bounds_issues)} potential text boundary issues: manual review required")
    if blanks:
        warnings.append(f"{len(blanks)} pages with <12 characters: inspect page numbers")

    sheets: list[str] = []
    for begin in range(0, count, 12):
        pages = all_thumbnails[begin:begin+12]
        canvas = Image.new("RGB", (356*3, 510*4), "white")
        for i, tile in enumerate(pages):
            canvas.paste(tile, ((i % 3)*356, (i // 3)*510))
        name = f"contact-sheet-{begin//12+1:02d}.png"
        canvas.save(out / name, optimize=True)
        sheets.append(name)

    report = {
        "pdf": str(pdf), "sha256": digest, "source_sha256": version.get("source_sha256"),
        "page_count": count, "outline_entries": len(toc),
        "rendered_pages": len(all_thumbnails), "contact_sheets": sheets,
        "characters_extracted": len(aggregate),
        "pdf_links_by_kind": link_types, "blank_or_sparse_pages": blanks,
        "text_outside_page": bounds_issues, "invalid_links": invalid_links,
        "errors": errors, "warnings": warnings,
        "status": "failed" if errors else "automated_preflight_passed_manual_visual_review_pending",
        "method": "PyMuPDF extraction and rasterization of every page; sheets require human inspection."
    }
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("sha256","page_count","outline_entries","rendered_pages","characters_extracted","errors","warnings","status")}, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
