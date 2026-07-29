.PHONY: setup migrate run start_db prod test lint format test-db-start test-db-stop test-ephemeral

setup:
	pip install -r requirements.txt

migrate:
	flask db init
	flask db migrate -m "migration"
	flask db upgrade

start_db:
	@pg_ctl status -D $$PREFIX/var/lib/postgresql > /dev/null 2>&1 || pg_ctl start -D $$PREFIX/var/lib/postgresql

run: start_db
	flask run --host=0.0.0.0 --port=5000

prod:
	gunicorn -c gunicorn_config.py run:app

test:
	pytest tests/

test-db-start:
	./scripts/manage_test_db.sh start

test-db-stop:
	./scripts/manage_test_db.sh stop

test-ephemeral: test-db-start
	export TEST_DATABASE_URL=postgresql://localhost:5433/flexam_test && PYTHONPATH=. pytest tests/
	$(MAKE) test-db-stop

lint:
	ruff check .

format:
	black .
