include .env

# ============ Docker compose ============ 
build:
	docker compose build

up:
	docker compose up

up-d:
	docker compose up -d

up-build:
	docker compose up --build

up-build-d:
	docker compose up --build -d

down:
	docker compose down

restart: down up

restart-d: down up-d

restart-build-d: down up-build-d

sleep:
	sleep 20

