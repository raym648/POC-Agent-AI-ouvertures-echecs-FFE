# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/llm_node.py

from transformers import pipeline

from app.agents.state import AgentState
from app.core.config import settings


llm_pipeline = pipeline(
    "text-generation",
    model=settings.HF_MODEL_NAME,
    device=0 if settings.HF_DEVICE == "cuda" else -1,
    max_new_tokens=300,
    temperature=0.4,
)


def llm_node(state: AgentState) -> AgentState:
    if not state["is_valid"]:
        return state

    try:
        moves_text = ""
        if state.get("moves"):
            moves_text = " ".join([m.get("san", "") for m in state["moves"][:5]])

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
            "explanation": explanation,
        }

    except Exception as e:
        return {
            **state,
            "explanation": None,
            "error": f"HF LLM error: {str(e)}",
        }
