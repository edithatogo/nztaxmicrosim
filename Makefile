.PHONY: test lint format install-dev-deps install clean run-example

install:
	pip install .

install-dev-deps:
	pip install -r requirements-dev.txt

test:
	pytest

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .

clean:
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	find . -type d -name "*.egg-info" -exec rm -rf {} + 
	rm -rf build/
	rm -rf dist/
	find . -type f -name "*.pyc" -delete

run-example:
	python examples/basic_usage.py