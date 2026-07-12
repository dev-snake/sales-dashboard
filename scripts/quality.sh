#!/usr/bin/env bash
# Local quality gate (no CI/CD in project scope).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> ruff"
ruff check src tests

echo "==> black"
black --check src tests

echo "==> mypy"
mypy

echo "==> pytest (unit only by default)"
if [[ "${RUN_INTEGRATION:-0}" == "1" ]]; then
  pytest -q
else
  pytest -q -m "not integration and not data_quality"
fi

echo "OK — quality gate passed"
