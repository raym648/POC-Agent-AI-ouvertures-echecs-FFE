# ♟️ Projet 13 - Mettez en place un Agent IA

**Mission - Développez un agent IA avec LandGraph pour l'apprentissage des échecs**

✍️ **Auteur :** *[Raymond Francius]*    
📚 **Rôle :** *[Apprenant - Promotion Sept-2025]* — **Engineer AI** — **Openclassrooms**   
🗓️ **Date de mise à jour :** *[20-04-2026]*  

---

## 📌 Contexte
La FFE souhaite, en vue des championnats d’Europe, disposer d’un **agent intelligent** permettant aux jeunes espoirs de s’entraîner sur les ouvertures.  

L’agent IA devra guider les jeunes espoirs en :  
- leur proposant les meilleurs coups issus de la théorie,  
- le contexte des ouvertures via des données enrichies par les parties historiques,  
- des vidéos explicatives pertinentes,  
- et une évaluation de la position par un moteur spécialisé (exemple Stockfish) si la partie s’écarte des sentiers battus.  

---

## 🧱 Stack technique
- FastAPI (backend)  
- Angular (frontend)  
- Docker / Docker Compose  
- Milvus (vector DB)  
- MongoDB (stockage)  
- LandGraph (orchestration)  

---

## 🚀 Lancement du projet

### 1. Cloner le repo
```bash
git clone <repo_url>
cd POC-Agent-AI-ouvertures-echecs-FFE  
```

### 2. Setup environnement : Linux / Mac
```bash
chmod +x setup_env.sh
./setup_env.sh
```
---

### 3. Installation de make et de docker-compose
```bash
sudo apt update
sudo apt install -y make
sudo apt  install docker-compose
```
---

### 4. Créer l'environnement virtuel et lancer les services "Docker"
```bash
make setup
make docker-up
```

### 5. Accéder à l’API
*Healthcheck :*
```bash
http://localhost:8000/api/v1/healthcheck
```

*Documentation Swagger :*
```bash
http://localhost:8000/docs
```

*Frontend :*
```bash
http://localhost:4200
```
