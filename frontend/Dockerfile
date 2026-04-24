# POC-Agent-AI-ouvertures-echecs-FFE/frontend/Dockerfile

# Image Node.js versionnée (reproductibilité)
FROM node:20-alpine

# Répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY package*.json ./

# Installation des dépendances
# Ajout --legacy-peer-deps pour éviter conflits Angular fréquents
RUN npm install --legacy-peer-deps

# Copie du reste du projet
COPY . .

# Exposition du port Angular
EXPOSE 4200

# Variable pour éviter problèmes binding Angular dans Docker
ENV HOST=0.0.0.0

# Commande par défaut
CMD ["npm", "start"]
