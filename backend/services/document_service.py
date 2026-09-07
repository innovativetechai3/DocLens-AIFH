import json
from pathlib import Path

from fastapi import HTTPException

from rag.vector_store import get_chroma_collection


REGISTRY_PATH = Path("data/document_registry.json")
UPLOAD_DIR = Path("data/uploads")


def load_registry():
    """Load registered document metadata from disk."""

    if not REGISTRY_PATH.exists():
        return []

    try:
        with REGISTRY_PATH.open(
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def save_registry(documents):
    """Persist document metadata to the registry."""

    REGISTRY_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with REGISTRY_PATH.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            documents,
            file,
            indent=4
        )


def register_document(
    document_id,
    filename,
    pages,
    chunks
):
    """Register a newly indexed document."""

    documents = load_registry()

    documents.append(
        {
            "document_id": document_id,
            "filename": filename,
            "pages": pages,
            "chunks": chunks
        }
    )

    save_registry(documents)


def get_all_documents():
    """Return all registered documents."""

    return load_registry()


def document_exists(filename):
    """Check whether a document with the same filename is registered."""

    documents = load_registry()

    return any(
        document["filename"].lower()
        == filename.lower()
        for document in documents
    )


def delete_document(document_id):
    """
    Delete a document and its associated application data.

    Removes:
    - Chroma vectors and chunk metadata
    - Uploaded PDF
    - Document registry entry
    """

    documents = load_registry()

    # Locate the registered document before deleting its resources.
    document = next(
        (
            document
            for document in documents
            if document["document_id"]
            == document_id
        ),
        None
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    # Remove all vector-store entries belonging to this document.
    try:
        collection = get_chroma_collection()

        collection.delete(
            where={
                "document_id": document_id
            }
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to delete document vectors "
                f"from Chroma: {error}"
            )
        )

    # Uploaded PDFs are stored using their document UUID.
    file_path = (
        UPLOAD_DIR /
        f"{document_id}.pdf"
    )

    try:
        if file_path.exists():
            file_path.unlink()

    except OSError as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to delete uploaded PDF: "
                f"{error}"
            )
        )

    # Remove the document from the application registry.
    updated_documents = [
        registered_document
        for registered_document in documents
        if registered_document["document_id"]
        != document_id
    ]

    save_registry(
        updated_documents
    )

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
        "filename": document["filename"]
    }