# Aqui se alojan funciones de pandas #

import pandas as pd

def get_stores_info(df_stores):
    #---- Obtiene caracteristicas de las tiendas ----#
    if df_stores is None or df_stores.empty:
        return "No hay informacion de tiendas disponibles."
    result = "**Informacion General de Tiendas (datos/tiendas.csv):**\n\n"
    for _, row in df_stores.iterrows():
        result += (
            f"- **{row['nombre']} (ID: {row['tienda_id']})**:\n"
            f"  * Ciudad: {row['ciudad']}\n"
            f"  * Estado: {row['estado']}\n"
            f"  * Formato: {row['formato']}\n"
            f"  * Superficie: {row['m2']:,} m² de piso de venta\n"
            f"  * Fecha de apertura: {row['fecha_apertura']}\n"
        )
    return result

def get_sales_summary(df_sales, df_stores):
    #---- Ventas totales por tienda ----#

    if df_stores is None or df_sales is None:
        return "No hay datos disponibles"

    total_sales = df_sales.groupby("tienda_id")["venta_neta_mxn"].sum().reset_index()
    total_sales = total_sales.merge(df_stores[["tienda_id", "nombre", "ciudad"]], on="tienda_id")
    total_sales = total_sales.sort_values(by="venta_neta_mxn", ascending=False)

    result = "**Resumen de Ventas Netas por Tienda (Junio - Agosto 2026):**\n\n"
    for _, row in total_sales.iterrows():
        result += f"- **{row['nombre']} ({row['tienda_id']})** en {row['ciudad']}: ${row['venta_neta_mxn']:,.2f} MXN\n"

    return result

def get_low_inventory(df_inventory, df_catalog, store_id=None):
    #---- Productos cuya existencia sea menor o igual al punto de reorden ----#
    if df_inventory is None or df_catalog is None:
        return "No hay datos de inventario disponibles"
    
    #---- Se crea una copy del df para un mejor manejo de los datos ----#
    inventory = df_inventory.copy()

    if store_id:
        inventory = inventory[inventory["tienda_id"].str.upper() == store_id.upper()]
    
    critic_products = inventory[inventory["existencia"] <= inventory["punto_reorden"]]
    if critic_products.empty:
        return f"No hay productos por debajo del punto de reorden{' para la tienda' + store_id if store_id else ''}."
    
    critic_products = critic_products.merge(df_catalog[["sku", "nombre", "categoria"]], on="sku")

    result = f" **Productos bajo el punto de reorden (Stock crítico):**\n\n"
    for _, row in critic_products.head(15).iterrows():
        result += f"- **Tienda {row['tienda_id']}** | SKU: {row['sku']} - {row['nombre']} | Existencia: {row['existencia']} (Mínimo requerido: {row['punto_reorden']})\n"
    return result
    
def search_tickets(df_tickets, text_filter=""):
    #---- Busca tickets de mesa de servicio que coincidan con palabras clave ----#
    if df_tickets is None:
        return "No hay datos de tickets disponibles"
    
    if text_filter:
        mask = df_tickets["titulo"].str.contains(text_filter, case=False, na=False) | \
               df_tickets["descripcion"].str.contains(text_filter, case=False, na=False)
        filtered_tickets = df_tickets[mask]
    else:
        filtered_tickets = df_tickets.head(10)
    
    if filtered_tickets.empty:
        return f"No se encontraron tickets relacionados con '{text_filter}'." 

    result = f"🛠️ **Tickets de Mesa de Servicio Encontrados ({len(filtered_tickets)}):**\n\n"

    for _, row in filtered_tickets.head(10).iterrows():
        result += f"- **Ticket #{row['ticket_id']}** ({row['fecha_creacion'].strftime('%Y-%m-%d')}) - [{row['estado']}] **{row['titulo']}**: {row['descripcion'][:100]}...\n"
    return result