"""
Módulo de Evaluación y Preguntas de Prueba (Benchmark BRIEF).
Cumple con el requerimiento #4 del BRIEF:
'Alguna forma de saber qué tan bien responde: un set de preguntas de prueba, métricas, lo que te haga sentido.'
"""

BENCHMARK_QUESTIONS = [
    {
        "id": "tiendas_info",
        "categoria": "🏬 Ficha de Tiendas",
        "pregunta": "Dame la informacion que tengas de las tiendas, nombre, estado, fecha de apertura, etc",
        "objetivo": "Verificar que devuelva todos los atributos de tiendas.csv (nombre, ciudad, estado, formato, m2, fecha de apertura).",
        "tablas": ["tiendas.csv"]
    },
    {
        "id": "relacion_m2_ventas",
        "categoria": "📊 Cruce Relacional (m² vs Ventas)",
        "pregunta": "Que me puedes decir de la relacion entre los metros cuadrados de las tiendas y sus ventas?",
        "objetivo": "Validar el cruce relacional entre ventas y tiendas, identificando volumen total vs eficiencia de venta por metro cuadrado ($/m²).",
        "tablas": ["tiendas.csv", "ventas.csv"]
    },
    {
        "id": "inventario_critico",
        "categoria": "📦 Stock Crítico",
        "pregunta": "¿Qué productos están por debajo del punto de reorden en la tienda T01 (Valle Norte)?",
        "objetivo": "Validar el cruce entre inventario.csv y catalogo_productos.csv filtrando existencia <= punto_reorden.",
        "tablas": ["inventario.csv", "catalogo_productos.csv", "tiendas.csv"]
    },
    {
        "id": "ventas_categoria",
        "categoria": "🏷️ Ventas por Categoría",
        "pregunta": "¿Cuáles son las categorías que generan mayores ingresos y cómo se distribuyen las ventas?",
        "objetivo": "Verificar el cruce entre ventas.csv y catalogo_productos.csv agrupado por categoría comercial.",
        "tablas": ["ventas.csv", "catalogo_productos.csv"]
    },
    {
        "id": "tickets_servicio",
        "categoria": "🛠️ Mesa de Servicio",
        "pregunta": "¿Cuáles son los tickets reportados sobre fallas en refrigeración, clima o merma de frutas?",
        "objetivo": "Verificar la búsqueda en tickets_mesa_servicio.csv cruzada con las tiendas.",
        "tablas": ["tickets_mesa_servicio.csv", "tiendas.csv"]
    },
    {
        "id": "politica_merma",
        "categoria": "📄 Políticas Internas (Citas)",
        "pregunta": "¿Cuál es el procedimiento oficial para reportar y dar de baja merma por caducidad?",
        "objetivo": "Validar que la respuesta cite el documento PDF exacto y el número de página de procedencia.",
        "tablas": ["politica_mermas_y_caducidad.pdf"]
    },
    {
        "id": "limite_no_alucinacion",
        "categoria": "🛡️ Falta de Información / Validación",
        "pregunta": "¿Cuánto vendió la sucursal Valle Norte en enero de 2024?",
        "objetivo": "Validar que reconozca que no tiene esos datos (el periodo registrado es exclusivamente junio-agosto 2026).",
        "tablas": ["Ninguna (fuera de alcance)"]
    }
]


def get_benchmark_questions():
    """Retorna la lista de preguntas del benchmark."""
    return BENCHMARK_QUESTIONS
