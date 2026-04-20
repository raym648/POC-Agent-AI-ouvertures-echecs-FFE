# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/core/config.py

"""
Configuration centrale du projet.

Ce module permet de centraliser :
- les variables d'environnement
- les paramètres techniques (API, timeouts, moteurs)
- les constantes globales

Bonne pratique MLOps :
→ éviter le hardcoding dans les services
→ centraliser toute configuration ici
"""

import os


def get_int_env(var_name: str, default: int) -> int:
    try:
        return int(os.getenv(var_name, default))
    except (ValueError, TypeError):
        return default


def get_bool_env(var_name: str, default: bool = False) -> bool:
    return os.getenv(var_name, str(default)).lower() in ("true", "1", "yes")


class Settings:

    # Lichess
    LICHESS_CLOUD_EVAL_URL: str = os.getenv(
        "LICHESS_CLOUD_EVAL_URL",
        "https://lichess.org/api/cloud-eval"
    )

    HTTP_TIMEOUT: int = get_int_env("HTTP_TIMEOUT", 5)

    # Stockfish
    STOCKFISH_PATH: str = os.getenv(
        "STOCKFISH_PATH",
        "/usr/games/stockfish"
    )

    STOCKFISH_DEPTH: int = get_int_env("STOCKFISH_DEPTH", 15)

    # App
    DEBUG: bool = get_bool_env("DEBUG", False)
    APP_NAME: str = os.getenv("APP_NAME", "Chess AI Agent")
    API_VERSION: str = os.getenv("API_VERSION", "v1")

    BACKEND_PORT: int = get_int_env("BACKEND_PORT", 8000)

    # Agent
    ENABLE_AGENT: bool = get_bool_env("ENABLE_AGENT", False)

    # Limits
    MAX_MOVES_RETURNED: int = get_int_env("MAX_MOVES_RETURNED", 5)
    EXTERNAL_API_TIMEOUT: int = get_int_env("EXTERNAL_API_TIMEOUT", 5)


settings = Settings()
