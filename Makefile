.PHONY: run
run:
	uv run main.py

.PHONY: validate
validate:
	uvx ruff format
	uvx ruff check --fix