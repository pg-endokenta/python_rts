.PHONY: frontend backend test

VENV := .venv
PYTHON := $(VENV)/bin/python

$(PYTHON):
	uv venv $(VENV)

frontend:
	npm install --prefix frontend
	npm --prefix frontend run dev -- --host

backend: $(PYTHON)
	uv pip install -p $(PYTHON) -e .
	$(PYTHON) -m uvicorn backend.webarena:app --reload

test: $(PYTHON)
	uv pip install -p $(PYTHON) -e .[dev]
	PATH=$(VENV)/bin:$$PATH SKIP_NESTED=1 $(PYTHON) -m pytest -v
