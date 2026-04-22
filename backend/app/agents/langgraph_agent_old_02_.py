# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/langgraph_agent.py

"""
Agent LangGraph pour l'analyse de positions d'échecs enrichi avec RAG.

Architecture :
- Lichess → théorie (ouvertures)
- Stockfish → évaluation (calcul)
- Milvus (RAG) → explication pédagogique

Pipeline :
FEN → Validation → Lichess → (Stockfish fallback) → RAG → Réponse enrichie
"""

# ================================
# Imports
# ================================
from typing import TypedDict, Optional, List, Dict, Any

from langgraph.graph import StateGraph, END

# Services métier
from app.services.lichess_service import LichessService
from app.services.stockfish_service import StockfishService
from app.services.fen_validator import validate_fen

# 🔥 RAG
from app.rag.embedding_service import embedding_service
from app.rag.milvus_service import milvus_service
from app.core.config import settings


# ================================
# Initialisation des services
# ================================
lichess_service = LichessService()

stockfish_service = StockfishService(
    path="/usr/games/stockfish",
    depth=15
)


# ================================
# State
# ================================
class AgentState(TypedDict):
    fen: str
    is_valid: bool
    moves: Optional[List[Dict[str, Any]]]
    evaluation: Optional[Dict[str, Any]]
    source: Optional[str]
    error: Optional[str]

    # 🔥 RAG
    rag_context: Optional[List[Dict[str, Any]]]


# ================================
# Node 1 — Validation FEN
# ================================
def validate_fen_node(state: AgentState) -> AgentState:
    fen = state["fen"]

    try:
        is_valid = validate_fen(fen)
        return {
            **state,
            "is_valid": is_valid,
            "error": None if is_valid else "Invalid FEN"
        }
    except Exception as e:
        return {
            **state,
            "is_valid": False,
            "error": str(e)
        }


# ================================
# Node 2 — Lichess (async)
# ================================
async def lichess_node(state: AgentState) -> AgentState:
    if not state["is_valid"]:
        return state

    fen = state["fen"]

    try:
        moves = await lichess_service.extract_moves(fen)

        if moves:
            return {
                **state,
                "moves": moves,
                "source": "lichess"
            }

        return {
            **state,
            "moves": [],
            "source": None
        }

    except Exception as e:
        return {
            **state,
            "moves": [],
            "error": f"Lichess error: {str(e)}"
        }


# ================================
# Node 3 — Stockfish (fallback)
# ================================
def stockfish_node(state: AgentState) -> AgentState:
    if not state["is_valid"]:
        return state

    if state.get("moves"):
        return state

    fen = state["fen"]

    try:
        result = stockfish_service.evaluate(fen)

        return {
            **state,
            "evaluation": result,
            "source": "stockfish"
        }

    except Exception as e:
        return {
            **state,
            "error": f"Stockfish error: {str(e)}"
        }


# ================================
# Node 4 — RAG (Milvus)
# ================================
def rag_node(state: AgentState) -> AgentState:
    """
    Enrichit la réponse avec un contexte sémantique via Milvus.
    """

    if not state["is_valid"]:
        return state

    try:
        # 🧠 Construction intelligente de la requête
        if state.get("moves"):
            # Cas ouverture (Lichess)
            query = " ".join([m.get("san", "") for m in state["moves"][:3]])

        elif state.get("evaluation"):
            # Cas Stockfish
            query = f"chess position analysis {state['fen']}"

        else:
            query = state["fen"]

        # 🔢 Embedding
        query_embedding = embedding_service.embed_text(query)

        # 🔍 Recherche vectorielle
        results = milvus_service.search(
            query_embedding,
            top_k=settings.RAG_TOP_K
        )

        return {
            **state,
            "rag_context": results
        }

    except Exception as e:
        return {
            **state,
            "rag_context": [],
            "error": f"RAG error: {str(e)}"
        }


# ================================
# Node 5 — Format final
# ================================
def format_response_node(state: AgentState) -> Dict[str, Any]:

    if not state["is_valid"]:
        return {
            "fen": state["fen"],
            "error": state["error"]
        }

    response: Dict[str, Any] = {
        "fen": state["fen"],
        "source": state.get("source"),
    }

    # 🎯 Cas théorie (Lichess)
    if state.get("moves"):
        response.update({
            "type": "theory",
            "moves": state["moves"]
        })

    # 🎯 Cas calcul (Stockfish)
    else:
        response.update({
            "type": "evaluation",
            "evaluation": state.get("evaluation")
        })

    # 🧠 Ajout RAG
    if state.get("rag_context"):
        response["explanations"] = state["rag_context"]

    return response


# ================================
# Graph LangGraph
# ================================
def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("validate_fen", validate_fen_node)
    graph.add_node("lichess", lichess_node)
    graph.add_node("stockfish", stockfish_node)
    graph.add_node("rag", rag_node)
    graph.add_node("format_response", format_response_node)

    graph.set_entry_point("validate_fen")

    graph.add_edge("validate_fen", "lichess")

    # 🔀 Routing intelligent
    def route_after_lichess(state: AgentState):
        if state.get("moves"):
            return "rag"
        return "stockfish"

    graph.add_conditional_edges(
        "lichess",
        route_after_lichess,
        {
            "rag": "rag",
            "stockfish": "stockfish"
        }
    )

    # 🔁 Stockfish → RAG
    graph.add_edge("stockfish", "rag")

    # 🔚 RAG → réponse finale
    graph.add_edge("rag", "format_response")
    graph.add_edge("format_response", END)

    return graph.compile()


# ================================
# Instance globale
# ================================
agent = build_agent()


# ================================
# Exécution async
# ================================
async def run_agent(fen: str) -> Dict[str, Any]:
    """
    Point d'entrée principal de l'agent.
    Compatible FastAPI (async).
    """

    initial_state: AgentState = {
        "fen": fen,
        "is_valid": False,
        "moves": None,
        "evaluation": None,
        "source": None,
        "error": None,
        "rag_context": None
    }

    return await agent.ainvoke(initial_state)
