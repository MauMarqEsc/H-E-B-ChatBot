# 🛒 Asistente Inteligente H-E-B México (ChatBot)

Sistema de consulta y analítica gerencial para directores y gerentes de tienda de H-E-B México. Permite analizar ventas, inventarios, infraestructura, tickets y políticas operativas a través de modelos de lenguaje mediante OpenRouter.

---

## 📋 Requisitos Previos

- **Python**: Versión 3.10 o superior (el proyecto fue desarrollado y probado en **Python 3.14**).
- **Terminal / Consola**: Acceso a CMD, PowerShell, Git Bash o Terminal (macOS/Linux).
- **Conexión a Internet**: Necesaria para la instalación de dependencias y la comunicación con la API de OpenRouter.

---

## 🔑 Configuración de la API Key (OpenRouter)

> [!IMPORTANT]
> **Nota para el evaluador:** La **API Key (`AI_AGENT_KEY`)** necesaria para la ejecución de las consultas a los modelos de inteligencia artificial **se encuentra incluida en el cuerpo del correo en el cual se responde a esta prueba técnica**.

Para proporcionarla a la aplicación, puedes elegir cualquiera de estas dos opciones:

### Opción A: Archivo `.env` (Recomendada / Automática)
1. En la carpeta raíz del proyecto, copia o renombra el archivo `.env.example` como `.env`.
2. Abre el archivo `.env` y asigna la clave provista en el correo:
   ```env
   AI_AGENT_KEY=tu_api_key_recibida_por_correo
   ```
*(De esta forma, la aplicación cargará la clave de forma predeterminada al iniciar).*

### Opción B: Directamente en la Interfaz Gráfica
Si prefieres no crear el archivo `.env`, puedes iniciar la aplicación y pegar la clave directamente en el campo **"API Key (OpenRouter)"** ubicado en la barra lateral izquierda (Sidebar).

---

## 🚀 Guía de Instalación y Ejecución

Sigue estos pasos en tu terminal para preparar el entorno e iniciar la aplicación:

### 1. Ubicarse en el directorio raíz del proyecto
Abre tu terminal en la carpeta principal del proyecto (donde se encuentra `app.py` y `README.md`), por ejemplo:
```bash
cd ruta/a/ChatBot
```

### 2. Crear un entorno virtual limpio
Se recomienda crear un entorno virtual aislado para evitar conflictos de paquetes:
```bash
python -m venv venv
```

### 3. Activar el entorno virtual

- **En Windows (PowerShell):**
  ```powershell
  venv\Scripts\Activate.ps1
  ```
  *(Nota: Si PowerShell bloquea la ejecución de scripts por política de seguridad, puedes habilitarlo temporalmente en esa terminal ejecutando: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y luego ejecutar de nuevo `venv\Scripts\Activate.ps1`).*

- **En Windows (CMD / Símbolo del Sistema):**
  ```cmd
  venv\Scripts\activate.bat
  ```

- **En macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

*(Una vez activado, verás el prefijo `(venv)` al inicio de tu consola).*

### 4. Instalar las dependencias
Con el entorno virtual activo, instala los paquetes requeridos:
```bash
pip install -r requirements.txt
```

### 5. Iniciar la aplicación
Ejecuta el siguiente comando para correr el servidor de Streamlit:
```bash
streamlit run app.py
```

Al iniciar, Streamlit abrirá automáticamente la aplicación en tu navegador web predeterminado en la dirección:
`http://localhost:8501`

---

## 🛡️ Notas sobre Firewall, Red y Solución de Problemas

- **Permisos de Firewall (Windows / Red Local):**
  - Al ejecutar Streamlit por primera vez, el Firewall de Windows Defender o de tu sistema operativo podría mostrar una advertencia solicitando permisos para que Python acceda a las redes.
  - Puedes conceder y seleccionar con total seguridad **"Permitir acceso"** (redes privadas/locales), ya que Streamlit crea un servidor exclusivamente local en tu máquina (`localhost`).
- **Puerto bloqueado u ocupado (Puerto 8501):**
  - Por defecto, Streamlit usa el puerto `8501`. Si dicho puerto estuviera ocupado o restringido por políticas de seguridad de red corporativa, puedes especificar otro puerto libre con el parámetro `--server.port`:
    ```bash
    streamlit run app.py --server.port 8080
    ```
- **Apertura manual en el navegador:**
  - Si por alguna razón la ventana del navegador no se abre de forma automática al ejecutar el comando, simplemente abre tu navegador (Chrome, Edge, Firefox, Safari) e ingresa manualmente a:
    ```
    http://localhost:8501
    ```