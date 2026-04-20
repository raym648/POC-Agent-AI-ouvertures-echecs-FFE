# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/services/lichess_service.py

import httpx
from typing import List, Dict


class LichessService:
    """
    Service d'accès à l'API Lichess Cloud Evaluation.
    """

    BASE_URL = "https://lichess.org/api/cloud-eval"

    async def get_cloud_evaluation(self, fen: str) -> Dict:
        """
        Récupère l'évaluation cloud depuis Lichess.

        Args:
            fen (str): position FEN

        Returns:
            dict: réponse JSON
        """
        params = {"fen": fen}

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(self.BASE_URL, params=params)

            # Gestion des erreurs HTTP
            if response.status_code != 200:
                return {}

            return response.json()

    async def extract_moves(self, fen: str) -> List[Dict]:
        """
        Extrait les meilleurs coups depuis les PVs Lichess.

        Args:
            fen (str): position FEN

        Returns:
            List[Dict]: liste de coups
        """
        data = await self.get_cloud_evaluation(fen)

        if not data or "pvs" not in data:
            return []

        moves = []

        for pv in data["pvs"]:
            first_move = pv["moves"].split()[0]

            moves.append({
                "move": first_move,
                "evaluation": pv.get("cp", 0)
            })

        return moves
