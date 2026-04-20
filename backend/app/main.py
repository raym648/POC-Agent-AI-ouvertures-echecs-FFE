# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/main.py

"""
Point d’entrée principal de l’application FastAPI.

Ce fichier expose :
- un endpoint de healthcheck pour vérifier que l’API fonctionne
- la base pour ajouter des routes futures (IA, Stockfish, etc.)
"""


from fastapi import FastAPI

# Import des routes
from app.api.v1 import moves, evaluate, agent


# Initialisation de l'application FastAPI
# title : nom de l’API visible dans la documentation Swagger
# version : version du service
app = FastAPI(
    title="Agent IA Échecs",
    version="1.0.0",
    description="API d'analyse d'échecs basée sur Lichess + Stockfish + LangGraph"  # noqa: E501
)

# Enregistrement des routes
app.include_router(moves.router, prefix="/api/v1")
app.include_router(evaluate.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")


# Endpoint de base pour vérifier que l'API est fonctionnelle
@app.get("/api/v1/healthcheck")
def healthcheck():
    """
    Endpoint de vérification de santé du service.

    Returns:
        dict: statut du service
    """
    return {"status": "ok"}


# Endpoint racine (utile pour debug rapide)
@app.get("/")
def root():
    """
    Endpoint racine pour vérifier que le serveur répond.
    """
    return {
        "message": "API Agent IA Échecs opérationnelle"
    }
