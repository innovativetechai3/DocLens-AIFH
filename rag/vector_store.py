import chromadb

# Persistent storage keeps indexed documents available across app restarts.
CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "doclensai_documents"


def get_chroma_collection():
    """Create or load the persistent Chroma collection."""

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,

        # Cosine distance is used for normalized sentence-transformer embeddings.
        metadata={"hnsw:space": "cosine"}
    )

    return collection


def add_chunks_to_chroma(
    collection,
    chunks: list[dict],
    embeddings
):
    """Store chunks, metadata, and embeddings in Chroma."""

    ids = [chunk["chunk_id"] for chunk in chunks]

    documents = [chunk["text"] for chunk in chunks]

    metadatas = [
        {
            "document_id": chunk["document_id"],
            "filename": chunk["filename"],
            "chunk_id": chunk["chunk_id"],
            "page_number": chunk["page_number"],
            "chunk_number": chunk["chunk_number"],
            "page_character_count": chunk["page_character_count"]
        }
        for chunk in chunks
    ]


    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings.tolist()
    )

    return collection