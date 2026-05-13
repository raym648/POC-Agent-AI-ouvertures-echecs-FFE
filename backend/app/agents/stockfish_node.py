# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/stockfish_node.py

from app.agents.state import AgentState
from app.services.stockfish_service import StockfishService


# =========================================================
# SERVICE
# =========================================================

stockfish_service = StockfishService(
    path="/usr/games/stockfish",
    depth=15,
)


# =========================================================
# NODE
# =========================================================

async def stockfish_node(
    state: AgentState,
) -> AgentState:
    """
    Node LangGraph Stockfish.

    Workflow :
        validate_fen
            -> stockfish

    Endpoint dédié à l'analyse moteur.

    IMPORTANT :
    - plus de fallback Lichess
    - plus de logique full workflow
    """

    # =====================================================
    # VALIDATION
    # =====================================================

    if not state.get("is_valid"):

        return {
            **state,
            "evaluation": None,
            "error": "Invalid FEN",
        }

    try:

        # =================================================
        # EVALUATION
        # =================================================

        result = stockfish_service.evaluate(
            state["fen"]
        )

        # =================================================
        # SUCCESS
        # =================================================

        return {
            **state,
            "evaluation": result,
            "source": "stockfish",
        }

    except Exception as e:

        return {
            **state,
            "evaluation": None,
            "error": str(e),
        }
