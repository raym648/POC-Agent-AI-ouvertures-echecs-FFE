# ♟️ POC-Agent-AI-ouvertures-echecs-FFE – Projet 13

## 📌 Contexte
Projet de développement d’un agent IA pour l’apprentissage des échecs dans le cadre de la Fédération Française des Échecs (FFE).

---

## 🧱 Stack technique
- FastAPI (backend)
- Angular (frontend)
- Docker / Docker Compose
- Milvus (vector DB)
- MongoDB (stockage)

---

## 🚀 Lancement du projet

### 1. Cloner le repo
```bash
git clone <repo_url>
cd project-root
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
