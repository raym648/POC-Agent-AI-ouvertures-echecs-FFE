# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/langgraph_agent.py

"""
Agent LangGraph avec :
- Lichess → théorie
- Stockfish → évaluation
- Milvus → RAG
- Hugging Face LLM → explication naturelle
- YouTube → vidéos pédagogiques (NEW)
"""

# ================================
# Imports
# ================================
from typing import TypedDict, Optional, List, Dict, Any

from langgraph.graph import StateGraph, END

from app.services.lichess_service import LichessService
from app.services.stockfish_service import StockfishService
from app.services.fen_validator import validate_fen

# RAG
from app.rag.embedding_service import embedding_service
from app.rag.milvus_service import milvus_service

# 🔥 Hugging Face
from transformers import pipeline

# 🎥 YouTube node
from app.agents.video_node import video_retriever_node

# Config
from app.core.config import settings


# ================================
# Init services
# ================================
lichess_service = LichessService()

stockfish_service = StockfishService(
    path="/usr/games/stockfish",
    depth=15
)

# 🔥 LLM Hugging Face
llm_pipeline = pipeline(
    "text-generation",
    model=settings.HF_MODEL_NAME,
    device=0 if settings.HF_DEVICE == "cuda" else -1,
    max_new_tokens=300,
    temperature=0.4
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

    rag_context: Optional[List[Dict[str, Any]]]

    # 🔥 LLM
    explanation: Optional[str]

    # 🎥 YouTube
    videos: Optional[List[Dict[str, Any]]]
    
    # ♟️ Opening détectée
    opening: Optional[str]


# ================================
# Node 1 — Validation
# ================================
def validate_fen_node(state: AgentState) -> AgentState:
    try:
        is_valid = validate_fen(state["fen"])
        return {
            **state,
            "is_valid": is_valid,
            "error": None if is_valid else "Invalid FEN"
        }
    except Exception as e:
        return {**state, "is_valid": False, "error": str(e)}


# ================================
# Node 2 — Lichess
# ================================
async def lichess_node(state: AgentState) -> AgentState:
    if not state["is_valid"]:
        return state

    try:
        moves = await lichess_service.extract_moves(state["fen"])

        if moves:
            return {**state, "moves": moves, "source": "lichess"}

        return {**state, "moves": [], "source": None}

    except Exception as e:
        return {**state, "moves": [], "error": str(e)}


# ================================
# Node 3 — Stockfish
# ================================
def stockfish_node(state: AgentState) -> AgentState:
    if not state["is_valid"]:
        return state

    if state.get("moves"):
        return state

    try:
        result = stockfish_service.evaluate(state["fen"])
        return {**state, "evaluation": result, "source": "stockfish"}

    except Exception as e:
        return {**state, "error": str(e)}


# ================================
# Node 4 — RAG
# ================================
def rag_node(state: AgentState) -> AgentState:
    if not state["is_valid"]:
        return state

    try:
        if state.get("moves"):
            query = " ".join([m.get("san", "") for m in state["moves"][:3]])
        elif state.get("evaluation"):
            query = f"chess analysis {state['fen']}"
        else:
            query = state["fen"]

        embedding = embedding_service.embed_text(query)

        results = milvus_service.search(
            embedding,
            top_k=settings.RAG_TOP_K
        )

        return {**state, "rag_context": results}

    except Exception as e:
        return {**state, "rag_context": [], "error": str(e)}


# ================================
# 🎥 Node 5 — YouTube Retriever
# ================================
def should_fetch_videos(state: AgentState) -> bool:
    """
    Déclenchement si contexte exploitable.
    """
    return state.get("moves") is not None or state.get("evaluation") is not None  # noqa: E501


# ================================
# 🔥 Node 6 — LLM Hugging Face
# ================================
def llm_node(state: AgentState) -> AgentState:
    if not state["is_valid"]:
        return state

    try:
        moves_text = ""
        if state.get("moves"):
            moves_text = " ".join([m.get("san", "") for m in state["moves"][:5]])  # noqa: E501

        evaluation_text = ""
        if state.get("evaluation"):
            evaluation_text = str(state["evaluation"])

        rag_text = ""
        if state.get("rag_context"):
            rag_text = "\n".join([
                str(doc.get("text", "")) for doc in state["rag_context"]
            ])

        videos_text = ""
        if state.get("videos"):
            videos_text = "\n".join([
                f"- {v['title']} ({v['url']})" for v in state["videos"][:3]
            ])

        prompt = f"""
You are a chess coach.

Explain clearly this position.

FEN:
{state["fen"]}

Moves:
{moves_text}

Evaluation:
{evaluation_text}

Context:
{rag_text}

Relevant videos:
{videos_text}

Give a pedagogical explanation.
"""

        outputs = llm_pipeline(prompt)

        generated_text = outputs[0]["generated_text"]
        explanation = generated_text.replace(prompt, "").strip()

        return {
            **state,
            "explanation": explanation
        }

    except Exception as e:
        return {
            **state,
            "explanation": None,
            "error": f"HF LLM error: {str(e)}"
        }


# ================================
# ♟️ Node 7 — Opening Detector
# ================================
def opening_detector_node(state: AgentState) -> AgentState:
    """
    Détecte l'ouverture d'échecs à partir des moves (Lichess)
    ou fallback heuristique.
    """

    if not state["is_valid"]:
        return state

    try:
        opening = None

        # =========================
        # 1. Cas idéal : Lichess fournit l’ouverture
        # =========================
        if state.get("moves"):
            first_moves = " ".join([m.get("san", "") for m in state["moves"][:3]])  # noqa: E501

            # Heuristique simple (POC)
            if "e4 c5" in first_moves:
                opening = "Sicilian Defense"
            elif "e4 e5 Nf3 Nc6 Bb5" in first_moves:
                opening = "Ruy Lopez"
            elif "d4 d5 c4" in first_moves:
                opening = "Queen's Gambit"

        # =========================
        # 2. Fallback
        # =========================
        if not opening:
            opening = "chess opening strategy"

        return {
            **state,
            "opening": opening
        }

    except Exception as e:
        return {
            **state,
            "opening": None,
            "error": str(e)
        }


# ================================
# Node 7 — Format final
# ================================
def format_response_node(state: AgentState) -> Dict[str, Any]:

    if not state["is_valid"]:
        return {"fen": state["fen"], "error": state["error"]}

    response: Dict[str, Any] = {
        "fen": state["fen"],
        "source": state.get("source"),
    }

    if state.get("moves"):
        response["type"] = "theory"
        response["moves"] = state["moves"]
    else:
        response["type"] = "evaluation"
        response["evaluation"] = state.get("evaluation")

    if state.get("rag_context"):
        response["rag"] = state["rag_context"]

    if state.get("videos"):
        response["videos"] = state["videos"]

    if state.get("explanation"):
        response["explanation"] = state["explanation"]

    return response


# ================================
# Graph
# ================================
def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("validate_fen", validate_fen_node)
    graph.add_node("lichess", lichess_node)
    graph.add_node("stockfish", stockfish_node)
    graph.add_node("rag", rag_node)
    graph.add_node("video_retriever", video_retriever_node)
    graph.add_node("llm", llm_node)
    graph.add_node("format", format_response_node)
    graph.add_node("opening_detector", opening_detector_node)

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
            "stockfish": "stockfish"
        }
    )

    graph.add_edge("stockfish", "rag")
    graph.add_edge("opening_detector", "rag")

    # 🎥 insertion YouTube
    graph.add_conditional_edges(
        "rag",
        should_fetch_videos,
        {
            True: "video_retriever",
            False: "llm"
        }
    )

    graph.add_edge("video_retriever", "llm")

    # 🔥 pipeline final
    graph.add_edge("llm", "format")
    graph.add_edge("format", END)

    return graph.compile()


# ================================
# Instance
# ================================
agent = build_agent()


# ================================
# Run
# ================================
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
