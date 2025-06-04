.PHONY: frontend backend test

frontend:
	npm install --prefix frontend
	npm --prefix frontend run dev -- --host

backend:
	uvicorn backend.webarena:app --reload

test:
	pip install -e .[dev]
	SKIP_NESTED=1 python -m pytest -v
