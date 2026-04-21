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
        board = chess.Board(fen)  # tentative de création d’un plateau

        # Vérifications supplémentaires
        if not board.is_valid():
            return False

        # Vérifie qu'il y a exactement 2 rois
        if len(board.pieces(chess.KING, chess.WHITE)) != 1:
            return False
        if len(board.pieces(chess.KING, chess.BLACK)) != 1:
            return False

        return True

    except ValueError:
        return False
