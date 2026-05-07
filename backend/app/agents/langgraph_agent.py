# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/langgraph_agent.py

from typing import Dict, Any, Literal

from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.validate_fen_node import validate_fen_node
from app.agents.lichess_node import lichess_node
from app.agents.stockfish_node import stockfish_node
from app.agents.rag_node import rag_node
from app.agents.video_node import video_retriever_node
from app.agents.llm_node import llm_node
from app.agents.opening_detector_node import opening_detector_node
from app.agents.format_response_node import format_response_node


# =========================================================
# TYPES
# =========================================================

WorkflowMode = Literal[
    "moves",
    "evaluate",
    "full",
]


# =========================================================
# ROUTING HELPERS
# =========================================================

def should_use_stockfish(state: AgentState) -> str:
    """
    Décide si l'on doit fallback vers Stockfish.

    Si aucun coup théorique n'est trouvé via Lichess,
    alors on passe par Stockfish.
    """

    if state.get("moves"):
        return "has_moves"

    return "no_moves"


def should_fetch_videos(state: AgentState) -> bool:
    """
    Détermine si des vidéos doivent être récupérées.

    On récupère des vidéos uniquement si :
    - une ouverture a été détectée,
    - ou des coups théoriques existent.
    """

    return bool(
        state.get("opening")
        or state.get("moves")
    )


# =========================================================
# GRAPH BUILDERS
# =========================================================

def build_moves_graph():
    """
    Workflow léger :
    validate -> lichess -> format
    """

    graph = StateGraph(AgentState)

    graph.add_node("validate_fen", validate_fen_node)
    graph.add_node("lichess", lichess_node)
    graph.add_node("format", format_response_node)

    graph.set_entry_point("validate_fen")

    graph.add_edge("validate_fen", "lichess")
    graph.add_edge("lichess", "format")
    graph.add_edge("format", END)

    return graph.compile()


def build_evaluate_graph():
    """
    Workflow Stockfish uniquement :
    validate -> stockfish -> format
    """

    graph = StateGraph(AgentState)

    graph.add_node("validate_fen", validate_fen_node)
    graph.add_node("stockfish", stockfish_node)
    graph.add_node("format", format_response_node)

    graph.set_entry_point("validate_fen")

    graph.add_edge("validate_fen", "stockfish")
    graph.add_edge("stockfish", "format")
    graph.add_edge("format", END)

    return graph.compile()


def build_full_graph():
    """
    Workflow IA complet :
    validate
        -> lichess
            -> opening_detector + rag + videos
        -> stockfish fallback
            -> rag
    """

    graph = StateGraph(AgentState)

    # =====================================================
    # NODES
    # =====================================================

    graph.add_node("validate_fen", validate_fen_node)
    graph.add_node("lichess", lichess_node)
    graph.add_node("stockfish", stockfish_node)
    graph.add_node("opening_detector", opening_detector_node)
    graph.add_node("rag", rag_node)
    graph.add_node("video_retriever", video_retriever_node)
    graph.add_node("llm", llm_node)
    graph.add_node("format", format_response_node)

    # =====================================================
    # ENTRYPOINT
    # =====================================================

    graph.set_entry_point("validate_fen")

    # =====================================================
    # VALIDATION
    # =====================================================

    graph.add_edge("validate_fen", "lichess")

    # =====================================================
    # ROUTING LICHESS -> STOCKFISH
    # =====================================================

    graph.add_conditional_edges(
        "lichess",
        should_use_stockfish,
        {
            "has_moves": "opening_detector",
            "no_moves": "stockfish",
        },
    )

    # =====================================================
    # OPENING DETECTION
    # =====================================================

    graph.add_edge("opening_detector", "rag")

    # =====================================================
    # STOCKFISH FALLBACK
    # =====================================================

    graph.add_edge("stockfish", "rag")

    # =====================================================
    # RAG -> VIDEOS / LLM
    # =====================================================

    graph.add_conditional_edges(
        "rag",
        should_fetch_videos,
        {
            True: "video_retriever",
            False: "llm",
        },
    )

    # =====================================================
    # VIDEOS -> LLM
    # =====================================================

    graph.add_edge("video_retriever", "llm")

    # =====================================================
    # FINAL FORMAT
    # =====================================================

    graph.add_edge("llm", "format")
    graph.add_edge("format", END)

    return graph.compile()


# =========================================================
# GRAPH INSTANCES
# =========================================================

moves_agent = build_moves_graph()

evaluate_agent = build_evaluate_graph()

full_agent = build_full_graph()


# =========================================================
# MAIN RUNNER
# =========================================================

async def run_agent(
    fen: str,
    mode: WorkflowMode = "full",
) -> Dict[str, Any]:
    """
    Point d'entrée unique LangGraph.

    Modes disponibles :
    - moves
    - evaluate
    - full
    """

    state: AgentState = {
        "fen": fen,
        "is_valid": False,
        "moves": None,
        "evaluation": None,
        "source": None,
        "error": None,
        "rag_context": None,
        "explanation": None,
        "videos": None,
        "opening": None,
    }

    # =====================================================
    # WORKFLOW SELECTION
    # =====================================================

    if mode == "moves":
        return await moves_agent.ainvoke(state)

    if mode == "evaluate":
        return await evaluate_agent.ainvoke(state)

    return await full_agent.ainvoke(state)
