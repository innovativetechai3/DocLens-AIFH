from rag.document_loader import extract_pages_from_pdf
from rag.chunker import create_chunks
from rag.embeddings import (
    load_embedding_model,
    create_document_embeddings
)
from rag.vector_store import get_chroma_collection, add_chunks_to_chroma


pdf_path = "data/documents/sample.pdf"

document_id = "test-sample-document"
filename = "sample.pdf"


# Extract PDF
pages = extract_pages_from_pdf(pdf_path)

# Create chunks with document metadata
chunks = create_chunks(
    pages,
    document_id=document_id,
    filename=filename
)

# Make chunk IDs unique for this document
for chunk in chunks:
    chunk["chunk_id"] = (
        f"{document_id}_{chunk['chunk_id']}"
    )

# Load embedding model
model = load_embedding_model()

# Create embeddings
embeddings = create_document_embeddings(
    chunks,
    model
)

# Get persistent Chroma collection
collection = get_chroma_collection()

# Store chunks + embeddings + metadata
add_chunks_to_chroma(
    collection,
    chunks,
    embeddings
)

print("\nChroma indexing completed.")
print("Collection name:", collection.name)
print("Documents stored:", collection.count())
print("Embedding dimension:", embeddings.shape[1])