# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/state.py

from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict, total=False):
    """
    État partagé LangGraph.

    Architecture refactorée :
    - workflows FEN :
        moves
        evaluate

    - workflows opening :
        rag
        videos

    Les champs sont donc optionnels
    selon le workflow exécuté.
    """

    # =====================================================
    # INPUTS
    # =====================================================

    fen: Optional[str]

    opening: Optional[str]

    # =====================================================
    # VALIDATION
    # =====================================================

    is_valid: bool

    error: Optional[str]

    # =====================================================
    # MOVES
    # =====================================================

    moves: Optional[List[Dict[str, Any]]]

    # =====================================================
    # STOCKFISH
    # =====================================================

    evaluation: Optional[Dict[str, Any]]

    # =====================================================
    # RAG
    # =====================================================

    rag_context: Optional[List[Dict[str, Any]]]

    # =====================================================
    # VIDEOS
    # =====================================================

    videos: Optional[List[Dict[str, Any]]]

    # =====================================================
    # EXPLANATION
    # =====================================================

    explanation: Optional[str]

    # =====================================================
    # METADATA
    # =====================================================

    source: Optional[str]
