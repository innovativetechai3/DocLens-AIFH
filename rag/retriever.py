from rag.embeddings import create_query_embedding
from rag.vector_store import get_chroma_collection

def retrieve_chunks(
    query: str,
    model,
    top_k: int = 5,
    document_id: str | None = None
):
    """Retrieve semantically relevant document chunks for a user query."""

    collection = get_chroma_collection()

    query_embedding = create_query_embedding(
        query,
        model
    )

    # Restrict retrieval to the selected document when requested.
    where_filter = None

    if document_id:
        where_filter = {
            "document_id": document_id
        }

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=top_k,
        where=where_filter,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    retrieved_chunks = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    # Guard against duplicate chunks in the final evidence set.
    seen_chunks = set()

    for (
        document,
        metadata,
        distance
    ) in zip(
        documents,
        metadatas,
        distances
    ):

        chunk_key = (
            metadata["document_id"],
            metadata["chunk_id"]
        )

        if chunk_key in seen_chunks:
            continue

        seen_chunks.add(
            chunk_key
        )

        chunk = {
            "document_id": metadata["document_id"],
            "filename": metadata["filename"],
            "chunk_id": metadata["chunk_id"],
            "page_number": metadata["page_number"],
            "chunk_number": metadata["chunk_number"],
            "text": document,
            "distance": distance
        }

        retrieved_chunks.append(
            chunk
        )

    return retrieved_chunks