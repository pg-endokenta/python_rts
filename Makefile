.PHONY: dev test

dev:
	@if command -v docker > /dev/null; then \
	       docker compose build && docker compose up; \
	else \
	       echo "docker is not available"; \
	fi

test:
	SKIP_NESTED=1 python -m pytest -v
