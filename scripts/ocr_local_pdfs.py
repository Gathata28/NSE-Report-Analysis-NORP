"""Extract text from local NORP PDFs with a text-layer-first strategy.

The extractor walks a directory recursively, runs ``pdftotext`` first, and
uses ``pdftoppm`` plus Tesseract only when direct extraction produces too little
usable text. It writes one UTF-8 sidecar per PDF and a JSONL manifest suitable
for bundle-level progress reporting. It never promotes extracted numbers to
verified facts; database fact review remains a separate workflow.

Examples::

    python scripts/ocr_local_pdfs.py --input-dir data/retrieved
    python scripts/ocr_local_pdfs.py --input-dir downloads/banking \
        --manifest downloads/banking/extraction_manifest.jsonl
"""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

LOGGER = logging.getLogger("norp_extract")


@dataclass
class ExtractionResult:
    """Manifest row describing one PDF extraction attempt."""

    pdf_path: str
    text_path: str
    extraction_method: str
    extraction_status: str
    page_count: int | None
    character_count: int
    error: str | None = None


def require_binary(name: str) -> str:
    """Return an executable path or raise an actionable dependency error."""
    path = shutil.which(name)
    if path is None:
        raise RuntimeError(
            f"Missing required system dependency: {name}. Install Poppler utilities "
            "(pdftotext/pdftoppm) and/or tesseract-ocr, then retry."
        )
    return path


def direct_text(pdf: Path, pdftotext: str) -> str:
    """Extract the PDF text layer, returning stdout as UTF-8 text."""
    completed = subprocess.run(
        [pdftotext, "-layout", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
        errors="replace",
    )
    return completed.stdout.replace("\x00", "").strip()


def has_usable_text(text: str, minimum_chars: int) -> bool:
    """Detect whether direct extraction is substantial enough to avoid OCR."""
    normalized = " ".join(text.split())
    if len(normalized) < minimum_chars:
        return False
    alpha = sum(char.isalpha() for char in normalized)
    return alpha >= max(20, len(normalized) // 20)


def ocr_text(pdf: Path, pdftoppm: str, tesseract: str, keep_pages: bool = False) -> tuple[str, int]:
    """Render pages and OCR them with Tesseract, returning text and page count."""
    if keep_pages:
        work_dir = pdf.parent / f"{pdf.stem}_ocr"
        work_dir.mkdir(exist_ok=True)
        cleanup = False
    else:
        temporary = tempfile.TemporaryDirectory(prefix="norp-ocr-")
        work_dir = Path(temporary.name)
        cleanup = True
    try:
        prefix = work_dir / "page"
        subprocess.run(
            [pdftoppm, "-jpeg", "-r", "150", str(pdf), str(prefix)],
            check=True,
            capture_output=True,
            text=True,
            errors="replace",
        )
        pages: list[str] = []
        for image in sorted(work_dir.glob("page-*.jpg")):
            output_prefix = image.with_suffix("")
            subprocess.run(
                [tesseract, str(image), str(output_prefix), "-l", "eng"],
                check=True,
                capture_output=True,
                text=True,
                errors="replace",
            )
            text_file = output_prefix.with_suffix(".txt")
            pages.append(text_file.read_text(encoding="utf-8", errors="replace") if text_file.exists() else "")
        return "\f".join(pages).strip(), len(pages)
    finally:
        if cleanup:
            temporary.cleanup()


def extract_one(pdf: Path, *, minimum_chars: int = 80, keep_pages: bool = False) -> ExtractionResult:
    """Extract one PDF and write its sidecar next to the source PDF."""
    text_path = pdf.with_suffix(".txt")
    try:
        pdftotext = require_binary("pdftotext")
        direct = direct_text(pdf, pdftotext)
        if has_usable_text(direct, minimum_chars):
            text_path.write_text(direct + "\n", encoding="utf-8")
            return ExtractionResult(str(pdf), str(text_path), "pdftotext", "extracted", None, len(direct))
        pdftoppm = require_binary("pdftoppm")
        tesseract = require_binary("tesseract")
        ocr, pages = ocr_text(pdf, pdftoppm, tesseract, keep_pages=keep_pages)
        text_path.write_text(ocr + "\n", encoding="utf-8")
        return ExtractionResult(str(pdf), str(text_path), "tesseract-ocr", "extracted", pages, len(ocr))
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        LOGGER.error("failed %s: %s", pdf, exc)
        return ExtractionResult(str(pdf), str(text_path), "none", "failed", None, 0, str(exc))


def main() -> int:
    """Run recursive PDF extraction and emit a JSON summary."""
    parser = argparse.ArgumentParser(description="Extract NORP PDF text layers, using OCR only as a fallback.")
    parser.add_argument("--input-dir", type=Path, required=True, help="Directory searched recursively for PDFs.")
    parser.add_argument("--manifest", type=Path, help="JSONL output path; defaults to <input-dir>/extraction_manifest.jsonl.")
    parser.add_argument("--minimum-chars", type=int, default=80, help="Minimum usable direct-text length before OCR fallback.")
    parser.add_argument("--keep-pages", action="store_true", help="Keep rendered OCR page images and text files.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s %(message)s")
    if not args.input_dir.is_dir():
        parser.error(f"input directory does not exist: {args.input_dir}")
    if args.minimum_chars < 1:
        parser.error("--minimum-chars must be positive")
    results = [extract_one(pdf, minimum_chars=args.minimum_chars, keep_pages=args.keep_pages) for pdf in sorted(args.input_dir.rglob("*.pdf"))]
    manifest = args.manifest or args.input_dir / "extraction_manifest.jsonl"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("".join(json.dumps(asdict(result), ensure_ascii=False) + "\n" for result in results), encoding="utf-8")
    counts: dict[str, int] = {}
    for result in results:
        counts[result.extraction_method] = counts.get(result.extraction_method, 0) + 1
    print(json.dumps({"selected": len(results), "methods": counts, "manifest": str(manifest)}, indent=2))
    return 0 if all(result.extraction_status == "extracted" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
