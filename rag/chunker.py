from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_chunks(
    pages: list[dict],
    document_id: str | None = None,
    filename: str | None = None
) -> list[dict]:

    # Overlap helps preserve context when relevant text spans chunk boundaries.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = []

    for page in pages:
        page_chunks = splitter.split_text(page["text"])

        for chunk_number, chunk_text in enumerate(page_chunks, start=1):

            base_chunk_id = (
                f"p{page['page_number']}_c{chunk_number}"
            )

            chunk = {
                "chunk_id": base_chunk_id,
                "page_number": page["page_number"],
                "chunk_number": chunk_number,
                "page_character_count": page["character_count"],
                "text": chunk_text
            }

            if document_id is not None:
                chunk["document_id"] = document_id

            if filename is not None:
                chunk["filename"] = filename

            chunks.append(chunk)

    return chunks