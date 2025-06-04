.PHONY: frontend backend test

frontend:
	npm install --prefix frontend
	npm --prefix frontend run dev -- --host

backend:
	pip install -e .
	python -m uvicorn backend.webarena:app --reload

test:
	pip install -e .[dev]
	SKIP_NESTED=1 python -m pytest -v
