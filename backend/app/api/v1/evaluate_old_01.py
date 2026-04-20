# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/api/v1/evaluate.py

from fastapi import APIRouter, HTTPException
from app.services.lichess_service import LichessService
from app.services.stockfish_service import StockfishService
from app.services.fen_validator import validate_fen
from app.core.config import settings

router = APIRouter()
lichess_service = LichessService()
stockfish_service = StockfishService(settings.STOCKFISH_PATH)


@router.get("/api/v1/evaluate/{fen}")
async def evaluate_position(fen: str):
    """
    Retourne l’évaluation d’une position :
    - Lichess (cloud)
    - fallback Stockfish
    """

    if not validate_fen(fen):
        raise HTTPException(status_code=400, detail="Invalid FEN")

    data = await lichess_service.get_cloud_evaluation(fen)

    if data and "pvs" in data:
        return {
            "fen": fen,
            "source": "lichess",
            "evaluation": data["pvs"][0].get("cp", 0),
            "depth": data.get("depth", 0)
        }

    # fallback Stockfish
    evaluation = stockfish_service.evaluate(fen)

    return {
        "fen": fen,
        "source": "stockfish",
        "evaluation": evaluation["value"]
    }
