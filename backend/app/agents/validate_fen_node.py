# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/validate_fen_node.py

from app.agents.state import AgentState
from app.services.fen_validator import validate_fen


def validate_fen_node(state: AgentState) -> AgentState:
    try:
        is_valid = validate_fen(state["fen"])
        return {
            **state,
            "is_valid": is_valid,
            "error": None if is_valid else "Invalid FEN",
        }
    except Exception as e:
        return {
            **state,
            "is_valid": False,
            "error": str(e),
        }
