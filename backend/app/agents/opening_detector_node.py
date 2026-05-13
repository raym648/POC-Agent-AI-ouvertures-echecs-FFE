# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/agents/opening_detector_node.py

import logging

from app.agents.state import AgentState


logger = logging.getLogger(__name__)


def opening_detector_node(state: AgentState) -> AgentState:
    """
    Détection simplifiée d'ouverture d'échecs
    basée principalement sur la FEN.

    IMPORTANT :
    Les moves Lichess représentent souvent
    des réponses candidates et NON
    l'historique réel des coups joués.

    Donc :
    - la FEN est la source de vérité
    - les moves servent uniquement
      d'enrichissement secondaire
    """

    logger.info(
        "[OPENING NODE] Starting opening detection"
    )

    # =====================================================
    # VALIDATION
    # =====================================================

    if not state.get("is_valid"):

        logger.warning(
            "[OPENING NODE] Invalid state"
        )

        return state

    try:

        fen = (
            state.get("fen", "")
            .lower()
            .strip()
        )

        moves = state.get("moves", [])

        logger.info(
            f"[OPENING NODE] fen={fen}"
        )

        logger.info(
            f"[OPENING NODE] moves={moves}"
        )

        opening = "chess opening strategy"

        # =====================================================
        # KING PAWN OPENING
        # =====================================================

        # pion blanc avancé vers e4/e3

        if "4p3" in fen:

            opening = "king pawn opening"

            logger.info(
                "[OPENING NODE] Matched king pawn opening"
            )

        # =====================================================
        # QUEEN PAWN OPENING
        # =====================================================

        elif "3p4" in fen:

            opening = "queen pawn opening"

            logger.info(
                "[OPENING NODE] Matched queen pawn opening"
            )

        # =====================================================
        # ENGLISH OPENING
        # =====================================================

        elif "2p5" in fen:

            opening = "english opening"

            logger.info(
                "[OPENING NODE] Matched english opening"
            )

        # =====================================================
        # SICILIAN DEFENSE
        # =====================================================

        elif any(
            move.get("move") == "c7c5"
            for move in moves
        ):

            opening = "sicilian defense"

            logger.info(
                "[OPENING NODE] Matched sicilian defense"
            )

        # =====================================================
        # FRENCH DEFENSE
        # =====================================================

        elif any(
            move.get("move") == "e7e6"
            for move in moves
        ):

            opening = "french defense"

            logger.info(
                "[OPENING NODE] Matched french defense"
            )

        # =====================================================
        # CARO-KANN DEFENSE
        # =====================================================

        elif any(
            move.get("move") == "c7c6"
            for move in moves
        ):

            opening = "caro-kann defense"

            logger.info(
                "[OPENING NODE] Matched caro-kann defense"
            )

        # =====================================================
        # FINAL RESULT
        # =====================================================

        logger.info(
            f"[OPENING NODE] Final opening={opening}"
        )

        return {
            **state,
            "opening": opening,
        }

    except Exception as e:

        logger.exception(
            f"[OPENING NODE] Unexpected error: {e}"
        )

        return {
            **state,
            "opening": "chess opening strategy",
            "error": str(e),
        }
