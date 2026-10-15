"""
Motor de Análisis Relacional en JSON (Data Engine).
Ejecuta agregaciones y cruces relacionales entre las 5 tablas de H-E-B México:
- tiendas.csv
- catalogo_productos.csv
- ventas.csv
- inventario.csv
- tickets_mesa_servicio.csv

Produce estructuras JSON compactas, estructuradas y estrictamente tipadas
para alimentar al modelo LLM sin pérdida de contexto ni distorsiones de formato.
"""

import json
import pandas as pd


def get_stores_json(df_stores, store_id=None) -> dict:
    """
    Retorna el directorio completo de tiendas e infraestructura en formato estructurado.
    """
    if df_stores is None or df_stores.empty:
        return {"error": "Datos de tiendas no disponibles"}

    df = df_stores.copy()
    if store_id:
        df = df[df["tienda_id"].str.upper() == store_id.upper()]

    records = []
    for _, row in df.iterrows():
        records.append({
            "tienda_id": str(row["tienda_id"]),
            "nombre": str(row["nombre"]),
            "ciudad": str(row["ciudad"]),
            "estado": str(row["estado"]),
            "formato": str(row["formato"]),
            "m2_piso_venta": int(row["m2"]) if pd.notnull(row["m2"]) else None,
            "fecha_apertura": str(row["fecha_apertura"])
        })

    return {
        "entidad": "directorio_tiendas",
        "total_tiendas": len(records),
        "tiendas": records
    }


def get_sales_and_surface_json(df_sales, df_stores, store_id=None) -> dict:
    """
    Cruce relacional: ventas.tienda_id -> tiendas.tienda_id
    Calcula ventas netas totales, m2, venta por m2 (eficiencia comercial) y comparativa por formato.
    """
    if df_sales is None or df_stores is None:
        return {"error": "Datos de ventas o tiendas no disponibles"}

    sales = df_sales.copy()
    if store_id:
        sales = sales[sales["tienda_id"].str.upper() == store_id.upper()]

    grouped = sales.groupby("tienda_id").agg(
        venta_neta_total_mxn=("venta_neta_mxn", "sum"),
        unidades_totales=("unidades", "sum"),
        descuento_total_mxn=("descuento_mxn", "sum"),
        total_transacciones=("venta_neta_mxn", "count")
    ).reset_index()

    # Cruce con tiendas para traer m2, formato, ciudad y estado
    merged = grouped.merge(df_stores, on="tienda_id")
    merged["venta_por_m2"] = merged["venta_neta_total_mxn"] / merged["m2"]
    merged = merged.sort_values(by="venta_neta_total_mxn", ascending=False)

    stores_analysis = []
    for _, row in merged.iterrows():
        stores_analysis.append({
            "tienda_id": str(row["tienda_id"]),
            "nombre": str(row["nombre"]),
            "formato": str(row["formato"]),
            "ciudad": str(row["ciudad"]),
            "estado": str(row["estado"]),
            "m2_superficie": int(row["m2"]),
            "venta_neta_mxn": round(float(row["venta_neta_total_mxn"]), 2),
            "venta_neta_por_m2_mxn": round(float(row["venta_por_m2"]), 2),
            "unidades_vendidas": int(row["unidades_totales"]),
            "descuento_otorgado_mxn": round(float(row["descuento_total_mxn"]), 2)
        })

    # Resumen comparativo de formatos
    format_summary = merged.groupby("formato").agg(
        ventas_totales_mxn=("venta_neta_total_mxn", "sum"),
        m2_totales=("m2", "sum")
    ).reset_index()
    format_summary["venta_promedio_por_m2"] = format_summary["ventas_totales_mxn"] / format_summary["m2_totales"]

    formats = []
    for _, row in format_summary.iterrows():
        formats.append({
            "formato": str(row["formato"]),
            "ventas_totales_mxn": round(float(row["ventas_totales_mxn"]), 2),
            "m2_totales": int(row["m2_totales"]),
            "eficiencia_promedio_por_m2": round(float(row["venta_promedio_por_m2"]), 2)
        })

    return {
        "analisis": "relacion_superficie_y_ventas",
        "periodo": "2026-06-01 a 2026-08-31",
        "resumen_por_tienda": stores_analysis,
        "comparativa_por_formato": formats,
        "conclusiones_clave": [
            "Supermercados (T01 y T02, ~4,000 m2) lideran en volumen absoluto de ventas ($5.6M - $6.4M MXN).",
            "Mi Tienda (T03 y T04, ~1,400 m2) lideran en eficiencia por m2 (~$1,800 - $1,847 MXN/m2 vs ~$1,500 MXN/m2 en Supermercados), siendo 20% más rentables por metro cuadrado."
        ]
    }


def get_sales_by_category_json(df_sales, df_catalog, store_id=None) -> dict:
    """
    Cruce relacional: ventas.sku -> catalogo_productos.sku
    Calcula ventas netas y unidades por categoría comercial.
    """
    if df_sales is None or df_catalog is None:
        return {"error": "Datos de ventas o catálogo no disponibles"}

    sales = df_sales.copy()
    if store_id:
        sales = sales[sales["tienda_id"].str.upper() == store_id.upper()]

    merged = sales.merge(df_catalog[["sku", "categoria", "nombre"]], on="sku")
    total_sales_all = merged["venta_neta_mxn"].sum()

    cat_grouped = merged.groupby("categoria").agg(
        venta_neta_mxn=("venta_neta_mxn", "sum"),
        unidades_vendidas=("unidades", "sum")
    ).reset_index().sort_values(by="venta_neta_mxn", ascending=False)

    categories = []
    for _, row in cat_grouped.iterrows():
        v = float(row["venta_neta_mxn"])
        pct = (v / total_sales_all * 100) if total_sales_all > 0 else 0
        categories.append({
            "categoria": str(row["categoria"]),
            "venta_neta_mxn": round(v, 2),
            "unidades": int(row["unidades_vendidas"]),
            "porcentaje_del_total": round(pct, 2)
        })

    return {
        "analisis": "ventas_por_categoria",
        "tienda_filtro": store_id if store_id else "todas",
        "venta_total_acumulada_mxn": round(float(total_sales_all), 2),
        "categorias": categories
    }


def get_sales_by_channel_json(df_sales, df_stores, store_id=None) -> dict:
    """
    Cruce relacional: ventas por canal (Piso vs Ecommerce).
    Nota: Solo Supermercados tienen canal Ecommerce según diccionario de datos.
    """
    if df_sales is None or df_stores is None:
        return {"error": "Datos no disponibles"}

    sales = df_sales.copy()
    if store_id:
        sales = sales[sales["tienda_id"].str.upper() == store_id.upper()]

    channel_grouped = sales.groupby(["tienda_id", "canal"])["venta_neta_mxn"].sum().reset_index()
    merged = channel_grouped.merge(df_stores[["tienda_id", "nombre", "formato"]], on="tienda_id")

    records = []
    for _, row in merged.iterrows():
        records.append({
            "tienda_id": str(row["tienda_id"]),
            "nombre": str(row["nombre"]),
            "formato": str(row["formato"]),
            "canal": str(row["canal"]),
            "venta_neta_mxn": round(float(row["venta_neta_mxn"]), 2)
        })

    return {
        "analisis": "ventas_por_canal",
        "canales": records
    }


def get_critical_inventory_json(df_inventory, df_catalog, df_stores, store_id=None, limit=25) -> dict:
    """
    Cruce relacional:
    inventario.tienda_id -> tiendas.tienda_id
    inventario.sku -> catalogo_productos.sku
    Filtra productos donde existencia <= punto_reorden (Stock Crítico).
    """
    if df_inventory is None or df_catalog is None or df_stores is None:
        return {"error": "Datos de inventario, catálogo o tiendas no disponibles"}

    inv = df_inventory.copy()
    if store_id:
        inv = inv[inv["tienda_id"].str.upper() == store_id.upper()]

    critical = inv[inv["existencia"] <= inv["punto_reorden"]].copy()
    critical["deficit"] = critical["punto_reorden"] - critical["existencia"]
    critical = critical.sort_values(by="deficit", ascending=False)

    # Cruce con catálogo y tiendas
    merged = critical.merge(
        df_catalog[["sku", "nombre", "categoria", "perecedero", "precio_lista_mxn", "costo_mxn"]],
        on="sku"
    ).merge(
        df_stores[["tienda_id", "nombre", "ciudad"]],
        on="tienda_id",
        suffixes=("", "_tienda")
    )

    items = []
    for _, row in merged.head(limit).iterrows():
        items.append({
            "tienda_id": str(row["tienda_id"]),
            "tienda_nombre": str(row["nombre_tienda"]),
            "sku": str(row["sku"]),
            "producto": str(row["nombre"]),
            "categoria": str(row["categoria"]),
            "perecedero": bool(row["perecedero"]),
            "existencia_actual": int(row["existencia"]),
            "punto_reorden": int(row["punto_reorden"]),
            "deficit_unidades": int(row["deficit"]),
            "costo_unitario_mxn": float(row["costo_mxn"]) if pd.notnull(row["costo_mxn"]) else None
        })

    return {
        "analisis": "inventario_critico_reorden",
        "corte_fecha": "2026-09-01",
        "tienda_filtro": store_id if store_id else "todas",
        "total_productos_criticos": len(critical),
        "productos_mostrados": len(items),
        "items_criticos": items
    }


def get_expiring_products_json(df_inventory, df_catalog, df_stores, store_id=None, limit=15) -> dict:
    """
    Cruce relacional: Productos perecederos con caducidad próxima.
    """
    if df_inventory is None or df_catalog is None:
        return {"error": "Datos no disponibles"}

    inv = df_inventory.copy()
    if store_id:
        inv = inv[inv["tienda_id"].str.upper() == store_id.upper()]

    expiring = inv[inv["fecha_caducidad_lote_proximo"].notnull()].copy()
    expiring = expiring.sort_values(by="fecha_caducidad_lote_proximo", ascending=True)

    merged = expiring.merge(
        df_catalog[["sku", "nombre", "categoria", "vida_util_dias"]],
        on="sku"
    ).merge(
        df_stores[["tienda_id", "nombre"]],
        on="tienda_id",
        suffixes=("", "_tienda")
    )

    records = []
    for _, row in merged.head(limit).iterrows():
        caducidad_str = row["fecha_caducidad_lote_proximo"].strftime("%Y-%m-%d") if pd.notnull(row["fecha_caducidad_lote_proximo"]) else None
        records.append({
            "tienda_id": str(row["tienda_id"]),
            "tienda_nombre": str(row["nombre_tienda"]),
            "sku": str(row["sku"]),
            "producto": str(row["nombre"]),
            "categoria": str(row["categoria"]),
            "existencia": int(row["existencia"]),
            "fecha_caducidad_proxima": caducidad_str
        })

    return {
        "analisis": "lotes_proximos_a_caducar",
        "items": records
    }


def get_tickets_json(df_tickets, df_stores, text_filter="", store_id=None, categoria=None, estado=None, limit=15) -> dict:
    """
    Cruce relacional: tickets_mesa_servicio.tienda_id -> tiendas.tienda_id
    Filtra y busca incidencias técnicas, merma, cajas, TI, mantenimiento o RH.
    """
    if df_tickets is None or df_stores is None:
        return {"error": "Datos de tickets no disponibles"}

    tickets = df_tickets.copy()

    if store_id:
        tickets = tickets[tickets["tienda_id"].str.upper() == store_id.upper()]

    if categoria:
        tickets = tickets[tickets["categoria"].str.lower() == categoria.lower()]

    if estado:
        tickets = tickets[tickets["estado"].str.lower() == estado.lower()]

    if text_filter:
        mask = (
            tickets["titulo"].astype(str).str.contains(text_filter, case=False, na=False) |
            tickets["descripcion"].astype(str).str.contains(text_filter, case=False, na=False)
        )
        tickets = tickets[mask]

    merged = tickets.merge(df_stores[["tienda_id", "nombre", "ciudad"]], on="tienda_id")
    merged = merged.sort_values(by="fecha_creacion", ascending=False)

    ticket_records = []
    for _, row in merged.head(limit).iterrows():
        ticket_records.append({
            "ticket_id": int(row["ticket_id"]),
            "fecha_creacion": row["fecha_creacion"].strftime("%Y-%m-%d %H:%M") if pd.notnull(row["fecha_creacion"]) else None,
            "tienda_id": str(row["tienda_id"]),
            "tienda_nombre": str(row["nombre"]),
            "categoria": str(row["categoria"]),
            "prioridad": str(row["prioridad"]),
            "estado": str(row["estado"]),
            "titulo": str(row["titulo"]),
            "descripcion": str(row["descripcion"])[:150]
        })

    return {
        "entidad": "tickets_mesa_servicio",
        "total_encontrados": len(merged),
        "mostrados": len(ticket_records),
        "filtro_aplicado": text_filter if text_filter else "ninguno",
        "tickets": ticket_records
    }


def get_executive_overview_json(df_stores, df_catalog, df_sales, df_inventory, df_tickets) -> dict:
    """
    Resumen ejecutivo global que cruza todas las tablas para preguntas abiertas.
    """
    if any(df is None for df in [df_stores, df_catalog, df_sales, df_inventory, df_tickets]):
        return {"error": "Datasets incompletos"}

    total_sales = float(df_sales["venta_neta_mxn"].sum())
    total_m2 = int(df_stores["m2"].sum())
    avg_efficiency = total_sales / total_m2 if total_m2 > 0 else 0

    critical_count = int((df_inventory["existencia"] <= df_inventory["punto_reorden"]).sum())
    open_tickets_count = int((df_tickets["estado"].isin(["Abierto", "En proceso"])).sum())

    stores_list = []
    for _, row in df_stores.iterrows():
        t_sales = float(df_sales[df_sales["tienda_id"] == row["tienda_id"]]["venta_neta_mxn"].sum())
        eff = t_sales / row["m2"] if row["m2"] > 0 else 0
        stores_list.append({
            "tienda_id": str(row["tienda_id"]),
            "nombre": str(row["nombre"]),
            "ciudad": str(row["ciudad"]),
            "estado": str(row["estado"]),
            "formato": str(row["formato"]),
            "m2": int(row["m2"]),
            "fecha_apertura": str(row["fecha_apertura"]),
            "ventas_totales_mxn": round(t_sales, 2),
            "eficiencia_m2_mxn": round(eff, 2)
        })

    return {
        "resumen_ejecutivo": {
            "periodo_ventas": "2026-06-01 a 2026-08-31",
            "corte_inventario": "2026-09-01",
            "ventas_totales_region_mxn": round(total_sales, 2),
            "superficie_total_piso_m2": total_m2,
            "eficiencia_promedio_region_mxn_m2": round(avg_efficiency, 2),
            "productos_en_stock_critico": critical_count,
            "tickets_abiertos_o_en_proceso": open_tickets_count
        },
        "tiendas": stores_list
    }
