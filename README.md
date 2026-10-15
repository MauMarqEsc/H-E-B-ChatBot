## Recomendación de entorno
El proyecto fue probado en Python 3.14.  Recomiendo crear un entorno virtual limpio antes de instalar las dependencias:

## Requisitos para correr
- Tener instalada alguna verison de python y poder acceder desde el cmd.

Con la consola/terminal en la ruta "..\ChatBot>" ingresar:

python -m venv venv

# En Mac/Linux pegar en terminal:
source venv/bin/activate
# En Windows pegar en terminal:
venv\Scripts\Activate.ps1

Ingresar el comando:
pip install -r requirements.txt

Para correr la app ingresar:
streamlit run app.py