# main.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
import google.generativeai as genai
import os

# Substitua por sua API key do Gemini
GENAI_API_KEY = os.getenv("GENAI_API_KEY") or "AIzaSyBNAdFIIYvSuuU0j-4AlafFpjNvaS2j3NU"
genai.configure(api_key=GENAI_API_KEY)

app = FastAPI()

class DadosSensor(BaseModel):
    temperatura: float
    umidade: float
    pressao: float
    frequencia_vento: float
    direcao_encoder: str
    posicao_encoder: int

@app.post("/api/dados")
async def receber_dados(dados: DadosSensor):
    # Log dos dados recebidos (para Render)
    print(f"📡 Dados recebidos do ESP32: {dados}")

    # Formata a entrada
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

    # Interação com o Gemini
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    try:
        response = model.generate_content(prompt)
        insight = response.text.strip()
        
        # Log da resposta do Gemini
        print(f"🌟 Resposta do Gemini: {insight}")
        
        return {
            "status": "ok",
            "insight": insight
        }
    
    except Exception as e:
        print(f"❌ Erro ao gerar resposta: {e}")
        return {"status": "error", "message": "Erro ao gerar resposta"}
