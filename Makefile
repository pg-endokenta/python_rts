.PHONY: frontend backend test

frontend:
	npm install --prefix frontend
	npm --prefix frontend run dev -- --host

backend:
	uv pip install --system -e .
	python -m uvicorn backend.webarena:app --reload

test:
	uv pip install --system -e .[dev]
	SKIP_NESTED=1 python -m pytest -v
