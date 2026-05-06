# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/langgraph_agent.py

from typing import Dict, Any

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


def should_fetch_videos(state: AgentState) -> bool:
    return state.get("moves") is not None or state.get("evaluation") is not None


def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("validate_fen", validate_fen_node)
    graph.add_node("lichess", lichess_node)
    graph.add_node("stockfish", stockfish_node)
    graph.add_node("rag", rag_node)
    graph.add_node("video_retriever", video_retriever_node)
    graph.add_node("llm", llm_node)
    graph.add_node("opening_detector", opening_detector_node)
    graph.add_node("format", format_response_node)

    graph.set_entry_point("validate_fen")

    graph.add_edge("validate_fen", "lichess")

    def route(state: AgentState):
        if state.get("moves"):
            return "rag"
        return "stockfish"

    graph.add_conditional_edges(
        "lichess",
        route,
        {
            "rag": "opening_detector",
            "stockfish": "stockfish",
        },
    )

    graph.add_edge("stockfish", "rag")
    graph.add_edge("opening_detector", "rag")

    graph.add_conditional_edges(
        "rag",
        should_fetch_videos,
        {
            True: "video_retriever",
            False: "llm",
        },
    )

    graph.add_edge("video_retriever", "llm")
    graph.add_edge("llm", "format")
    graph.add_edge("format", END)

    return graph.compile()


agent = build_agent()


async def run_agent(fen: str) -> Dict[str, Any]:
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

    return await agent.ainvoke(state)
