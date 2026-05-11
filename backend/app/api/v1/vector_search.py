# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/api/v1/vector_search.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.langgraph_agent import run_agent


router = APIRouter()


class SearchRequest(BaseModel):
    fen: str


@router.post("/vector-search")
async def vector_search(request: SearchRequest):

    try:

        result = await run_agent(
            request.fen,
            mode="rag",
        )

        if result.get("error"):

            raise HTTPException(
                status_code=400,
                detail=result["error"],
            )

        return {
            "fen": request.fen,
            "opening": result.get("opening"),
            "rag_context": result.get("rag_context"),
            "source": result.get("source"),
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
