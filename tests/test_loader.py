from rag.document_loader import extract_pages_from_pdf
from rag.chunker import create_chunks

from rag.embeddings import (
    load_embedding_model,
    create_document_embeddings
)

pdf_path = "data/documents/sample.pdf"

# Extract pages
pages = extract_pages_from_pdf(pdf_path)

# Create chunks
chunks = create_chunks(pages)

# Load embedding model
model = load_embedding_model()

# Create embeddings
embeddings = create_document_embeddings(
    chunks,
    model
)

print("\nTotal pages with extracted text:", len(pages))
print("Total chunks created:", len(chunks))
print("Embedding device:",model.device)
print("Total embeddings created:", len(embeddings))
print("Embedding dimension:", embeddings.shape[1])

print("\nFirst chunk:")
print(chunks[0])

print("\nFirst 10 values of first embedding:")
print(embeddings[0][:10])