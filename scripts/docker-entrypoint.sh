#!/usr/bin/env bash
set -euo pipefail

# run alembic migrations unless in test environment
if [ "${ENV:-development}" != "test" ]; then
  echo "Running migrations..."
  alembic upgrade head || true
fi

exec "$@"
