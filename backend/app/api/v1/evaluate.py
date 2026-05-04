# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/api/v1/evaluate.py

"""
Endpoint pour évaluer une position.

Utilise l'agent LangGraph mais force le fallback Stockfish
si aucune théorie d'ouverture n'est disponible.
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
        result = await run_agent(fen)

        # Erreur FEN / erreur métier
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])

        # Si la position est encore dans la théorie
        if result.get("type") == "theory":
            return {
                "fen": fen,
                "evaluation": None,
                "message": "Position théorique — utiliser /agent pour plus de détails",
            }

        return {
            "fen": fen,
            "evaluation": result.get("evaluation"),
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
