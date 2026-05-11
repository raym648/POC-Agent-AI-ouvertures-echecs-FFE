# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/langgraph_agent.py

from typing import Dict, Any, Literal

from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.validate_fen_node import validate_fen_node
from app.agents.lichess_node import lichess_node
from app.agents.stockfish_node import stockfish_node
from app.agents.rag_node import rag_node
from app.agents.video_node import video_retriever_node
from app.agents.format_response_node import format_response_node

# from app.agents.llm_node import llm_node
# from app.agents.opening_detector_node import opening_detector_node


# =========================================================
# TYPES
# =========================================================

WorkflowMode = Literal[
    "moves",
    "evaluate",
    "rag",
    "videos",
]


# =========================================================
# GRAPH BUILDERS
# =========================================================

def build_moves_graph():
    """
    Workflow coups théoriques :

    validate_fen
        -> lichess
            -> format

    Input :
        FEN

    Usage :
        récupération des coups théoriques
        depuis Lichess.
    """

    graph = StateGraph(AgentState)

    # =====================================================
    # NODES
    # =====================================================

    graph.add_node(
        "validate_fen",
        validate_fen_node,
    )

    graph.add_node(
        "lichess",
        lichess_node,
    )

    graph.add_node(
        "format",
        format_response_node,
    )

    # =====================================================
    # ENTRYPOINT
    # =====================================================

    graph.set_entry_point("validate_fen")

    # =====================================================
    # EDGES
    # =====================================================

    graph.add_edge(
        "validate_fen",
        "lichess",
    )

    graph.add_edge(
        "lichess",
        "format",
    )

    graph.add_edge(
        "format",
        END,
    )

    return graph.compile()


def build_evaluate_graph():
    """
    Workflow évaluation moteur :

    validate_fen
        -> stockfish
            -> format

    Input :
        FEN

    Usage :
        analyse moteur Stockfish.
    """

    graph = StateGraph(AgentState)

    # =====================================================
    # NODES
    # =====================================================

    graph.add_node(
        "validate_fen",
        validate_fen_node,
    )

    graph.add_node(
        "stockfish",
        stockfish_node,
    )

    graph.add_node(
        "format",
        format_response_node,
    )

    # =====================================================
    # ENTRYPOINT
    # =====================================================

    graph.set_entry_point("validate_fen")

    # =====================================================
    # EDGES
    # =====================================================

    graph.add_edge(
        "validate_fen",
        "stockfish",
    )

    graph.add_edge(
        "stockfish",
        "format",
    )

    graph.add_edge(
        "format",
        END,
    )

    return graph.compile()


def build_rag_graph():
    """
    Workflow RAG :

    rag
        -> format

    Input :
        nom d'ouverture

    Usage :
        récupération du contexte
        stratégique depuis Milvus.

    IMPORTANT :
        Aucun validate_fen ici.
        Aucun opening_detector ici.

        Le endpoint transmet déjà
        directement une opening name.
    """

    graph = StateGraph(AgentState)

    # =====================================================
    # NODES
    # =====================================================

    graph.add_node(
        "rag",
        rag_node,
    )

    graph.add_node(
        "format",
        format_response_node,
    )

    # =====================================================
    # ENTRYPOINT
    # =====================================================

    graph.set_entry_point("rag")

    # =====================================================
    # EDGES
    # =====================================================

    graph.add_edge(
        "rag",
        "format",
    )

    graph.add_edge(
        "format",
        END,
    )

    return graph.compile()


def build_video_graph():
    """
    Workflow vidéos :

    video_retriever
        -> format

    Input :
        nom d'ouverture

    Usage :
        récupération des vidéos YouTube.

    IMPORTANT :
        Aucun validate_fen ici.
        Aucun opening_detector ici.

        Le endpoint transmet déjà
        directement une opening name.
    """

    graph = StateGraph(AgentState)

    # =====================================================
    # NODES
    # =====================================================

    graph.add_node(
        "video_retriever",
        video_retriever_node,
    )

    graph.add_node(
        "format",
        format_response_node,
    )

    # =====================================================
    # ENTRYPOINT
    # =====================================================

    graph.set_entry_point(
        "video_retriever",
    )

    # =====================================================
    # EDGES
    # =====================================================

    graph.add_edge(
        "video_retriever",
        "format",
    )

    graph.add_edge(
        "format",
        END,
    )

    return graph.compile()


# =========================================================
# GRAPH INSTANCES
# =========================================================

moves_agent = build_moves_graph()

evaluate_agent = build_evaluate_graph()

rag_agent = build_rag_graph()

video_agent = build_video_graph()


# =========================================================
# MAIN RUNNER
# =========================================================

async def run_agent(
    input_data: str,
    mode: WorkflowMode = "moves",
) -> Dict[str, Any]:
    """
    Point d'entrée principal LangGraph.

    Modes disponibles :
        - moves
        - evaluate
        - rag
        - videos

    Inputs :
        - moves/evaluate :
            FEN

        - rag/videos :
            nom d'ouverture
    """

    # =====================================================
    # BASE STATE
    # =====================================================

    state: AgentState = {
        "fen": None,
        "opening": None,
        "is_valid": False,
        "moves": [],
        "evaluation": None,
        "source": None,
        "error": None,
        "rag_context": None,
        "explanation": None,
        "videos": [],
    }

    # =====================================================
    # MODE INITIALIZATION
    # =====================================================

    if mode in ["moves", "evaluate"]:

        state["fen"] = input_data

    if mode in ["rag", "videos"]:

        state["opening"] = input_data

    # =====================================================
    # WORKFLOW SELECTION
    # =====================================================

    if mode == "moves":

        return await moves_agent.ainvoke(state)

    if mode == "evaluate":

        return await evaluate_agent.ainvoke(state)

    if mode == "rag":

        return await rag_agent.ainvoke(state)

    if mode == "videos":

        return await video_agent.ainvoke(state)

    # =====================================================
    # INVALID MODE
    # =====================================================

    return {
        "error": f"Unsupported workflow mode: {mode}",
    }
