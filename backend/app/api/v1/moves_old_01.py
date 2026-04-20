# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/api/v1/moves.py

"""
Endpoint /api/v1/moves/{fen}
"""

from fastapi import APIRouter, HTTPException
from app.services.lichess_service import LichessService
from app.services.stockfish_service import StockfishService
from app.services.fen_validator import validate_fen
from app.core.config import settings

router = APIRouter()
lichess_service = LichessService()
stockfish_service = StockfishService(settings.STOCKFISH_PATH)


@router.get("/api/v1/moves/{fen}")
async def get_moves(fen: str):
    """
    Retourne les coups recommandés :
    - Lichess si disponible
    - sinon Stockfish
    """

    # 🔍 Validation FEN
    if not validate_fen(fen):
        raise HTTPException(status_code=400, detail="Invalid FEN")

    # 🌐 Tentative via Lichess
    moves = await lichess_service.extract_moves(fen)

    # ♟️ Si Lichess retourne des résultats
    if moves:
        return {
            "fen": fen,
            "source": "lichess",
            "moves": moves
        }

    # 🔁 Fallback Stockfish
    evaluation = stockfish_service.evaluate(fen)

    return {
        "fen": fen,
        "source": "stockfish",
        "moves": [
            {
                "move": evaluation["best_move"],
                "evaluation": evaluation["value"]
            }
        ]
    }
