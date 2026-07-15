#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f docker/.env ]; then
  cp docker/.env.example docker/.env
  echo "Created docker/.env from example — update SECRET_KEY before production use."
fi

docker compose --profile ai up -d --build

echo "SKYASSIST AI is starting..."
echo "  Frontend:  http://localhost"
echo "  Backend:   http://localhost:8000"
echo "  API docs:  http://localhost:8000/docs"
echo "  Health:    http://localhost:8000/health"
echo "  Metrics:   http://localhost:8000/metrics"
echo ""
echo "Pull Ollama model (first time): docker exec skyassist-ollama ollama pull llama3.2"
