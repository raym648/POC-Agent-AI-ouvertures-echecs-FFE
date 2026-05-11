# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/api/v1/vector_search.py

"""
Endpoint de recherche vectorielle.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.rag.embedding_service import embedding_service
from app.rag.milvus_service import milvus_service
from app.core.config import settings


router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    top_k: int | None = None


@router.post("/vector-search")
def vector_search(request: SearchRequest):

    top_k = request.top_k or settings.RAG_TOP_K

    query_embedding = embedding_service.embed_text(request.query)

    results = milvus_service.search(query_embedding, top_k)

    return {
        "query": request.query,
        "results": results,
    }
