.PHONY: setup migrate run prod test lint format

setup:
	pip install -r requirements.txt

migrate:
	flask db init
	flask db migrate -m "migration"
	flask db upgrade

run:
	flask run

prod:
	gunicorn -c gunicorn_config.py run:app

test:
	pytest tests/

lint:
	ruff check .

format:
	black .
