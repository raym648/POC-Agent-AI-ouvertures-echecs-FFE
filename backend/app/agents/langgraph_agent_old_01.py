# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/langgraph_agent.py

"""
Agent LangGraph pour l'analyse de positions d'échecs.

Ce module implémente un graphe décisionnel permettant :
1. De valider une position FEN
2. D'interroger Lichess (base d'ouvertures)
3. Si aucun résultat → fallback vers Stockfish
4. Retourner une réponse structurée

Architecture :
Lichess = mémoire (théorie)
Stockfish = raisonnement (calcul)
"""


# ================================
# Imports
# ================================
from typing import TypedDict, Optional, List, Dict, Any

from langgraph.graph import StateGraph, END

# Services métier
from app.services.lichess_service import LichessService
from app.services.stockfish_service import StockfishService

# Validation FEN
from app.services.fen_validator import validate_fen

# 🔥 RAG (Milvus)
from app.rag.embedding_service import embedding_service
from app.rag.milvus_service import milvus_service
from app.core.config import settings


# ================================
# Initialisation des services
# ================================

lichess_service = LichessService()

# ⚠️ Adapter le path selon ton Docker
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
    rag_context: Optional[List[Dict[str, Any]]]    # 🔥 RAG (Milvus)


# ================================
# Node 1 — Validation
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
        else:
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
# Node 3 — Stockfish
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
# Node 4 — Format réponse
# ================================
def format_response_node(state: AgentState) -> Dict[str, Any]:

    if not state["is_valid"]:
        return {
            "fen": state["fen"],
            "error": state["error"]
        }

    response = {
        "fen": state["fen"],
        "source": state.get("source"),
    }

    if state.get("moves"):
        response.update({
            "type": "theory",
            "moves": state["moves"]
        })
    else:
        response.update({
            "type": "evaluation",
            "evaluation": state.get("evaluation")
        })

    # 🔥 AJOUT RAG
    if state.get("rag_context"):
        response["explanations"] = state["rag_context"]

    return response


# ================================
# Node 5 — RAG (Milvus)
# ================================
def rag_node(state: AgentState) -> AgentState:
    """
    Enrichissement via recherche vectorielle (Milvus).
    """

    if not state["is_valid"]:
        return state

    try:
        # 🔎 Construction de la requête intelligente
        if state.get("moves"):
            # Cas Lichess → on enrichit avec ouverture
            query = " ".join([m.get("san", "") for m in state["moves"][:3]])
        elif state.get("evaluation"):
            # Cas Stockfish → contexte stratégique
            query = f"chess position evaluation {state['fen']}"
        else:
            query = state["fen"]

        # Embedding
        query_embedding = embedding_service.embed_text(query)

        # Recherche Milvus
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
# Graph
# ================================
def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("validate_fen", validate_fen_node)
    graph.add_node("lichess", lichess_node)
    graph.add_node("stockfish", stockfish_node)

    # 🔥 NEW
    graph.add_node("rag", rag_node)

    graph.add_node("format_response", format_response_node)

    graph.set_entry_point("validate_fen")

    graph.add_edge("validate_fen", "lichess")

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

    # 🔥 Stockfish → RAG aussi
    graph.add_edge("stockfish", "rag")

    # 🔥 RAG → réponse finale
    graph.add_edge("rag", "format_response")

    graph.add_edge("format_response", END)

    return graph.compile()


# ================================
# Instance globale
# ================================
agent = build_agent()


# ================================
# Run (async-safe)
# ================================
async def run_agent(fen: str) -> Dict[str, Any]:
    initial_state: AgentState = {
        "fen": fen,
        "is_valid": False,
        "moves": None,
        "evaluation": None,
        "source": None,
        "error": None
    }

    # ✅ FIX critique : async invoke
    return await agent.ainvoke(initial_state)
