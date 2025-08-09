.PHONY: test coverage profile lint format install-dev-deps install clean run-example

install:
	pip install .

install-dev-deps:
	pip install -e .
	pip install -r requirements-dev.txt

test:
	PYTHONWARNINGS="ignore:pkg_resources is deprecated as an API" pytest

coverage:
	pytest --cov=src --cov-report=term-missing

profile:
	pytest --profile

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
	./syspop/venv/bin/python examples/basic_usage.py

run-microsim-comparison:
	./syspop/venv/bin/python examples/run_microsim_comparison.py --param_files $(PARAM_FILES) $(if $(POPULATION_SCALE),--population_scale $(POPULATION_SCALE))

generate-reports:
	./syspop/venv/bin/python examples/generate_reports.py --param_files $(PARAM_FILES)

docs:
	mkdocs serve
