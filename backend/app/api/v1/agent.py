# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/api/v1/agent.py

"""
Route FastAPI pour l'agent LangGraph.

Expose un endpoint unique :
/api/v1/agent/analyze/{fen}

Cet endpoint utilise toute la logique décisionnelle :
Lichess → fallback Stockfish
"""


from fastapi import APIRouter, HTTPException

# from backend.app.agents.langgraph_agent import run_agent
from app.agents.langgraph_agent import run_agent


router = APIRouter(
    prefix="/agent",
    tags=["Agent IA"]
)


@router.get("/analyze/{fen}")
async def analyze_position(fen: str):
    """
    Analyse complète d'une position via LangGraph.

    Args:
        fen (str): position d'échecs au format FEN

    Returns:
        dict: résultat structuré (théorie ou évaluation)
    """

    try:
        # ✅ FIX : await obligatoire
        result = await run_agent(fen)

        # Gestion des erreurs métier
        if "error" in result and result["error"]:
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
