#!/bin/bash

set -e  # Exit on error

echo "Running mypy..."
mypy .

echo "Running ruff..."
ruff check .

echo "Running pytest..."
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pytest --cov=src --cov-report=term-missing

echo "All checks passed!"

