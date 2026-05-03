# POC-Agent-AI-ouvertures-echecs-FFE/backend/Dockerfile


# ================================
# 🐍 Base image légère Python
# ================================
FROM python:3.11-slim

# ================================
# ⚙️ Variables d'environnement
# ================================
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    TRANSFORMERS_CACHE=/app/cache \
    HF_HOME=/app/cache

# ================================
# 📁 Working directory
# ================================
WORKDIR /app

# ================================
# 🔧 Installation des dépendances système
# ================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    stockfish \
    gcc \
    g++ \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ================================
# 📦 Installation des dépendances Python
# ================================
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ================================
# 📁 Copie du code source
# ================================
COPY . .

# ================================
# 📦 Préchargement modèle embedding
# ================================
# Évite un téléchargement runtime au 1er appel
RUN mkdir -p /app/cache && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# ================================
# 🔒 Création d’un utilisateur non-root
# ================================
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

# ================================
# 🌐 Exposition du port
# ================================
EXPOSE 8000

# ================================
# ❤️ Healthcheck
# ================================
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/docs || exit 1

# ================================
# 🚀 Commande de lancement
# ================================
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
