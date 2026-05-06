# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/lichess_node.py

from app.agents.state import AgentState
from app.services.lichess_service import LichessService


lichess_service = LichessService()


async def lichess_node(state: AgentState) -> AgentState:
    if not state["is_valid"]:
        return state

    try:
        moves = await lichess_service.extract_moves(state["fen"])

        if moves:
            return {
                **state,
                "moves": moves,
                "source": "lichess",
            }

        return {
            **state,
            "moves": [],
            "source": None,
        }

    except Exception as e:
        return {
            **state,
            "moves": [],
            "error": str(e),
        }
