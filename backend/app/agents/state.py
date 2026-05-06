# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/state.py

from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict):
    fen: str
    is_valid: bool
    moves: Optional[List[Dict[str, Any]]]
    evaluation: Optional[Dict[str, Any]]
    source: Optional[str]
    error: Optional[str]
    rag_context: Optional[List[Dict[str, Any]]]
    explanation: Optional[str]
    videos: Optional[List[Dict[str, Any]]]
    opening: Optional[str]
