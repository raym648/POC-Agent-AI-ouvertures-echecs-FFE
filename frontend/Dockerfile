# POC-Agent-AI-ouvertures-echecs-FFE/frontend/Dockerfile

# Image Node.js versionnée (reproductibilité)
FROM node:20-alpine

# Répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY package*.json ./

# Installation des dépendances
RUN npm install

# Copie du reste du projet
COPY . .

# Exposition du port Angular
EXPOSE 4200

# Commande par défaut
CMD ["npm", "start"]
