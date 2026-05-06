# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/opening_detector_node.py

from app.agents.state import AgentState


def opening_detector_node(state: AgentState) -> AgentState:
    if not state["is_valid"]:
        return state

    try:
        opening = None

        if state.get("moves"):
            first_moves = " ".join([m.get("san", "") for m in state["moves"][:3]])

            if "e4 c5" in first_moves:
                opening = "Sicilian Defense"
            elif "e4 e5 Nf3 Nc6 Bb5" in first_moves:
                opening = "Ruy Lopez"
            elif "d4 d5 c4" in first_moves:
                opening = "Queen's Gambit"

        if not opening:
            opening = "chess opening strategy"

        return {
            **state,
            "opening": opening,
        }

    except Exception as e:
        return {
            **state,
            "opening": None,
            "error": str(e),
        }
