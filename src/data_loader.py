"""
Módulo de Carga y Validación de Datos.
Lee y valida los archivos CSV de H-E-B México respetando el diccionario de datos.
"""

import os
import pandas as pd
import streamlit as st
from config.settings import DATA_FOLDER

@st.cache_data(show_spinner=False)
def load_data():
    """
    Carga todos los datasets del directorio de datos con caché de Streamlit.
    Retorna (df_stores, df_catalog, df_sales, df_inventory, df_tickets).
    """
    try:
        encoding = 'latin-1'
        folder = DATA_FOLDER if os.path.exists(DATA_FOLDER) else "datos"

        catalog_path = os.path.join(folder, "catalogo_productos.csv")
        inventory_path = os.path.join(folder, "inventario.csv")
        tickets_path = os.path.join(folder, "tickets_mesa_servicio.csv")
        stores_path = os.path.join(folder, "tiendas.csv")
        sales_path = os.path.join(folder, "ventas.csv")

        # 1. Catálogo de productos (121 filas)
        df_catalog = pd.read_csv(catalog_path, encoding=encoding)
        df_catalog["precio_lista_mxn"] = pd.to_numeric(df_catalog["precio_lista_mxn"], errors="coerce")
        df_catalog["costo_mxn"] = pd.to_numeric(df_catalog["costo_mxn"], errors="coerce")

        # 2. Inventario al corte (2026-09-01, 480 filas)
        df_inventory = pd.read_csv(
            inventory_path,
            parse_dates=["fecha_ultimo_conteo", "fecha_caducidad_lote_proximo"]
        )
        df_inventory["existencia"] = pd.to_numeric(df_inventory["existencia"], errors="coerce")
        df_inventory["punto_reorden"] = pd.to_numeric(df_inventory["punto_reorden"], errors="coerce")

        # 3. Tickets de mesa de servicio (285 filas)
        df_tickets = pd.read_csv(
            tickets_path,
            encoding=encoding,
            parse_dates=["fecha_creacion", "fecha_cierre"]
        )

        # 4. Tiendas (4 filas)
        df_stores = pd.read_csv(stores_path, encoding=encoding)
        df_stores["m2"] = pd.to_numeric(df_stores["m2"], errors="coerce")


        # 5. Ventas históricas (Junio - Agosto 2026, 41,859 filas)
        df_sales = pd.read_csv(
            sales_path,
            encoding=encoding,
            parse_dates=["fecha"]
        )
        df_sales["unidades"] = pd.to_numeric(df_sales["unidades"], errors="coerce")
        df_sales["venta_neta_mxn"] = pd.to_numeric(df_sales["venta_neta_mxn"], errors="coerce")
        df_sales["descuento_mxn"] = pd.to_numeric(df_sales["descuento_mxn"], errors="coerce")

        return df_stores, df_catalog, df_sales, df_inventory, df_tickets

    except Exception as e:
        st.error(f"Error crítico al cargar datasets en '{DATA_FOLDER}': {e}")
        return None, None, None, None, None


def get_dataset_stats(df_stores, df_catalog, df_sales, df_inventory, df_tickets):
    """
    Retorna métricas de salud de los datos cargados para inspección en UI.
    """
    if any(df is None for df in [df_stores, df_catalog, df_sales, df_inventory, df_tickets]):
        return None

    return {
        "tiendas": len(df_stores),
        "productos": len(df_catalog),
        "ventas_registros": len(df_sales),
        "inventario_registros": len(df_inventory),
        "tickets_registros": len(df_tickets),
        "periodo_ventas": f"{df_sales['fecha'].min().strftime('%Y-%m-%d')} a {df_sales['fecha'].max().strftime('%Y-%m-%d')}",
        "corte_inventario": "2026-09-01"
    }