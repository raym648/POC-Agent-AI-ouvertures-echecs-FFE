# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/lichess_node.py

from app.agents.state import AgentState
from app.services.lichess_service import LichessService


lichess_service = LichessService()


# =========================================================
# OPENING DETECTION
# =========================================================

def detect_opening(
    moves: list,
) -> str | None:
    """
    Détection simplifiée d'ouverture.

    Basée sur les premiers coups UCI.
    """

    try:

        first_moves = " ".join(
            [
                m.get("move", "")
                for m in moves[:5]
            ]
        )

        first_moves = first_moves.strip()

        # =================================================
        # SICILIAN DEFENSE
        # =================================================

        if "e2e4 c7c5" in first_moves:

            return "Sicilian Defense"

        # =================================================
        # RUY LOPEZ
        # =================================================

        if (
            "e2e4 e7e5 g1f3 b8c6 f1b5"
            in first_moves
        ):

            return "Ruy Lopez"

        # =================================================
        # QUEEN'S GAMBIT
        # =================================================

        if "d2d4 d7d5 c2c4" in first_moves:

            return "Queen's Gambit"

        # =================================================
        # FALLBACK
        # =================================================

        return "Chess Opening Strategy"

    except Exception:

        return None


# =========================================================
# MAIN NODE
# =========================================================

async def lichess_node(
    state: AgentState,
) -> AgentState:
    """
    Node LangGraph Lichess.

    Workflow :
        validate_fen
            -> lichess
                -> opening detection
    """

    # =====================================================
    # VALIDATION
    # =====================================================

    if not state.get("is_valid"):

        return {
            **state,
            "moves": [],
            "error": "Invalid FEN",
        }

    try:

        # =================================================
        # FETCH MOVES
        # =================================================

        moves = await lichess_service.extract_moves(
            state["fen"]
        )

        # =================================================
        # EMPTY RESULT
        # =================================================

        if not moves:

            return {
                **state,
                "moves": [],
                "opening": None,
                "source": None,
            }

        # =================================================
        # OPENING DETECTION
        # =================================================

        opening = detect_opening(moves)

        # =================================================
        # SUCCESS
        # =================================================

        return {
            **state,
            "moves": moves,
            "opening": opening,
            "source": "lichess",
        }

    except Exception as e:

        return {
            **state,
            "moves": [],
            "opening": None,
            "error": str(e),
        }
