import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000"
INGESTION_ID = "ea6bbabe-5338-435b-be1f-f5f4da9fa4ab"

async def call_insights():
    print("🚀 Iniciando requisição de INSIGHTS (lenta)...")
    start = time.time()
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/insights/",
                json={"ingestion_id": INGESTION_ID}
            )
            end = time.time()
            print(f"✅ INSIGHTS concluído em {end - start:.2f}s")
        except Exception as e:
            print(f"❌ Erro em INSIGHTS: {e}")

async def call_metrics():
    # Espera 1 segundo para garantir que a de insights começou
    await asyncio.sleep(1)
    print("📊 Iniciando requisição de MÉTRICAS (rápida)...")
    start = time.time()
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/metrics/",
                json={"ingestion_id": INGESTION_ID}
            )
            end = time.time()
            print(f"✅ MÉTRICAS concluída em {end - start:.2f}s")
        except Exception as e:
            print(f"❌ Erro em MÉTRICAS: {e}")

async def main():
    # Executa ambas concorrentemente
    await asyncio.gather(call_insights(), call_metrics())

if __name__ == "__main__":
    asyncio.run(main())
