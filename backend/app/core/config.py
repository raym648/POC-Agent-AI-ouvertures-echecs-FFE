# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/core/config.py

"""
Configuration centrale du projet.

Ce module centralise :
- les variables d'environnement
- les paramètres techniques (API, timeouts, moteurs)
- les constantes globales

Bonne pratique MLOps :
- éviter le hardcoding dans les services
- centraliser toute configuration ici
- garantir un contrat de configuration explicite et stable
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
    
    # ================================
    # ♟️ LICHESS
    # ================================
    LICHESS_CLOUD_EVAL_URL: str = os.getenv(
        "LICHESS_CLOUD_EVAL_URL",
        "https://lichess.org/api/cloud-eval",
    )

    HTTP_TIMEOUT: int = get_int_env("HTTP_TIMEOUT", 5)

    # ================================
    # ♟️ STOCKFISH
    # ================================
    STOCKFISH_PATH: str = os.getenv(
        "STOCKFISH_PATH",
        "/usr/games/stockfish",
    )

    STOCKFISH_DEPTH: int = get_int_env("STOCKFISH_DEPTH", 15)
    STOCKFISH_HOST: str = os.getenv("STOCKFISH_HOST", "")
    STOCKFISH_PORT: str = os.getenv("STOCKFISH_PORT", "stdin")

    # ================================
    # 🗄️ MONGODB
    # ================================
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "chess_db")

    # ================================
    # 🔎 MILVUS
    # ================================
    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "milvus")
    MILVUS_PORT: int = get_int_env("MILVUS_PORT", 19530)

    # ================================
    # 🧠 EMBEDDINGS / RAG
    # ================================
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )

    VECTOR_COLLECTION_NAME: str = os.getenv(
        "VECTOR_COLLECTION_NAME",
        "chess_openings",
    )

    VECTOR_DIMENSION: int = get_int_env("VECTOR_DIMENSION", 384)
    RAG_TOP_K: int = get_int_env("RAG_TOP_K", 3)

    # ================================
    # 🤖 HUGGING FACE LLM
    # ================================
    HF_MODEL_NAME: str = os.getenv(
        "HF_MODEL_NAME",
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    )

    HF_DEVICE: str = os.getenv("HF_DEVICE", "cpu")

    # ================================
    # 🌐 BACKEND INTERNAL URL
    # ================================
    BACKEND_INTERNAL_URL: str = os.getenv(
        "BACKEND_INTERNAL_URL",
        "http://backend:8000",
    )
    
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:4200",
    ]

    # ================================
    # ⚙️ APPLICATION
    # ================================
    DEBUG: bool = get_bool_env("DEBUG", False)
    APP_NAME: str = os.getenv("APP_NAME", "Chess AI Agent")
    API_VERSION: str = os.getenv("API_VERSION", "v1")
    BACKEND_PORT: int = get_int_env("BACKEND_PORT", 8000)
    ENV: str = os.getenv("ENV", "development")

    # ================================
    # 🤖 AGENT
    # ================================
    ENABLE_AGENT: bool = get_bool_env("ENABLE_AGENT", False)

    # ================================
    # 📊 LIMITES
    # ================================
    MAX_MOVES_RETURNED: int = get_int_env("MAX_MOVES_RETURNED", 5)
    EXTERNAL_API_TIMEOUT: int = get_int_env("EXTERNAL_API_TIMEOUT", 5)


settings = Settings()
