from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.model_service import embedding_model
from rag.rag_pipeline import answer_question


router = APIRouter(
    prefix="/query",
    tags=["Query"]
)

class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question to ask about the uploaded document."
    )

    document_id: str | None = Field(
        default=None,
        description="ID of the document to search."
    )

    # Limit retrieval depth to a practical range for grounded document QA.
    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of relevant chunks to retrieve."
    )


@router.post("")
def query(request: QueryRequest):
    """Answer a question using the RAG pipeline."""

    # Strip whitespace so whitespace-only questions are rejected.
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    answer, sources = answer_question(
        question=question,
        model=embedding_model,
        top_k=request.top_k,
        document_id=request.document_id
    )

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }

