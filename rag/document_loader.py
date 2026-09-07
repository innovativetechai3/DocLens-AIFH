import pymupdf


def extract_pages_from_pdf(
    file_path: str
) -> list[dict]:
    """Extract text while preserving the original PDF page numbers."""

    pages = []

    with pymupdf.open(
        file_path
    ) as document:

        for page_number, page in enumerate(
            document,
            start=1
        ):

            text = page.get_text().strip()

            if not text:
                continue

            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                    "character_count": len(text)
                }
            )

    return pages