"""
Configuración centralizada para acceso a Cloudflare R2.
Las credenciales se cargan desde variables de entorno.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

# R2 Configuration
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL", "https://1345c0d7da19b13339e8ff83529689ff.r2.cloudflarestorage.com")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "microdata-geih-duckdb")

# URL pública para acceso directo (si está configurada)
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL", "")


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
