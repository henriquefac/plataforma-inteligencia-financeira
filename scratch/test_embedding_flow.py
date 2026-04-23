import sys
import os
from pathlib import Path
import pandas as pd

# Adiciona o root do projeto ao sys.path
root = Path(__file__).parent.parent
sys.path.append(str(root))

import logging
from app.domain.data_artifact import DataArtifact
from app.service.rag.embedding import EmbeddingService
from app.core.chromadb.db import chroma_db

# Configura logging
logging.basicConfig(level=logging.INFO)

def test_embedding_flow():
    try:
        print("🚀 Iniciando teste do fluxo de Embedding -> ChromaDB...")
        
        # 1. Criar um artefato de teste
        artifact = DataArtifact.create("teste_embedding.csv")
        ingestion_id = artifact.ingestion_id
        print(f"🆔 Ingestion ID: {ingestion_id}")
        
        # 2. Criar dados enriquecidos de teste
        df_enriched = pd.DataFrame([
            {
                "descricao": "Venda de software SaaS",
                "cliente": "Empresa A",
                "tipo_servico": "Software",
                "recorrencia": "Mensal",
                "status": "pago",
                "is_inadimplente": False,
                "receita_real": 5000,
                "setor": "Tecnologia"
            },
            {
                "descricao": "Consultoria técnica",
                "cliente": "Empresa B",
                "tipo_servico": "Serviço",
                "recorrencia": "Única",
                "status": "pendente",
                "is_inadimplente": True,
                "receita_real": 12000,
                "setor": "Consultoria"
            }
        ])
        
        # Salvar o DataFrame como enriquecido
        artifact.save_enriched(df_enriched)
        print("✅ Dados enriquecidos de teste criados.")
        
        # 3. Executar o serviço de Embedding
        service = EmbeddingService()
        print("⚙️ Executando EmbeddingService.generate_and_store_embeddings...")
        result = service.generate_and_store_embeddings(ingestion_id)
        
        print(f"📊 Resultado: {result}")
        
        if result["status"] == "success":
            print("✅ Fluxo concluído com sucesso!")
            
            # 4. Verificar se conseguimos recuperar o índice
            print("🔍 Verificando acesso ao índice...")
            index = chroma_db.get_index()
            print("✅ Acesso ao índice confirmado.")
        else:
            print(f"❌ Falha no fluxo: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_embedding_flow()
