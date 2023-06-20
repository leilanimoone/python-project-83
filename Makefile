install:
	poetry install

build:
	poetry build

build-db: 
        db-reset schema-data-load

db-start:
	sudo service postgresql start

db-status:
	sudo service postgresql status

db-stop:
	sudo service postgresql stop

db-create:
	createdb page_analyzer

db-drop:
	dropdb page_analyzer

db-reset:
	dropdb page_analyzer || true
	createdb page_analyzer

db-dev-setup: 
        db-reset schema-load

schema-load:
	psql page_analyzer < database.sql

db-connect:
	psql -d page_analyzer

lint:
	poetry run flake8 page_analyzer

test:
	poetry run pytest

dev:
	poetry run flask --app page_analyzer:app --debug run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app