#!/bin/bash

# Nome do container
CONTAINER_NAME="chroma_db"

# Porta
PORT=8000

# Diretório local para persistência
DATA_DIR="./chroma_data"

echo "🚀 Subindo Chroma DB..."

# Cria diretório se não existir
mkdir -p $DATA_DIR

# Para e remove container antigo (se existir)
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "🛑 Parando container existente..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# Sobe o container
docker run -d \
  --name $CONTAINER_NAME \
  -p $PORT:8000 \
  -v $(pwd)/chroma_data:/chroma/chroma \
  chromadb/chroma

echo "✅ Chroma rodando em http://localhost:$PORT"