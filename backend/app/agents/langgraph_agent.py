# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/langgraph_agent.py

from typing import Dict, Any, Literal

from app.agents.state import AgentState

from app.agents.validate_fen_node import validate_fen_node
from app.agents.lichess_node import lichess_node
from app.agents.stockfish_node import stockfish_node
from app.agents.rag_node import rag_node
from app.agents.video_node import video_retriever_node
from app.agents.format_response_node import format_response_node
from app.agents.opening_detector_node import opening_detector_node


# =========================================================
# TYPES
# =========================================================

WorkflowMode = Literal[
    "moves",
    "evaluate",
    "rag",
    "videos",
    "complete",
]


# =========================================================
# BASE STATE
# =========================================================

def create_initial_state() -> AgentState:

    return {
        "fen": None,
        "opening": None,
        "is_valid": False,
        "moves": [],
        "evaluation": None,
        "source": None,
        "error": None,
        "rag_context": [],
        "explanation": None,
        "videos": [],
    }


# =========================================================
# MOVES WORKFLOW
# =========================================================

async def run_moves_workflow(
    state: AgentState,
) -> AgentState:
    """
    Workflow moves :

    validate_fen
        -> lichess
        -> opening_detector

    IMPORTANT :
    Angular dépend de state["opening"]
    pour déclencher automatiquement :

    - /videos/{opening}
    - /vector-search
    """

    # =====================================================
    # VALIDATION
    # =====================================================

    state = validate_fen_node(state)

    if not state.get("is_valid"):
        return state

    # =====================================================
    # LICHESS MOVES
    # =====================================================

    state = await lichess_node(state)

    # =====================================================
    # OPENING DETECTION
    # =====================================================

    state = opening_detector_node(state)

    return state


# =========================================================
# EVALUATION WORKFLOW
# =========================================================

async def run_evaluate_workflow(
    state: AgentState,
) -> AgentState:

    state = validate_fen_node(state)

    if not state.get("is_valid"):
        return state

    state = await stockfish_node(state)

    return state


# =========================================================
# RAG WORKFLOW
# =========================================================

async def run_rag_workflow(
    state: AgentState,
) -> AgentState:

    if not state.get("opening"):
        return state

    state = await rag_node(state)

    return state


# =========================================================
# VIDEO WORKFLOW
# =========================================================

async def run_video_workflow(
    state: AgentState,
) -> AgentState:

    if not state.get("opening"):
        return state

    state = await video_retriever_node(state)

    return state


# =========================================================
# COMPLETE WORKFLOW
# =========================================================

async def run_complete_workflow(
    state: AgentState,
) -> AgentState:
    """
    Workflow complet interne.

    NOTE :
    Ce workflow n'est actuellement pas utilisé
    directement par Angular.

    Angular utilise les 4 endpoints REST séparés.
    """

    # =====================================================
    # VALIDATION
    # =====================================================

    state = validate_fen_node(state)

    if not state.get("is_valid"):
        return state

    # =====================================================
    # MOVES
    # =====================================================

    state = await lichess_node(state)

    # =====================================================
    # EVALUATION
    # =====================================================

    state = await stockfish_node(state)

    # =====================================================
    # OPENING DETECTION
    # =====================================================

    state = opening_detector_node(state)

    # =====================================================
    # RAG
    # =====================================================

    if state.get("opening"):
        state = await rag_node(state)

    # =====================================================
    # VIDEOS
    # =====================================================

    if state.get("opening"):
        state = await video_retriever_node(state)

    # =====================================================
    # FORMAT
    # =====================================================

    state = format_response_node(state)

    return state


# =========================================================
# MAIN RUNNER
# =========================================================

async def run_agent(
    input_data: str,
    mode: WorkflowMode = "moves",
) -> Dict[str, Any]:

    state = create_initial_state()

    # =====================================================
    # MODE INITIALIZATION
    # =====================================================

    if mode in ["moves", "evaluate", "complete"]:

        state["fen"] = input_data

    if mode in ["rag", "videos"]:

        state["opening"] = input_data

    # =====================================================
    # MOVES
    # =====================================================

    if mode == "moves":

        state = await run_moves_workflow(state)

        return format_response_node(state)

    # =====================================================
    # EVALUATION
    # =====================================================

    if mode == "evaluate":

        state = await run_evaluate_workflow(state)

        return format_response_node(state)

    # =====================================================
    # RAG
    # =====================================================

    if mode == "rag":

        state = await run_rag_workflow(state)

        return format_response_node(state)

    # =====================================================
    # VIDEOS
    # =====================================================

    if mode == "videos":

        state = await run_video_workflow(state)

        return format_response_node(state)

    # =====================================================
    # COMPLETE
    # =====================================================

    if mode == "complete":

        return await run_complete_workflow(state)

    # =====================================================
    # INVALID MODE
    # =====================================================

    return {
        "error": f"Unsupported workflow mode: {mode}",
    }
