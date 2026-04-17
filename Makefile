# POC-Agent-AI-ouvertures-echecs-FFE/Makefile

# ===============================
# Commandes projet
# ===============================

setup:
	bash setup_env.sh

run:
	source .venv/bin/activate && uvicorn backend.app.main:app --reload

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

lint:
	echo "Lint à ajouter (flake8 / ruff)"

test:
	echo "Tests à ajouter (pytest)"
