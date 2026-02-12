#!/bin/bash

set -e  # Exit on error

echo "Running mypy..."
mypy .

echo "Running ruff..."
ruff check . --fix

echo "Running unit tests..."
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pytest tests/ --cov=src --cov-report=term-missing

echo "Running E2E tests..."
pytest tests_e2e/

echo "All checks passed!"

