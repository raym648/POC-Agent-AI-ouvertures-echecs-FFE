# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/services/stockfish_service.py

from stockfish import Stockfish
from app.core.config import settings


class StockfishService:
    """
    Service d'évaluation avec Stockfish.

    Supporte :
    - mode local (binaire)
    - préparation future mode service (Docker)
    """

    def __init__(self, path: str = None, depth: int = None):

        # ================================
        # 🔧 Configuration dynamique
        # ================================
        self.path = path or settings.STOCKFISH_PATH
        self.depth = depth or settings.STOCKFISH_DEPTH

        # ================================
        # ⚠️ Initialisation sécurisée
        # ================================
        try:
            self.stockfish = Stockfish(path=self.path)
            self.stockfish.set_depth(self.depth)
        except Exception as e:
            raise RuntimeError(
                f"[StockfishService] Failed to initialize Stockfish: {e}"
            )

    def evaluate(self, fen: str) -> dict:
        """
        Évalue une position avec Stockfish.

        Args:
            fen (str): position FEN

        Returns:
            dict: évaluation enrichie
        """

        # ================================
        # 🧪 Validation minimale
        # ================================
        if not fen or not isinstance(fen, str):
            raise ValueError("Invalid FEN provided")

        try:
            # Charger position
            self.stockfish.set_fen_position(fen)

            # Récupérer évaluation brute
            evaluation = self.stockfish.get_evaluation()

            # Meilleur coup
            best_move = self.stockfish.get_best_move()

            return {
                "type": evaluation.get("type"),
                "value": evaluation.get("value"),
                "best_move": best_move,
                "depth": self.depth  # 👉 utile pour debug / UI
            }

        except Exception as e:
            return {
                "error": str(e),
                "type": None,
                "value": None,
                "best_move": None
            }
