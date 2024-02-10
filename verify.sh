#! /usr/bin/env sh

set -e

echo "Installing Dependencies..."
python -m pip install --upgrade pip
python setup.py install
pip install --upgrade flake8 pylint pytest pytest-cov pytest-asyncio pytest-httpserver black mypy

echo "Running black..."
black --check .

echo "Running isort"
isort --profile black .

echo "Running mypy..."
mypy --exclude venv .

echo "Running flake8..."
flake8 --ignore=E501,E704 solax tests

echo "Running pylint..."
pylint -d 'C0111' solax tests

echo "Running pytest..."
pytest --cov=solax --cov-fail-under=100 --cov-branch --cov-report=term-missing .
