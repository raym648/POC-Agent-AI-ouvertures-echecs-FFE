# POC-Agent-AI-ouvertures-echecs-FFE/setup_env.sh
#!/bin/bash

# ================================
# Script de création environnement Python
# ================================

set -e  # stop en cas d'erreur

echo "📦 Création de l'environnement virtuel..."

# Création du venv
python3 -m venv .venv

echo "✅ Environnement virtuel créé"

# Activation
echo "🔌 Activation de l'environnement..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Mise à jour de pip..."
pip install --upgrade pip

# Installation des dépendances
echo "📚 Installation des dépendances..."
pip install -r requirements.txt

echo "✅ Environnement prêt !"
echo "👉 Pour activer manuellement : source .venv/bin/activate"
