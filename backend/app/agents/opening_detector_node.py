# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/opening_detector_node.py

from app.agents.state import AgentState


def opening_detector_node(state: AgentState) -> AgentState:
    """
    Détecte une ouverture d'échecs à partir
    des premiers coups retournés par Lichess.

    IMPORTANT :
    Les moves Lichess sont au format :

    {
        "move": "e2e4",
        "evaluation": 19
    }

    et NON au format SAN.
    """

    if not state.get("is_valid"):
        return state

    try:

        opening = None

        moves = state.get("moves") or []

        if moves:

            first_moves = [
                move.get("move", "").lower()
                for move in moves[:5]
            ]

            joined_moves = " ".join(first_moves)

            # =====================================================
            # SICILIAN DEFENSE
            # =====================================================

            if any("c7c5" in move for move in first_moves):
                opening = "sicilian defense"

            # =====================================================
            # KING'S PAWN GAME
            # =====================================================

            elif any("e2e4" in move for move in first_moves):
                opening = "king pawn opening"

            # =====================================================
            # QUEEN'S GAMBIT
            # =====================================================

            elif any("d2d4" in move for move in first_moves):
                opening = "queen's gambit"

            # =====================================================
            # FALLBACK
            # =====================================================

        if not opening:
            opening = "chess opening strategy"

        return {
            **state,
            "opening": opening,
        }

    except Exception as e:

        return {
            **state,
            "opening": "chess opening strategy",
            "error": str(e),
        }
