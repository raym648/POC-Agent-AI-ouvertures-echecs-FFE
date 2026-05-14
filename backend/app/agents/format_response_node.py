# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/format_response_node.py

from typing import Any, Dict

from app.agents.state import AgentState


def format_response_node(state: AgentState) -> Dict[str, Any]:
    """
    Formate la réponse finale envoyée au frontend.

    Responsabilités :
    - normaliser la structure API
    - préserver compatibilité frontend Angular
    - sérialiser les enrichissements IA
    """

    # =================================================
    # INVALID FEN / VALIDATION FAILURE
    # =================================================
    
    if (
        state.get("fen") is not None
        and not state["is_valid"]
    ):

        return {
            "fen": state["fen"],
            "error": state["error"],
        }

    # =================================================
    # BASE RESPONSE
    # =================================================

    response: Dict[str, Any] = {
        "fen": state["fen"],
        "source": state.get("source"),
    }

    # =================================================
    # THEORY MOVES
    # =================================================

    if state.get("moves"):

        response["type"] = "theory"
        response["moves"] = state["moves"]

    # =================================================
    # STOCKFISH EVALUATION
    # =================================================

    else:

        response["type"] = "evaluation"
        response["evaluation"] = state.get("evaluation")

    # =================================================
    # RAG CONTEXT
    # =================================================

    if state.get("rag_context"):

        # IMPORTANT:
        # Angular frontend attend explicitement:
        # "rag_context"
        # et NON "rag"

        response["rag_context"] = state["rag_context"]

    # =================================================
    # VIDEOS
    # =================================================

    if state.get("videos"):

        response["videos"] = state["videos"]

    # =================================================
    # EXPLANATION
    # =================================================

    if state.get("explanation"):

        response["explanation"] = state["explanation"]

    # =================================================
    # OPENING
    # =================================================

    if state.get("opening"):

        response["opening"] = state["opening"]

    # =================================================
    # OPTIONAL ERROR PROPAGATION
    # =================================================

    if state.get("error"):

        response["error"] = state["error"]

    return response
