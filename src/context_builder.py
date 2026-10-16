"""
Módulo Orquestador de Contexto (Context Builder).
Analiza la intención de la consulta de la gerente y genera un payload estructurado en JSON
respetando la integridad relacional entre tiendas, catálogo, ventas, inventario y tickets.
"""

import json
from src.data_engine import (
    get_stores_json,
    get_sales_and_surface_json,
    get_sales_by_category_json,
    get_sales_by_channel_json,
    get_critical_inventory_json,
    get_expiring_products_json,
    get_tickets_json,
    get_executive_overview_json
)
from src.policy_search import search_in_policies

def detect_store_id(prompt: str) -> str | None:
    """
    Detecta si la consulta hace referencia a una tienda específica por código o nombre.
    """
    p = prompt.lower()
    store_map = {
        "t01": "T01",
        "valle norte": "T01",
        "t02": "T02",
        "cumbres": "T02",
        "t03": "T03",
        "anahuac": "T03",
        "anáhuac": "T03",
        "t04": "T04",
        "lomas del sur": "T04",
        "saltillo": "T04"
    }
    for alias, s_id in store_map.items():
        if alias in p:
            return s_id
    return None

def build_json_context(prompt: str, df_stores, df_catalog, df_sales, df_inventory, df_tickets) -> tuple[str, dict]:
    """
    Construye el contexto en formato JSON según la intención de la pregunta.
    Retorna:
    - context_str (str): Cadena formateada en JSON para inyectar en el prompt.
    - raw_payload (dict): Diccionario crudo para visualización en UI.
    """
    p_lower = prompt.lower()
    target_store = detect_store_id(prompt)

    payload = {
        "sistema": "Asistente Inteligente H-E-B México",
        "version_esquema": "1.0-relacional-json",
        "entorno": {
            "periodo_ventas": "Junio 2026 - Agosto 2026",
            "corte_inventario": "2026-09-01",
            "tienda_detectada": target_store if target_store else "todas"
        },
        "datos_relacionales": {},
        "politicas_normativas": []
    }

    matched_sections = 0

    # 1. Información e infraestructura de Tiendas / Superficie / Apertura / m2
    store_keywords = [
        "tienda", "tiendas", "sucursal", "sucursales", "apertura", "formato",
        "estado", "ciudad", "m2", "metros", "superficie", "ubicacion", "ubicación"
    ]
    if any(k in p_lower for k in store_keywords):
        payload["datos_relacionales"]["directorio_tiendas"] = get_stores_json(df_stores, store_id=target_store)
        matched_sections += 1

    # 2. Análisis de Ventas, Ingresos y Relación con Metros Cuadrados / Eficiencia
    sales_keywords = [
        "venta", "ventas", "dinero", "ingresos", "m2", "metro", "metros",
        "cuadrado", "superficie", "relacion", "relación", "eficiencia",
        "rendimiento", "canal", "piso", "ecommerce"
    ]
    if any(k in p_lower for k in sales_keywords):
        payload["datos_relacionales"]["analisis_ventas_y_superficie"] = get_sales_and_surface_json(
            df_sales, df_stores, store_id=target_store
        )
        if any(c in p_lower for c in ["canal", "ecommerce", "piso", "online"]):
            payload["datos_relacionales"]["ventas_por_canal"] = get_sales_by_channel_json(
                df_sales, df_stores, store_id=target_store
            )
        matched_sections += 1

    # 3. Categorías de Productos
    category_keywords = [
        "categoria", "categoría", "departamento", "abarrotes", "lacteos",
        "lácteos", "carnes", "limpieza", "bebidas", "panaderia", "panadería",
        "frutas", "verduras"
    ]
    if any(k in p_lower for k in category_keywords):
        payload["datos_relacionales"]["ventas_por_categoria"] = get_sales_by_category_json(
            df_sales, df_catalog, store_id=target_store
        )
        matched_sections += 1

    # 4. Inventario, Stock, Reorden y Caducidad
    inventory_keywords = [
        "inventario", "stock", "reorden", "existencia", "producto", "faltante",
        "caducidad", "caducar", "lote", "perecedero"
    ]
    if any(k in p_lower for k in inventory_keywords):
        payload["datos_relacionales"]["inventario_critico_reorden"] = get_critical_inventory_json(
            df_inventory, df_catalog, df_stores, store_id=target_store, limit=20
        )
        if any(c in p_lower for c in ["caducid", "caducar", "lote", "vencer", "vence", "pereced"]):
            payload["datos_relacionales"]["lotes_proximos_caducidad"] = get_expiring_products_json(
                df_inventory, df_catalog, df_stores, store_id=target_store, limit=15
            )
        matched_sections += 1

    # 5. Tickets de Mesa de Servicio (Problemas, Fallas, Mantenimiento, etc.)
    ticket_keywords = [
        "ticket", "tickets", "mesa", "servicio", "problema", "reporte",
        "falla", "incidencia", "mantenimiento", "cajas", "refrigeracion", "clima"
    ]
    if any(k in p_lower for k in ticket_keywords):
        key_filter = ""
        for word in ["frutas", "merma", "inventario", "cajas", "refrigeracion", "clima", "falla"]:
            if word in p_lower:
                key_filter = word
                break
        payload["datos_relacionales"]["tickets_mesa_servicio"] = get_tickets_json(
            df_tickets, df_stores, text_filter=key_filter, store_id=target_store, limit=15
        )
        matched_sections += 1

    # 6. Políticas Internas en PDF
    policy_keywords = [
        "política", "politica", "regla", "manual", "procedimiento",
        "devolución", "devolucion", "merma", "baja", "cierre", "apertura", "norma"
    ]
    if any(k in p_lower for k in policy_keywords):
        policy_text = search_in_policies(prompt)
        payload["politicas_normativas"] = policy_text
        matched_sections += 1

    # 7. Fallback: Si no se activó ninguna sección específica, proveer Resumen Ejecutivo Global
    if matched_sections == 0 or not payload["datos_relacionales"]:
        payload["datos_relacionales"]["resumen_ejecutivo_global"] = get_executive_overview_json(
            df_stores, df_catalog, df_sales, df_inventory, df_tickets
        )
        # Siempre agregar directorio de tiendas para contexto base
        payload["datos_relacionales"]["directorio_tiendas"] = get_stores_json(df_stores)

    # Serializar a formato JSON legible para el LLM
    json_formatted = json.dumps(payload, indent=2, ensure_ascii=False)
    return json_formatted, payload
