up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

migrate:
	poetry run alembic upgrade head

test:
	poetry run pytest -q

lint:
	poetry run python -m compileall app && poetry run python -m compileall tests

