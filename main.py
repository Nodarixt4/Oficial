from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from datetime import datetime

# ——— Configuração da API Gemini (GenAI) ———
GENAI_API_KEY = os.getenv("GENAI_API_KEY") or "AIzaSyBNAdFIIYvSuuU0j-4AlafFpjNvaS2j3NU"
genai.configure(api_key=GENAI_API_KEY)

# ——— FastAPI e CORS ———
app = FastAPI()

# Permitir requisições do front-end
# Em produção, troque ["*"] pelos domínios reais, ex: ["https://meu-site.com"]
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],    # GET, POST, PUT, etc.
    allow_headers=["*"],    # Content-Type, Authorization, etc.
)

# ——— Modelos de dados ———
class DadosSensor(BaseModel):
    temperatura: float
    umidade: float
    pressao: float
    frequencia_vento: float
    direcao_encoder: str
    posicao_encoder: int

# Armazenamento dos últimos dados
ultimos_dados = None
ultimo_insight = None
ultimo_timestamp = None

# ——— Endpoints ———

@app.post("/api/dados")
async def receber_dados(dados: DadosSensor):
    global ultimos_dados, ultimo_insight, ultimo_timestamp

    # Log dos dados recebidos (Render)
    print(f"📡 Dados recebidos do ESP32: {dados}")

    # Monta prompt para o Gemini
    prompt = f"""
    Dados recebidos de uma estação climática:
    Temperatura: {dados.temperatura:.1f} °C
    Umidade: {dados.umidade:.1f} %
    Pressão: {dados.pressao:.2f} hPa
    Frequência do vento: {dados.frequencia_vento:.2f} Hz
    Direção do vento: {dados.direcao_encoder}
    Posição do encoder: {dados.posicao_encoder}

    Gere um insight interpretativo e claro para o usuário sobre o clima atual.
    """

    # Gera resposta com Gemini
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    try:
        response = model.generate_content(prompt)
        insight = response.text.strip()

        # Log da resposta
        print(f"🌟 Resposta do Gemini: {insight}")

        # Armazena para o GET /ultimos
        ultimos_dados = dados
        ultimo_insight = insight
        ultimo_timestamp = datetime.now().isoformat()

        return {
            "status": "ok",
            "insight": insight
        }

    except Exception as e:
        print(f"❌ Erro ao gerar resposta: {e}")
        return {"status": "error", "message": "Erro ao gerar resposta"}

@app.get("/api/dados/ultimos")
async def obter_ultimos_dados():
    if ultimos_dados and ultimo_insight and ultimo_timestamp:
        return {
            "status": "ok",
            "timestamp": ultimo_timestamp,
            "dados": ultimos_dados.dict(),
            "insight": ultimo_insight
        }
    else:
        return {"status": "error", "message": "Nenhum dado disponível"}
