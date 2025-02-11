.PHONY: lint test run install clean check

PYTHON := poetry run python
PYTEST := poetry run pytest
FLAKE8 := poetry run flake8
BLACK := poetry run black
ISORT := poetry run isort
MYPY := poetry run mypy

lint: 
	$(ISORT) --check .
	$(BLACK) --check .
	$(FLAKE8) .
	$(MYPY) .

test:
	$(PYTEST) --cov=log_analyzer --cov-report=term

run:
	$(PYTHON) log_analyzer/log_analyzer.py $(OPTIONS)

install:
	poetry install

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf .mypy_cache .pytest_cache .venv

# Вызов всех проверок
check: lint test