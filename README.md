# **DocLens AI**

##**Evidence Grounded Document Intelligence System**

##**Project Type:Retrieval Augmented Generation (RAG)**  
## **Version:1.0  **
## **Vision: Ask. Retrieve. Ground. Trust.**
## **Architecture:Local-first, two-step RAG ** 
## **Developed for:Educational **

## Overview

DocLens AI is a local document question answering application that allows users to upload text-based PDF documents, retrieve semantically relevant evidence, and generate grounded answers using a local Large Language Model (LLM).

The system combines PDF text extraction, recursive text chunking, dense vector embeddings, persistent vector storage, semantic retrieval, and local LLM generation. Answers are returned together with evidence source metadata so users can trace the retrieved document pages and chunks.

DocLens AI is designed to run locally and does not require a paid external LLM API.

## Application & RAG Pipeline

```text
Frontend
   ↓
FastAPI Backend
   ↓
PDF Text Extraction
   ↓
Chunking
   ↓
BGE Embeddings
   ↓
Chroma Vector Store
   ↓
Semantic Retrieval
   ↓
Ollama Local LLM
   ↓
Grounded Answer + Evidence Sources
```

## Core Features

- Upload text-based PDF documents.
- Extract PDF text while preserving original page numbers.
- Split document text into overlapping chunks.
- Generate dense embeddings using `BAAI/bge-small-en-v1.5`.
- Store embeddings and metadata in persistent ChromaDB storage.
- Perform semantic vector retrieval against uploaded documents.
- Restrict retrieval to a selected document.
- Generate evidence grounded answers using local Ollama `qwen2.5:7b`.
- Return source metadata including document, page, and chunk information.
- Configure retrieval depth through `top_k`.
- List and delete indexed documents.
- Use a FastAPI backend with an HTML/CSS/JavaScript frontend.
- Run locally without a paid LLM API.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | FastAPI |
| ASGI Server | Uvicorn |
| Frontend | HTML, CSS, JavaScript |
| PDF Extraction | PyMuPDF |
| Text Splitting | LangChain Text Splitters |
| Embedding Model | BAAI/bge-small-en-v1.5 |
| Embedding Framework | Sentence Transformers |
| Vector Database | ChromaDB |
| Local LLM Runtime | Ollama |
| Local LLM | qwen2.5:7b |
| HTTP Communication | Requests |
| ML Runtime | PyTorch |

## Project Structure

```text
DocLens AI/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── documents.py
│   │   └── query.py
│   └── services/
│       ├── __init__.py
│       ├── document_service.py
│       └── model_service.py
│
├── data/
│   └── document_registry.json
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   ├── logo.png
│   └── it-logo.png
│
├── rag/
│   ├── __init__.py
│   ├── document_loader.py
│   ├── chunker.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── generator.py
│   └── rag_pipeline.py
│
├── tests/
│   ├── __init__.py
│   ├── test_chroma.py
│   ├── test_generator.py
│   ├── test_loader.py
│   ├── test_rag.py
│   └── test_retrieval.py
│
├── README.md
├── requirements.txt
└── .gitignore
```

Runtime directories such as `data/uploads/`, `data/chroma_db/`, and the local test-document directory are intentionally excluded from version control.

## RAG Configuration

Current project defaults include:

- Embedding model: `BAAI/bge-small-en-v1.5`
- Embedding dimension: 384
- Chunk size: 1000 characters
- Chunk overlap: 200 characters
- Vector similarity: cosine distance
- Default retrieval depth (`top_k`): 5
- Maximum API retrieval depth:10
- LLM: `qwen2.5:7b`
- Generation temperature: 0.0

The BGE query embedding uses a retrieval oriented instruction before encoding the user question.

## How It Works

### 1. Document Ingestion

When a PDF is uploaded:

1. FastAPI receives and validates the PDF.
2. PyMuPDF extracts text while preserving page numbers.
3. Empty pages are skipped.
4. The extracted text is divided into overlapping chunks.
5. BGE generates a vector embedding for each chunk.
6. Chunks, embeddings, and metadata are stored in ChromaDB.
7. Document metadata is registered locally.

### 2. Retrieval

When a user asks a question:

1. The question is converted into a BGE query embedding.
2. ChromaDB performs semantic similarity search.
3. Retrieval can optionally be restricted to the selected document.
4. The most relevant chunks are returned as evidence.

### 3. Grounded Generation

The retrieved evidence is supplied to the local Ollama LLM together with instructions to answer from the provided document context. The application then returns:

- The generated answer, and
- Evidence source metadata containing document, page, and chunk information.

## Installation

### Prerequisites

Install:

- Python
- Ollama
- Git (recommended)
- An NVIDIA GPU is optional

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd "DocLens AI"
```

### 2. Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### PyTorch and GPU Acceleration

DocLens AI was developed and tested with a CUDA-enabled PyTorch environment:

- PyTorch `2.11.0+cu130`
- CUDA 13.0 PyTorch build
- NVIDIA GeForce RTX 4070 Laptop GPU

The repository uses `torch==2.11.0` as the portable project dependency. GPU acceleration is optional. The embedding code automatically uses CUDA when it is available and falls back to CPU otherwise.

For GPU acceleration, install the PyTorch build appropriate for your operating system, Python version, GPU, and supported CUDA configuration.

### 4. Install the Local LLM

Pull the required Ollama model:

```bash
ollama pull qwen2.5:7b
```

Ensure Ollama is running:

```bash
ollama serve
```

### 5. Start DocLens AI

From the project root:

```bash
uvicorn backend.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

FastAPI interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## API Overview

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Serve the DocLens AI frontend |
| `GET` | `/health` | Application health check |
| `GET` | `/documents` | List registered documents |
| `POST` | `/documents/upload` | Upload and index a PDF |
| `DELETE` | `/documents/{document_id}` | Delete an indexed document |
| `POST` | `/query` | Ask a grounded document question |

A query request supports a question, optional document ID, and retrieval depth (`top_k`).

Example:

```json
{
  "question": "What was the net income in 2025?",
  "document_id": "<document-id>",
  "top_k": 5
}
```

## Tests and Local Test PDF

The `tests/` directory is intentionally retained in the repository because it documents the development checks used for the document loading, vector-store, retrieval, generation, and RAG pipeline components.

The sample PDF itself is intentionally not included in the GitHub repository.

Some test scripts expect a local text-based PDF at:

```text
data/documents/sample.pdf
```

To run those tests locally:

1. Create the directory if it does not already exist:

```text
data/documents/
```

2. Place a suitable text-based PDF in that directory.
3. Rename it to:

```text
sample.pdf
```

4. Run the required test script from the project root, for example:

```bash
python -m tests.test_loader
python -m tests.test_chroma
python -m tests.test_retrieval
python -m tests.test_generator
python -m tests.test_rag
```

The sample document is not committed because it is test data rather than application source code. Test results depend on the content of the PDF used.


## Data and Privacy

DocLens AI follows a local-first architecture:

- Uploaded PDFs are processed locally.
- Embeddings are generated locally.
- ChromaDB storage is local.
- Answer generation uses a locally running Ollama model.
- No paid external LLM API is required.

Runtime document data and vector-store files are excluded from Git through `.gitignore`.

## Limitations

- Best suited to text-based PDFs.
- Scanned/image-only PDFs require OCR, which is not part of the current version.
- Complex tables may not preserve their original visual structure during text extraction.
- Retrieval quality depends on document content, chunking, embedding quality, and `top_k`.
- The local LLM must already be available through Ollama.
- Evidence sources identify retrieved pages/chunks but do not constitute a formal citation-management system.

## Future Improvements

Potential extensions include:

- OCR support for scanned PDFs.
- Improved table extraction.
- Hybrid dense + keyword retrieval.
- Reranking.
- Automated retrieval and answer-quality evaluation.
- Streaming answer generation.
- Additional document formats.
- More comprehensive automated tests.

## Developer

**Farhana Hameed**

## License

This project is developed for educational Purpose

© 2026 Innovative Tech. All Rights Reserved.