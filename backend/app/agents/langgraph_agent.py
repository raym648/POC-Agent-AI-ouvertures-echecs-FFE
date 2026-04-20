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

# LangGraph
from langgraph.graph import StateGraph, END

# Services métier
from app.services.lichess_service import get_lichess_moves
from app.services.stockfish_service import evaluate_position

# Validation FEN
from app.services.fen_validator import validate_fen


# ================================
# Définition de l'état du graphe
# ================================
class AgentState(TypedDict):
    """
    Représente l'état partagé entre les nœuds du graphe.
    """
    fen: str
    is_valid: bool
    moves: Optional[List[Dict[str, Any]]]
    evaluation: Optional[float]
    source: Optional[str]  # "lichess" ou "stockfish"
    error: Optional[str]


# ================================
# Node 1 — Validation FEN
# ================================
def validate_fen_node(state: AgentState) -> AgentState:
    """
    Vérifie si le FEN est valide.
    """
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
# Node 2 — Appel Lichess
# ================================
def lichess_node(state: AgentState) -> AgentState:
    """
    Interroge l'API Lichess pour récupérer les coups théoriques.
    """
    if not state["is_valid"]:
        return state

    fen = state["fen"]

    try:
        moves = get_lichess_moves(fen)

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
        # Gestion robuste : fallback vers Stockfish
        return {
            **state,
            "moves": [],
            "error": f"Lichess error: {str(e)}"
        }


# ================================
# Node 3 — Stockfish fallback
# ================================
def stockfish_node(state: AgentState) -> AgentState:
    """
    Évalue la position avec Stockfish si Lichess n'a rien retourné.
    """
    if not state["is_valid"]:
        return state

    # Si déjà trouvé via Lichess → pas besoin de Stockfish
    if state.get("moves"):
        return state

    fen = state["fen"]

    try:
        evaluation = evaluate_position(fen)

        return {
            **state,
            "evaluation": evaluation,
            "source": "stockfish"
        }

    except Exception as e:
        return {
            **state,
            "error": f"Stockfish error: {str(e)}"
        }


# ================================
# Node 4 — Formatage réponse finale
# ================================
def format_response_node(state: AgentState) -> Dict[str, Any]:
    """
    Formate la réponse finale retournée par l'agent.
    """
    if not state["is_valid"]:
        return {
            "fen": state["fen"],
            "error": state["error"]
        }

    # Cas 1 : coups théoriques trouvés
    if state.get("moves"):
        return {
            "fen": state["fen"],
            "type": "theory",
            "source": "lichess",
            "moves": state["moves"]
        }

    # Cas 2 : fallback Stockfish
    return {
        "fen": state["fen"],
        "type": "evaluation",
        "source": "stockfish",
        "evaluation": state.get("evaluation")
    }


# ================================
# Construction du graphe LangGraph
# ================================
def build_agent():
    """
    Construit et compile le graphe LangGraph.
    """

    # Initialisation du graphe avec le state
    graph = StateGraph(AgentState)

    # Ajout des nodes
    graph.add_node("validate_fen", validate_fen_node)
    graph.add_node("lichess", lichess_node)
    graph.add_node("stockfish", stockfish_node)
    graph.add_node("format_response", format_response_node)

    # ================================
    # Définition du flux
    # ================================

    # Entry point
    graph.set_entry_point("validate_fen")

    # Validation → Lichess
    graph.add_edge("validate_fen", "lichess")

    # Lichess → condition
    def route_after_lichess(state: AgentState):
        """
        Si moves trouvés → format
        Sinon → Stockfish
        """
        if state.get("moves"):
            return "format_response"
        return "stockfish"

    graph.add_conditional_edges(
        "lichess",
        route_after_lichess,
        {
            "format_response": "format_response",
            "stockfish": "stockfish"
        }
    )

    # Stockfish → format
    graph.add_edge("stockfish", "format_response")

    # Fin
    graph.add_edge("format_response", END)

    # Compilation
    return graph.compile()


# ================================
# Instance globale de l'agent
# ================================
agent = build_agent()


# ================================
# Fonction utilitaire principale
# ================================
def run_agent(fen: str) -> Dict[str, Any]:
    """
    Fonction principale pour exécuter l'agent.

    Args:
        fen (str): Position d'échecs au format FEN

    Returns:
        Dict: Résultat structuré (moves ou évaluation)
    """

    initial_state: AgentState = {
        "fen": fen,
        "is_valid": False,
        "moves": None,
        "evaluation": None,
        "source": None,
        "error": None
    }

    # Invocation du graphe
    result = agent.invoke(initial_state)

    return result
