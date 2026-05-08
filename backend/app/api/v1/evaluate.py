# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/api/v1/evaluate.py

"""
Endpoint pour évaluer une position avec Stockfish.

Utilise le workflow LangGraph "evaluate".
"""

from fastapi import APIRouter, HTTPException

from app.agents.langgraph_agent import run_agent


router = APIRouter(
    prefix="/evaluate",
    tags=["Evaluation"],
)


@router.get("/{fen:path}")
async def evaluate(fen: str):
    """
    Évalue une position avec Stockfish.

    Args:
        fen (str): position FEN

    Returns:
        dict: score d'évaluation
    """

    try:

        result = await run_agent(
            fen,
            mode="evaluate",
        )

        # =============================================
        # ERREURS
        # =============================================

        if result.get("error"):

            raise HTTPException(
                status_code=400,
                detail=result["error"],
            )

        # =============================================
        # SUCCESS
        # =============================================

        return {
            "fen": fen,
            "evaluation": result.get("evaluation"),
            "source": result.get("source"),
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
