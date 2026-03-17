"""
Configuración centralizada para acceso a Cloudflare R2.
Las credenciales se cargan desde variables de entorno o Streamlit Secrets.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env (para desarrollo local)
load_dotenv()

# Intentar importar streamlit para soportar secrets en la nube
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

# Función para obtener configuración desde env o st.secrets
def get_config(key, default=None):
    """Obtiene configuración desde variables de entorno o Streamlit secrets."""
    # Primero intentar desde variables de entorno
    value = os.getenv(key)
    if value:
        return value

    # Si está en Streamlit Cloud, intentar desde st.secrets
    if HAS_STREAMLIT:
        try:
            # Intentar primero en la sección R2
            if hasattr(st, 'secrets') and 'R2' in st.secrets:
                if key in st.secrets['R2']:
                    return st.secrets['R2'][key]
            # Intentar en root de secrets
            if hasattr(st, 'secrets') and key in st.secrets:
                return st.secrets[key]
        except:
            pass

    return default


# R2 Configuration
R2_ENDPOINT_URL = get_config("R2_ENDPOINT_URL", "https://1345c0d7da19b13339e8ff83529689ff.r2.cloudflarestorage.com")
R2_ACCESS_KEY_ID = get_config("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = get_config("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = get_config("R2_BUCKET_NAME", "microdata-geih-duckdb")

# URL pública para acceso directo (si está configurada)
R2_PUBLIC_URL = get_config("R2_PUBLIC_URL", "")


def validate_config():
    """Valida que todas las credenciales necesarias estén configuradas."""
    missing = []
    if not R2_ACCESS_KEY_ID:
        missing.append("R2_ACCESS_KEY_ID")
    if not R2_SECRET_ACCESS_KEY:
        missing.append("R2_SECRET_ACCESS_KEY")
    if not R2_BUCKET_NAME:
        missing.append("R2_BUCKET_NAME")

    if missing:
        raise ValueError(
            f"Faltan las siguientes variables de entorno: {', '.join(missing)}\n"
            "Por favor, configúralas en un archivo .env o en el entorno del sistema."
        )
