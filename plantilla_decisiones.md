# Documento de decisiones

Nombre: Jose Mauricio Márquez Escobedo
Fecha: 12 de Octubre del 2026
Repositorio: 
Proveedor y modelos usados: 

Llena cada sección en 3 a 5 líneas. No hace falta que sea prosa pulida; nos interesa el razonamiento.

## 1. Qué construí y por qué en ese orden
1- data_loader.py: Quise validad la extracción de datos. su limpieza y acomodo en los DataFrames.
2- data_engine.py: Definir desde el comienzo las métricas que eran de mi interés que el BackEnd calculara.
3- policy_search.py: Validar que los datos del PDF se leyeran bien.
4- context_builder.py: Con lo anterior implementar este arhchivo de contexto fue sencillo.
5- llm_router.py: Ya con todos los elementos listos y programados solo necesité seguir la documentación.

## 2. Qué decidí no hacer
- Usar una Base de Datos relacional para no causar complicaciones a los evaluadores.
- Por cuestiones de tiempo me centré en desarrolar las metricas/relaciones entre columnas que consideré más importantes, principalmente las mencionadas en BRIEF.md
- Decidí no confiar en un solo modelo pues al utilizar servicios gratuitos las limitaciones al querer hacer request desde uno solo eran bastante molestas, y 1 sola daba constantes errores en el response.

## 3. Cómo sé que funciona
Puedo preguntar datos concretos y validarlos yo mismo en los exceles, asi mismo acudir a los PDF y las respuestas que da son fieles a los archivos fuente. Asi mismo considero que esta muy bien delimitada en sus respuestas. El haber configurado "temperature": 0.1 en llm_router.py me da también esa confianza que no divagará demasiado.


## 4. Costo por interacción y cómo lo medí
Los modelos son gratuitos, pero métricas de sus respuestas se encuentran en los valores del responde que entrega la conexión a OpenRouter que se despliegan en el chat.


## 5. Qué haría con dos semanas más
- Una base de datos dedicada, si es necesaria vectorial para manejar mejor las relaciones entre datos y no hacerlo a traves de las DataFrames y sobre todo para aagilizar la busqueda en PDFs.
- Sustituit la funcion de get_dataset_stats por un archivo "source_values.py" que obtenga datos importantes de los archivos disponibles para el análisis(Periodo de ventas, Corte, etc).



