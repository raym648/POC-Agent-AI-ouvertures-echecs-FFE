# POC-Agent-AI-ouvertures-echecs-FFE/backend/app/main.py

"""
Point d’entrée principal de l’application FastAPI.

Ce fichier expose :
- un endpoint de healthcheck pour vérifier que l’API fonctionne
- la base pour ajouter des routes futures (IA, Stockfish, etc.)
"""

from fastapi import FastAPI

# Initialisation de l'application FastAPI
# title : nom de l’API visible dans la documentation Swagger
# version : version du service
app = FastAPI(
    title="Chess AI Backend",
    version="1.0.0"
)


# Endpoint de base pour vérifier que l'API est fonctionnelle
@app.get("/api/v1/healthcheck")
def healthcheck():
    """
    Endpoint de vérification de santé du service.

    Returns:
        dict: statut du service
    """
    return {
        "status": "ok"
    }


# Endpoint racine optionnel (utile pour debug rapide)
@app.get("/")
def root():
    """
    Endpoint racine pour vérifier que le serveur répond.
    """
    return {
        "message": "Chess AI Backend is running"
    }
