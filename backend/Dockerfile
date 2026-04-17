# POC-Agent-AI-ouvertures-echecs-FFE/backend/Dockerfile

# Image Python légère et stable
FROM python:3.11-slim

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

# Copie du fichier des dépendances
COPY requirements.txt .

# Installation des dépendances
# --no-cache-dir : évite de stocker les caches → image plus légère
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source dans le conteneur
COPY . .

# Exposition du port interne du conteneur
EXPOSE 8000

# Commande de lancement de l'application
# uvicorn lance le serveur FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
