from rag.retriever import retrieve_chunks
from rag.generator import generate_answer


def build_context(retrieved_chunks):
    """Build context from retrieved document chunks."""

    context_parts = []

    for i, chunk in enumerate(
        retrieved_chunks,
        start=1
    ):
        context_parts.append(
            f"[Evidence {i} | Page {chunk['page_number']} | "
            f"Chunk {chunk['chunk_number']}]\n"
            f"{chunk['text']}"
        )

    return "\n\n".join(context_parts)


def build_sources(retrieved_chunks):
    """Build source information from retrieved metadata."""

    sources = []

    seen = set()

    for chunk in retrieved_chunks:

        source_key = (
            chunk["document_id"],
            chunk["page_number"]
        )

        if source_key in seen:
            continue

        seen.add(source_key)

        sources.append({
            "document_id": chunk["document_id"],
            "filename": chunk["filename"],
            "page_number": chunk["page_number"],
            "chunk_id": chunk["chunk_id"],
            "chunk_number": chunk["chunk_number"]
        })

    return sources


def answer_question(
    question: str,
    model,
    top_k: int = 5,
    document_id: str | None = None
):
    """Retrieve evidence and generate a grounded answer."""

    # Retrieve relevant chunks from Chroma

    retrieved_chunks = retrieve_chunks(
        query=question,
        model=model,
        top_k=top_k,
        document_id=document_id
    )

    # Build context for Qwen

    context = build_context(
        retrieved_chunks
    )

    # Generate grounded answer using Qwen

    answer = generate_answer(
        question=question,
        context=context
    )

    # Generate source metadata

    sources = build_sources(
        retrieved_chunks
    )

    # Return answer + sources

    return answer, sources