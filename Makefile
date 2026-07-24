.PHONY: setup migrate run test lint format

setup:
	pip install -r requirements.txt

migrate:
	flask db init
	flask db migrate -m "migration"
	flask db upgrade

run:
	flask run

test:
	pytest tests/

lint:
	ruff check .

format:
	black .
