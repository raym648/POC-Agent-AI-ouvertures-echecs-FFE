# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/services/stockfish_service.py

from stockfish import Stockfish


class StockfishService:
    """
    Service d'évaluation avec Stockfish local.
    """

    def __init__(self, path: str, depth: int = 15):
        self.stockfish = Stockfish(path=path)
        self.stockfish.set_depth(depth)

    def evaluate(self, fen: str) -> dict:
        """
        Évalue une position avec Stockfish.

        Args:
            fen (str): position FEN

        Returns:
            dict: évaluation
        """
        self.stockfish.set_fen_position(fen)

        evaluation = self.stockfish.get_evaluation()

        return {
            "type": evaluation["type"],
            "value": evaluation["value"],
            "best_move": self.stockfish.get_best_move()
        }
