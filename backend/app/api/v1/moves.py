# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/api/v1/moves.py

"""
Endpoint pour récupérer les coups théoriques.

Utilise l'agent LangGraph mais filtre uniquement
les résultats issus de Lichess.
"""

from fastapi import APIRouter, HTTPException

from backend.app.agents.langgraph_agent import run_agent

router = APIRouter(
    prefix="/moves",
    tags=["Moves"]
)


@router.get("/{fen}")
def get_moves(fen: str):
    """
    Récupère les coups théoriques d'une position.

    Args:
        fen (str): position FEN

    Returns:
        dict: liste des coups
    """

    try:
        result = run_agent(fen)

        # Erreur FEN
        if "error" in result and result["error"]:
            raise HTTPException(status_code=400, detail=result["error"])

        # Si pas de théorie disponible
        if result.get("type") != "theory":
            return {
                "fen": fen,
                "moves": [],
                "message": "Position hors théorie (fallback Stockfish disponible via /agent)"  # noqa: E501
            }

        return {
            "fen": fen,
            "moves": result.get("moves", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
