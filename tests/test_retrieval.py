from rag.embeddings import load_embedding_model
from rag.retriever import retrieve_chunks


# Load embedding model
model = load_embedding_model()

# User question
question = "What was Microsoft's total revenue in fiscal year 2025?"

# Retrieve relevant chunks

retrieved_chunks = retrieve_chunks(
    query=question,
    model=model,
    top_k=5
)

print("\n" + "=" * 80)
print("RETRIEVAL RESULTS")
print("=" * 80)

print(f"\nQuestion: {question}")

for i, chunk in enumerate(retrieved_chunks, start=1):

    print("\n" + "-" * 80)
    print(f"RESULT {i}")
    print("-" * 80)

    print(f"Page: {chunk['page_number']}")
    print(f"Chunk ID: {chunk['chunk_id']}")
    print(f"Chunk: {chunk['chunk_number']}")
    print(f"Distance: {chunk['distance']}")

    print("\nTEXT:")
    print(chunk["text"])