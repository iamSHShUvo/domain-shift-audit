.PHONY: test run docker

test:
	python -m pytest

run:
	uvicorn app.main:app --reload

docker:
	docker compose up --build
