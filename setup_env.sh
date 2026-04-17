#!/bin/bash

# POC-Agent-AI-ouvertures-echecs-FFE/setup_env.sh

# ================================
# Script de création environnement Python
# ================================

set -e  # stop en cas d'erreur

echo "📦 Création de l'environnement virtuel..."

# Création du venv si non existant
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Environnement virtuel créé"
else
    echo "⚠️ Environnement déjà existant"
fi

# Activation
echo "🔌 Activation de l'environnement..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Mise à jour de pip..."
pip install --upgrade pip

# Vérification présence du fichier requirements
REQUIREMENTS_FILE="backend/requirements.txt"

if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "❌ ERREUR : $REQUIREMENTS_FILE introuvable"
    exit 1
fi

# Installation des dépendances
echo "📚 Installation des dépendances depuis $REQUIREMENTS_FILE..."
pip install -r $REQUIREMENTS_FILE

echo "✅ Environnement prêt !"
echo "👉 Activation manuelle : source .venv/bin/activate"
