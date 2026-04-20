# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/services/fen_validator.py

# Utilitaire de validation FEN avec python-chess

import chess


def validate_fen(fen: str) -> bool:
    """
    Vérifie si une position FEN est valide.

    Args:
        fen (str): chaîne FEN

    Returns:
        bool: True si valide, sinon False
    """
    try:
        chess.Board(fen)  # tentative de création d’un plateau
        return True
    except ValueError:
        return False
