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
    PIP_NO_CACHE_DIR=1

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
# 🔒 Création d’un utilisateur non-root
# ================================
RUN useradd -m appuser
USER appuser

# ================================
# 🌐 Exposition du port
# ================================
EXPOSE 8000

# ================================
# 🚀 Commande de lancement
# ================================
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
