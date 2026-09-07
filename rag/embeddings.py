import torch
from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-small-en-v1.5"

# Use GPU acceleration when CUDA is available, otherwise fall back to CPU.
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# BGE uses a retrieval-oriented instruction for query embeddings.
QUERY_INSTRUCTION = (
    "Represent this sentence for searching relevant passages: "
)


def load_embedding_model() -> SentenceTransformer:
    """Load the BGE embedding model on the available device."""

    model = SentenceTransformer(
        MODEL_NAME,
        device=DEVICE
    )

    return model


def create_document_embeddings(
    chunks: list[dict],
    model: SentenceTransformer
):
    """Create embeddings for document chunks."""

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    return embeddings


def create_query_embedding(
    query: str,
    model: SentenceTransformer
):
    """Create an embedding for a user's search query."""

    query_with_instruction = QUERY_INSTRUCTION + query

    embedding = model.encode(
        query_with_instruction,
        normalize_embeddings=True
    )

    return embedding