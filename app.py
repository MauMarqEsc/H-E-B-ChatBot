"""
Asistente Inteligente H-E-B México - Interfaz de Usuario (Streamlit)
Sistema de consulta gerencial para análisis de Ventas, Inventario, Infraestructura, Tickets y Políticas.
Desarrollado siguiendo los lineamientos de BRIEF.md y las mejores prácticas de ingeniería de software.
"""

import os
import streamlit as st
from config.settings import AVAILABLE_MODELS, CSS_PATH
from src.data_loader import load_data, get_dataset_stats
from src.context_builder import build_json_context
from src.llm_router import fetch_openrouter, DEFAULT_API_KEY
from src.evaluation import get_benchmark_questions


# 1. Configuración de página
st.set_page_config(
    page_title="H-E-B México | Asistente de Tienda",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Carga de estilos CSS corporativos
def load_css(css_path: str):
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css(CSS_PATH)

# 3. Carga y caché de datos relacionales
df_stores, df_catalog, df_sales, df_inventory, df_tickets = load_data()
data_stats = get_dataset_stats(df_stores, df_catalog, df_sales, df_inventory, df_tickets)

# 4. Inicialización de estado de sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

if "total_session_tokens" not in st.session_state:
    st.session_state.total_session_tokens = 0

if "last_tokens" not in st.session_state:
    st.session_state.last_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# 5. Sidebar: Configuración, Telemetría y Banco de Pruebas
with st.sidebar:
    st.markdown("### 🛒 H-E-B México")
    st.caption("Panel de Control del Asistente")

    st.markdown("---")
    st.subheader("⚙️ Modelo y Conectividad")
    model_choice = st.selectbox("Modelo de IA (OpenRouter)", AVAILABLE_MODELS, index=0)
    api_key_input = st.text_input("API Key (OpenRouter)", value=DEFAULT_API_KEY, type="password")

    st.markdown("---")
    # Requerimiento #5 del BRIEF: Telemetría de tokens y costo
    st.subheader("📊 Consumo de Tokens (BRIEF #5)")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.metric(
            label="Última Consulta",
            value=f"{st.session_state.last_tokens['total_tokens']:,}",
            help=f"Prompt: {st.session_state.last_tokens['prompt_tokens']} | Respuesta: {st.session_state.last_tokens['completion_tokens']}"
        )
    with col_t2:
        st.metric(
            label="Total Sesión",
            value=f"{st.session_state.total_session_tokens:,}",
            help="Tokens acumulados en la sesión actual"
        )
    st.caption("💳 **Costo estimado:** $0.00 USD (Modelos gratuitos / BYOK)")

    st.markdown("---")
    # Requerimiento #4 del BRIEF: Set de preguntas de prueba
    st.subheader("🎯 Pruebas del BRIEF (Req. #4)")
    st.caption("Haz clic en una prueba oficial para evaluar la precisión del asistente:")
    benchmarks = get_benchmark_questions()
    for item in benchmarks:
        if st.button(f"{item['categoria']}", key=f"btn_{item['id']}", use_container_width=True):
            st.session_state.pending_prompt = item["pregunta"]
            st.rerun()

    st.markdown("---")
    # Estado de Bases de Datos
    st.subheader("🗄️ Fuentes Conectadas")
    if data_stats:
        st.markdown(f"- 🏬 **Tiendas:** {data_stats['tiendas']} sucursales")
        st.markdown(f"- 📦 **Catálogo:** {data_stats['productos']} SKUs")
        st.markdown(f"- 💳 **Ventas:** {data_stats['ventas_registros']:,} registros ({data_stats['periodo_ventas']})")
        st.markdown(f"- 📊 **Inventario:** {data_stats['inventario_registros']} registros (corte 2026-09-01)")
        st.markdown(f"- 🛠️ **Tickets:** {data_stats['tickets_registros']} incidencias")
        st.markdown("- 📄 **Políticas:** 4 documentos PDF")
    else:
        st.error("No se pudieron cargar las bases de datos.")


# 6. Área Principal del Chat
st.title("🛒 Asistente Inteligente para Gerentes")
st.markdown(
    "Consulta asistida sobre **ventas netas**, **stock crítico**, "
    "**tickets de mesa de servicio** y **políticas internas en PDF** con citas y relaciones de datos reales."
)
st.markdown("---")

chat_container = st.container()

# Renderizar historial de mensajes
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # Si es respuesta del asistente y tiene telemetría o JSON
            if msg["role"] == "assistant":
                meta = msg.get("meta", {})
                tokens_info = meta.get("usage", {})
                latency = meta.get("latency", 0.0)
                model_used = meta.get("model", "N/A")

                # Badge de telemetría
                if tokens_info.get("total_tokens", 0) > 0:
                    st.caption(
                        f"⏱️ **Latencia:** {latency}s | "
                        f"🪙 **Tokens:** {tokens_info.get('total_tokens', 0):,} "
                        f"(Prompt: {tokens_info.get('prompt_tokens', 0)}, Resp: {tokens_info.get('completion_tokens', 0)}) | "
                        f"🤖 **Modelo:** `{model_used}`"
                    )

                # Inspección del JSON enviado a la IA
                json_ctx = meta.get("json_context")
                if json_ctx:
                    with st.expander("🔍 Ver datos relacionales JSON suministrados a la IA"):
                        st.json(json_ctx)


# 7. Procesamiento de Pregunta (Entrada de texto o botón de Benchmark)
prompt_input = st.chat_input("Escribe tu consulta gerencial aquí...")

# Determinar si la entrada viene de chat_input o de un botón del benchmark
active_prompt = None
if prompt_input:
    active_prompt = prompt_input
elif st.session_state.pending_prompt:
    active_prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if active_prompt:
    # 1. Registrar mensaje del usuario
    st.session_state.messages.append({
        "role": "user",
        "content": active_prompt
    })

    with chat_container:
        with st.chat_message("user"):
            st.markdown(active_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consultando bases de datos relacionales y políticas en PDF..."):

                # 2. Generar el contexto JSON estructurado mediante el orquestador
                json_context_str, raw_payload = build_json_context(
                    prompt=active_prompt,
                    df_stores=df_stores,
                    df_catalog=df_catalog,
                    df_sales=df_sales,
                    df_inventory=df_inventory,
                    df_tickets=df_tickets
                )

                # 3. Llamar al modelo de IA vía OpenRouter
                result = fetch_openrouter(
                    user_prompt=active_prompt,
                    data_context=json_context_str,
                    api_key=api_key_input,
                    preselected_model=model_choice
                )

                answer_text = result.get("content", "Sin respuesta.")
                usage = result.get("usage", {})
                latency = result.get("latency", 0.0)
                model_used = result.get("model", model_choice)

                # 4. Actualizar contadores de telemetría de tokens
                total_t = usage.get("total_tokens", 0)
                st.session_state.last_tokens = usage
                st.session_state.total_session_tokens += total_t

                # 5. Renderizar respuesta
                st.markdown(answer_text)

                if total_t > 0:
                    st.caption(
                        f"⏱️ **Latencia:** {latency}s | "
                        f"🪙 **Tokens:** {total_t:,} (Prompt: {usage.get('prompt_tokens', 0)}, Resp: {usage.get('completion_tokens', 0)}) | "
                        f"🤖 **Modelo:** `{model_used}`"
                    )

                with st.expander("🔍 Ver datos relacionales JSON suministrados a la IA"):
                    st.json(raw_payload)

                # 6. Guardar en historial con metadatos
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer_text,
                    "meta": {
                        "usage": usage,
                        "latency": latency,
                        "model": model_used,
                        "json_context": raw_payload
                    }
                })
