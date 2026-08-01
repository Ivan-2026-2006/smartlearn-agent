import argparse
import os
import re
import sys
import fitz  # pymupdf
from dotenv import load_dotenv
import openai

# Ensure stdout can handle emoji / wide Unicode (Windows GBK consoles can't)
if sys.stdout.encoding and sys.stdout.encoding.lower() in ("gbk", "cp936", "cp1252"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MAX_CHARS = 30_000  # ~7k tokens — safe headroom below qwen3.5 context limit


def extract_text(pdf_path: str, page_range: tuple[int, int] | None = None) -> tuple[str, int]:
    """Return (text_with_page_markers, page_count).

    If page_range is given as (start, end) 1-indexed inclusive, only those pages
    are extracted.
    """
    doc = fitz.open(pdf_path)
    page_count = len(doc)

    if page_range is not None:
        start, end = page_range
        pages: list[str] = []
        for i in range(start - 1, min(end, page_count)):
            text = doc[i].get_text().strip()
            if text:
                pages.append(f"[Page {i + 1}]\n{text}")
        doc.close()
        return "\n\n".join(pages), page_count

    pages = []
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            pages.append(f"[Page {i + 1}]\n{text}")
    doc.close()
    return "\n\n".join(pages), page_count


def build_prompt(text: str) -> str:
    return (
        "Read the following text extracted from a PDF document. "
        "Produce exactly three sections using the headings below.\n\n"
        "## Overview\n"
        "A 2-3 sentence summary of what this document is about.\n\n"
        "## Key Points\n"
        "- Bullet points of the main ideas. Every point MUST include a [Page X] citation "
        "based on the [Page X] markers in the source text.\n"
        "- Example: \"The system uses FAISS for vector search [Page 3].\"\n\n"
        "## Limitations\n"
        "- What the document omits, assumes, or could improve.\n\n"
        "Source text:\n"
        f"{text}"
    )


def parse_page_range(range_str: str) -> tuple[int, int]:
    """Parse 'START-END' into (start, end) 1-indexed inclusive.

    Prints a friendly message and exits on malformed input.
    """
    m = re.fullmatch(r"(\d+)-(\d+)", range_str)
    if not m:
        print(
            f"Error: --pages must be in the form START-END (e.g. 1-5), got '{range_str}'.",
            file=sys.stderr,
        )
        sys.exit(1)

    start, end = int(m.group(1)), int(m.group(2))

    if start < 1:
        print(
            f"Error: page numbers start at 1 (got {start}).",
            file=sys.stderr,
        )
        sys.exit(1)

    if end < start:
        print(
            f"Error: end page ({end}) must be >= start page ({start}).",
            file=sys.stderr,
        )
        sys.exit(1)

    return start, end


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarise a PDF lecture slide deck via OpenRouter LLM."
    )
    parser.add_argument("pdf", help="path to the PDF file")
    parser.add_argument(
        "--pages",
        metavar="START-END",
        help="only summarise pages START through END (e.g. --pages 1-5)",
    )
    args = parser.parse_args()

    pdf_path = args.pdf

    if not os.path.isfile(pdf_path):
        print(f"Error: file not found — '{pdf_path}'", file=sys.stderr)
        sys.exit(1)

    # ── API key ──────────────────────────────────────────────
    # .env files are normally UTF-8; this project's .env is UTF-16LE.
    # Try both so the code works regardless of encoding.
    try:
        load_dotenv(encoding="utf-8")
    except UnicodeDecodeError:
        load_dotenv(encoding="utf-16")  # fallback for Windows UTF-16LE .env
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print(
            "Error: OPENROUTER_API_KEY is missing. Add it to .env and try again.",
            file=sys.stderr,
        )
        sys.exit(1)

    # ── Page range (optional) ────────────────────────────────
    page_range: tuple[int, int] | None = None
    if args.pages is not None:
        page_range = parse_page_range(args.pages)

    # ── Extract text ─────────────────────────────────────────
    try:
        text, page_count = extract_text(pdf_path, page_range)
    except fitz.FileNotFoundError:
        print(f"Error: cannot open PDF — '{pdf_path}'", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error: failed to read PDF — {exc}", file=sys.stderr)
        sys.exit(1)

    # Validate page range against actual page count
    if page_range is not None:
        start, end = page_range
        if start > page_count:
            print(
                f"Error: start page ({start}) is beyond the last page ({page_count}).",
                file=sys.stderr,
            )
            sys.exit(1)
        if end > page_count:
            print(
                f"Note: end page ({end}) exceeds the document ({page_count} pages); "
                f"using pages {start}–{page_count}.",
                file=sys.stderr,
            )

    if not text.strip():
        print(
            f"This PDF has {page_count} page(s) but no extractable text. "
            "It may be a scanned document (image-only pages). "
            "OCR is required to extract text from scanned PDFs.",
            file=sys.stderr,
        )
        sys.exit(0)

    # Warn on long text rather than silently truncating
    if len(text) > MAX_CHARS:
        print(
            f"Warning: extracted text is {len(text):,} chars; "
            f"truncating to {MAX_CHARS:,} to stay within model limits.",
            file=sys.stderr,
        )
        text = text[:MAX_CHARS]

    # ── Call OpenRouter LLM ──────────────────────────────────
    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    try:
        response = client.chat.completions.create(
            model="inclusionai/ling-3.0-flash:free",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an academic summarizer. Output exactly three sections "
                        "with markdown headings: ## Overview, ## Key Points, ## Limitations. "
                        "Every key point must include a [Page X] citation."
                    ),
                },
                {"role": "user", "content": build_prompt(text)},
            ],
        )
    except openai.AuthenticationError:
        print(
            "Error: OpenRouter authentication failed. Check your OPENROUTER_API_KEY.",
            file=sys.stderr,
        )
        sys.exit(1)
    except openai.APIError as exc:
        print(f"Error: OpenRouter API error — {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error: unexpected error calling LLM — {exc}", file=sys.stderr)
        sys.exit(1)

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
