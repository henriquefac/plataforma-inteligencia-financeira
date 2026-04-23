import sys
import os
from pathlib import Path

# Adiciona o root do projeto ao sys.path
root = Path(__file__).parent.parent
sys.path.append(str(root))

import logging
from llama_index.core.schema import TextNode
from app.core.chromadb.db import chroma_db

# Configura logging para ver o que está acontecendo
logging.basicConfig(level=logging.INFO)

def test_chroma_integration():
    try:
        print("🚀 Iniciando teste de integração do ChromaDB...")
        
        # 1. Limpar coleção para o teste (opcional, mas bom para garantir consistência)
        # chroma_db.clear_collection()
        
        # 2. Criar nodes de teste
        nodes = [
            TextNode(
                text="O faturamento da empresa no primeiro trimestre foi de 1 milhão de reais.",
                metadata={"setor": "financeiro", "periodo": "Q1"}
            ),
            TextNode(
                text="A nova política de home office permite 3 dias presenciais e 2 remotos.",
                metadata={"setor": "RH", "tipo": "politica"}
            )
        ]
        
        print("📦 Criando índice a partir de nodes...")
        index = chroma_db.create_index_from_nodes(nodes)
        
        print("🔍 Realizando consulta de teste...")
        query_engine = index.as_query_engine()
        response = query_engine.query("Quanto a empresa faturou no Q1?")
        
        print(f"✅ Resposta recebida: {response}")
        
        # 3. Testar recuperação do índice
        print("🔄 Testando recuperação do índice existente...")
        existing_index = chroma_db.get_index()
        existing_query_engine = existing_index.as_query_engine()
        existing_response = existing_query_engine.query("Qual a política de home office?")
        
        print(f"✅ Resposta da recuperação: {existing_response}")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chroma_integration()
