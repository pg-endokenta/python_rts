.PHONY: frontend backend test

-include .env
BACKEND_PORT ?= 8000

VENV := .venv
PYTHON := $(VENV)/bin/python

$(PYTHON):
	uv venv $(VENV)

frontend:
	npm install --prefix frontend
	npm --prefix frontend run dev -- --host

backend: $(PYTHON)
	uv pip install -p $(PYTHON) -e .
	$(PYTHON) -m uvicorn backend.webarena:app --reload --port $(BACKEND_PORT)

test: $(PYTHON)
	uv pip install -p $(PYTHON) -e .[dev]
	PATH=$(VENV)/bin:$$PATH SKIP_NESTED=1 $(PYTHON) -m pytest -v

