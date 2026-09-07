
from rag.embeddings import load_embedding_model


# Load one shared embedding model for both ingestion and retrieval.
embedding_model = load_embedding_model()