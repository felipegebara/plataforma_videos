"""
Ollama Client Helper para Antigravity.
Conecta ao servidor Ollama local (http://localhost:11434) usando o modelo qwen2.5:7b.
"""
import json
import urllib.request
from typing import Optional, Dict

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:7b"


def query_ollama(prompt: str, model: str = DEFAULT_MODEL, timeout_sec: float = 10.0) -> Optional[str]:
    """
    Envia uma requisição de geração de texto para o Ollama local.
    Retorna a string de resposta ou None se houver falha/timeout.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 300,
        }
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            OLLAMA_URL,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            if resp.status == 200:
                body = json.loads(resp.read().decode("utf-8"))
                return body.get("response", "").strip()
    except Exception as err:
        print(f"[OllamaClient] Aviso ao consultar Ollama: {err}")
    return None
