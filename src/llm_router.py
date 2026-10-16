"""
Módulo de Comunicación con OpenRouter (LLM Router).
Gestiona llamadas a la API de OpenRouter, políticas de fallback entre modelos,
medición de latencia y telemetría de tokens/costos conforme al BRIEF de H-E-B.
"""

import os
import time
import json
import requests
from dotenv import load_dotenv
from config.settings import PROMPT_ROUTE, OPENROUTER_URL, AVAILABLE_MODELS

# Cargar variables de entorno desde .env
load_dotenv()

DEFAULT_API_KEY = os.getenv(
    "AI_AGENT_KEY"
)


def load_prompt() -> str:
    """
    Carga el prompt de sistema desde el archivo de configuración.
    """
    try:
        if os.path.exists(PROMPT_ROUTE):
            with open(PROMPT_ROUTE, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception:
        pass
    return (
        "Eres un asistente de inteligencia artificial experto para gerentes de tienda de H-E-B México. "
        "Responde con base estricta en el contexto JSON y citas de políticas suministradas."
    )


def fetch_openrouter(user_prompt: str, data_context: str, api_key: str = None, preselected_model: str = None) -> dict:
    """
    Ejecuta la llamada a OpenRouter enviando el contexto en JSON.
    Retorna un diccionario estructurado con:
    - content (str): Texto de la respuesta.
    - usage (dict): {"prompt_tokens": int, "completion_tokens": int, "total_tokens": int}
    - model (str): Modelo que atendió la respuesta.
    - latency (float): Segundos que tardó la llamada.
    - cost_usd (float): Costo monetario estimado en USD.
    - error (str | None): Mensaje de error si falló.
    """
    active_key = api_key if api_key else DEFAULT_API_KEY

    if not active_key:
        return {
            "content": "Por favor ingresa o configura tu API Key de OpenRouter para consultar al asistente.",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "model": "None",
            "latency": 0.0,
            "cost_usd": 0.0,
            "error": "Missing API Key"
        }

    headers = {
        "Authorization": f"Bearer {active_key}",
        "HTTP-Referer": "https://heb-asistente.streamlit.app",
        "X-Title": "HEB Store Assistant",
        "Content-Type": "application/json",
    }

    system_prompt = load_prompt()

    user_payload = f"""
### CONTEXTO DE DATOS Y POLÍTICAS (FORMATO JSON OFICIAL DE H-E-B MÉXICO):
{data_context}

### PREGUNTA DE LA GERENTE:
{user_prompt}
"""

    # Orden de prioridad de modelos para el fallback
    models = []
    if preselected_model and preselected_model in AVAILABLE_MODELS:
        models.append(preselected_model)

    for m in AVAILABLE_MODELS:
        if m not in models:
            models.append(m)

    if not models:
        models = ["openrouter/free"]

    models = models[:3]  # Máximo 3 modelos para fallback

    body = {
        "models": models,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_payload}
        ],
        "temperature": 0.1 # Gestionamos el nivel de divagacion/alucinamiento.
    }

    start_time = time.time()

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            data=json.dumps(body),
            timeout=40
        )
        latency = round(time.time() - start_time, 2)

        if response.status_code == 200:
            res_json = response.json()

            if "choices" in res_json and len(res_json["choices"]) > 0:
                answer = res_json["choices"][0]["message"]["content"]
                raw_usage = res_json.get("usage", {})
                usage = {
                    "prompt_tokens": raw_usage.get("prompt_tokens", 0),
                    "completion_tokens": raw_usage.get("completion_tokens", 0),
                    "total_tokens": raw_usage.get("total_tokens", 0)
                }
                model_used = res_json.get("model", models[0])
                cost = float(raw_usage.get("cost", 0.0))

                return {
                    "content": answer,
                    "usage": usage,
                    "model": model_used,
                    "latency": latency,
                    "cost_usd": cost,
                    "error": None
                }

            if "error" in res_json:
                error_msg = res_json["error"].get("message", "Error del proveedor")
                return {
                    "content": f"**Disculpa, el proveedor reportó saturación:** {error_msg}. Intenta de nuevo en unos segundos.",
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                    "model": models[0],
                    "latency": latency,
                    "cost_usd": 0.0,
                    "error": error_msg
                }

        return {
            "content": f"**Disculpa, los servidores están experimentando alta demanda.** (Código {response.status_code}: {response.text[:120]}). Intenta nuevamente en un momento.",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "model": models[0],
            "latency": latency,
            "cost_usd": 0.0,
            "error": f"HTTP {response.status_code}"
        }

    except requests.exceptions.Timeout:
        return {
            "content": "**La consulta tardó más de 40 segundos en responder.** Los servidores están con alta latencia. Por favor reintenta tu pregunta.",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "model": models[0],
            "latency": 40.0,
            "cost_usd": 0.0,
            "error": "Timeout"
        }
    except requests.exceptions.RequestException as e:
        return {
            "content": f"**Error de conexión:** No se pudo contactar al servidor: {e}",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "model": models[0],
            "latency": 0.0,
            "cost_usd": 0.0,
            "error": str(e)
        }
