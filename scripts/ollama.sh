#!/bin/bash

set -e

echo "🚀 Subindo container do Ollama..."

# Remove container antigo (se existir)

docker rm -f ollama >/dev/null 2>&1 || true

# Sobe o container (tudo em uma linha)

docker run -d --name ollama -p 11434:11434 -v ollama_data:/root/.ollama ollama/ollama

echo "⏳ Aguardando o serviço iniciar..."
sleep 5

echo "📦 Baixando modelo (mistral - leve e rápido)..."
docker exec ollama ollama pull mistral

echo "🧪 Testando o modelo..."

curl http://localhost:11434/api/generate -d '{
"model": "mistral",
"prompt": "Diga: Ollama funcionando!",
"stream": false
}'

echo ""
echo "✅ Ollama está pronto em http://localhost:11434"
