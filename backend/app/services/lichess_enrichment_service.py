# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/services/lichess_enrichment_service.py

class LichessEnrichmentService:
    """
    Mapping simple opening → tags pédagogiques Lichess
    (POC → extensible vers scraping/API plus tard)
    """

    TAG_MAPPING = {
        "Sicilian Defense": ["sicilian defense", "chess opening", "strategy", "attack"],  # noqa: E501
        "Ruy Lopez": ["ruy lopez", "spanish opening", "theory", "positional play"],  # noqa: E501
        "Queen's Gambit": ["queen's gambit", "d4 opening", "strategy", "classic games"]  # noqa: E501
    }

    def enrich_opening(self, opening: str) -> str:
        tags = self.TAG_MAPPING.get(opening, ["chess opening", "strategy"])

        # Construction requête optimisée SEO YouTube
        return f"{opening} {' '.join(tags)} tutorial"
