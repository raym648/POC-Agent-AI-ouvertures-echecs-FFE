# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/stockfish_node.py

from app.agents.state import AgentState
from app.services.stockfish_service import StockfishService


stockfish_service = StockfishService(
    path="/usr/games/stockfish",
    depth=15,
)


def stockfish_node(state: AgentState) -> AgentState:
    if not state["is_valid"]:
        return state

    if state.get("moves"):
        return state

    try:
        result = stockfish_service.evaluate(state["fen"])
        return {
            **state,
            "evaluation": result,
            "source": "stockfish",
        }

    except Exception as e:
        return {
            **state,
            "error": str(e),
        }
