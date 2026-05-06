# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/format_response_node.py

from typing import Dict, Any

from app.agents.state import AgentState


def format_response_node(state: AgentState) -> Dict[str, Any]:
    if not state["is_valid"]:
        return {
            "fen": state["fen"],
            "error": state["error"],
        }

    response: Dict[str, Any] = {
        "fen": state["fen"],
        "source": state.get("source"),
    }

    if state.get("moves"):
        response["type"] = "theory"
        response["moves"] = state["moves"]
    else:
        response["type"] = "evaluation"
        response["evaluation"] = state.get("evaluation")

    if state.get("rag_context"):
        response["rag"] = state["rag_context"]

    if state.get("videos"):
        response["videos"] = state["videos"]

    if state.get("explanation"):
        response["explanation"] = state["explanation"]

    if state.get("opening"):
        response["opening"] = state["opening"]

    return response
