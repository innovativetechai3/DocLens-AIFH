from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import uuid

from rag.document_loader import extract_pages_from_pdf
from rag.chunker import create_chunks

from rag.embeddings import create_document_embeddings
from backend.services.model_service import embedding_model

from rag.vector_store import (
    get_chroma_collection,
    add_chunks_to_chroma
)

from backend.services.document_service import (
    register_document,
    get_all_documents,
    delete_document,
    document_exists
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

# Upload Document

@router.post("/upload")
def upload_document(file: UploadFile = File(...)):
    """Upload a PDF and index it into Chroma."""

    # Validate file type

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    # Check for duplicate document

    if document_exists(file.filename):

        raise HTTPException(
            status_code=409,
            detail=(
                f"Document '{file.filename}' "
                "already exists."
            )
        )

    # Create unique document ID

    document_id = str(uuid.uuid4())

    # Create upload directory

    upload_dir = Path("data/uploads")

    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save uploaded PDF

    file_path = upload_dir / f"{document_id}.pdf"

    try:

        with file_path.open("wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except OSError as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save uploaded file: {e}"
        )

    # Extract pages

    pages = extract_pages_from_pdf(
        str(file_path)
    )

    if not pages:

        # Remove invalid/empty uploaded file
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=400,
            detail=(
                "No text could be extracted "
                "from the PDF."
            )
        )

    # Create chunks

    chunks = create_chunks(pages)

    if not chunks:

        # Remove uploaded file if no chunks were created
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=400,
            detail="No chunks could be created from the PDF."
        )

    # Add document metadata to chunks

    for chunk in chunks:

        # Make chunk IDs unique across documents
        chunk["chunk_id"] = (
            f"{document_id}_{chunk['chunk_id']}"
        )

        chunk["document_id"] = document_id

        chunk["filename"] = file.filename

    # Create embeddings

    embeddings = create_document_embeddings(
        chunks,
        embedding_model
    )

    # Get Chroma collection

    collection = get_chroma_collection()

    # Store chunks and embeddings in Chroma

    add_chunks_to_chroma(
        collection,
        chunks,
        embeddings
    )

    # Register document metadata

    register_document(
        document_id=document_id,
        filename=file.filename,
        pages=len(pages),
        chunks=len(chunks)
    )

    # Return response

    return {
        "message": (
            "Document uploaded and "
            "indexed successfully."
        ),
        "document_id": document_id,
        "filename": file.filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "embedding_dimension": embeddings.shape[1]
    }

# List Documents

@router.get("")
def list_documents():
    """Return all registered documents."""

    documents = get_all_documents()

    return {
        "documents": documents,
        "count": len(documents)
    }

# Delete Document

@router.delete("/{document_id}")
def delete_document_endpoint(
    document_id: str
):
    """Delete a document from the system."""

    return delete_document(
        document_id
    )