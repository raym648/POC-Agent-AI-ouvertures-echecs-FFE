# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/api/v1/agent.py

"""
Route FastAPI pour l'agent LangGraph complet.

Expose :
/api/v1/agent/analyze/{fen}

Workflow complet :
Lichess
→ fallback Stockfish
→ RAG Milvus
→ vidéos YouTube
→ explication LLM
"""

from fastapi import APIRouter, HTTPException

from app.agents.langgraph_agent import run_agent


router = APIRouter(
    prefix="/agent",
    tags=["Agent IA"],
)


@router.get("/analyze/{fen:path}")
async def analyze_position(fen: str):
    """
    Analyse complète d'une position via LangGraph.

    Args:
        fen (str): position d'échecs au format FEN

    Returns:
        dict: analyse enrichie
    """

    try:

        result = await run_agent(
            fen,
            mode="full",
        )

        # =============================================
        # ERREURS METIER
        # =============================================

        if result.get("error"):

            raise HTTPException(
                status_code=400,
                detail=result["error"],
            )

        return result

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
