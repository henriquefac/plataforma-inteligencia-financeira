#!/bin/bash

set -e

echo "🚀 Subindo container do Ollama..."

# Remove container antigo (se existir)
docker rm -f ollama >/dev/null 2>&1 || true

# Sobe o container
docker run -d --name ollama -p 11434:11434 -v ollama_data:/root/.ollama ollama/ollama

echo "⏳ Aguardando o serviço iniciar..."
sleep 5

echo "📦 Baixando modelo de geração (mistral)..."
docker exec ollama ollama pull mistral

echo "📦 Baixando modelo de embeddings (nomic-embed-text)..."
docker exec ollama ollama pull nomic-embed-text

echo "🧪 Testando modelo de geração..."

curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Diga: Ollama funcionando!",
  "stream": false
}'

echo ""
echo "🧪 Testando modelo de embedding..."

curl http://localhost:11434/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "teste de embedding"
}'

echo ""
echo "✅ Ollama está pronto em http://localhost:11434"