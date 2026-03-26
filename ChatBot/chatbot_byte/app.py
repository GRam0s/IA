import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests as req_lib

app = Flask(__name__, static_folder="static")
CORS(app)

API_KEY = os.environ.get("GROQ_API_KEY", "")

SYSTEM_PROMPT = """Você é o Dr. Byte, um assistente virtual especializado em parada cardiorrespiratória (PCR) e ressuscitação cardiopulmonar (RCP).

Seu conhecimento abrange:
- Reconhecimento de parada cardiorrespiratória
- Protocolo de RCP para adultos, crianças e lactentes (diretrizes AHA/ILCOR atualizadas)
- Uso do DEA (Desfibrilador Externo Automático)
- Cadeia de sobrevivência
- Suporte Básico de Vida (BLS) e Suporte Avançado de Vida (ACLS)
- Ritmos de parada: FV, TV sem pulso, AESP, Assistolia
- Drogas utilizadas na PCR (adrenalina, amiodarona, etc.)
- Cuidados pós-PCR
- Situações especiais: afogamento, choque elétrico, hipotermia, gestante

Regras importantes:
- Responda sempre em português brasileiro de forma clara e objetiva
- Em situações de emergência real, sempre oriente a ligar imediatamente para o SAMU (192)
- Seja preciso tecnicamente, mas use linguagem acessível quando o contexto pedir
- Nunca substitua atendimento médico presencial em emergências reais
- Para perguntas fora da sua especialidade, redirecione educadamente ao tema de PCR/RCP
- Use formatação clara com passos numerados quando descrever protocolos"""

def call_groq(messages):
    r = req_lib.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": "Bearer " + API_KEY},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            "max_tokens": 1000
        }
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/favicon.ico")
def favicon():
    return "", 204

@app.route("/chat", methods=["POST"])
def chat():
    try:
        if not API_KEY:
            return jsonify({"error": "GROQ_API_KEY nao definida!"}), 500
        data = request.json
        messages = data.get("messages", [])
        if not messages:
            return jsonify({"error": "Sem mensagem"}), 400
        reply = call_groq(messages)
        return jsonify({"reply": reply})
    except Exception as e:
        print("[ERRO]", type(e).__name__, str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    if not API_KEY:
        print("ERRO: $env:GROQ_API_KEY nao definida!")
    else:
        print("Chave Groq OK!")
    print("Dr. Byte rodando em http://localhost:5000")
    app.run(debug=True, port=5000)
