import os
import boto3
from botocore.config import Config
from scripts.config import (
    R2_ENDPOINT_URL,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME,
    validate_config
)

# =========================================================
# CONFIGURACIÓN
# =========================================================

# Ruta local donde debe vivir el archivo
LOCAL_PATH = "data/geih.duckdb"
REMOTE_KEY = "geih.duckdb"  # Nombre del archivo en R2


# =========================================================
# DESCARGA AUTOMÁTICA DEL ARCHIVO
# =========================================================

def get_r2_client():
    """Crea y retorna un cliente de S3 configurado para R2."""
    validate_config()

    s3 = boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT_URL,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4")
    )
    return s3


def ensure_duckdb_exists():
    """
    Descarga el archivo geih.duckdb desde Cloudflare R2 si no existe localmente.
    No se vuelve a descargar en cada ejecución.
    """
    os.makedirs("data", exist_ok=True)

    if os.path.exists(LOCAL_PATH):
        print("✔ geih.duckdb ya está presente.")
        return

    print("⬇ Descargando geih.duckdb desde Cloudflare R2...")

    try:
        s3 = get_r2_client()
        s3.download_file(R2_BUCKET_NAME, REMOTE_KEY, LOCAL_PATH)
        print("✔ Descarga completada.")
    except Exception as e:
        print(f"✘ Error al descargar: {e}")
        raise


def upload_duckdb_to_r2():
    """
    Sube el archivo geih.duckdb local a Cloudflare R2.
    Útil para actualizar la base de datos en la nube.
    """
    if not os.path.exists(LOCAL_PATH):
        print(f"✘ El archivo {LOCAL_PATH} no existe localmente.")
        return

    print("⬆ Subiendo geih.duckdb a Cloudflare R2...")

    try:
        s3 = get_r2_client()
        s3.upload_file(LOCAL_PATH, R2_BUCKET_NAME, REMOTE_KEY)
        print("✔ Subida completada.")
    except Exception as e:
        print(f"✘ Error al subir: {e}")
        raise


if __name__ == "__main__":
    ensure_duckdb_exists()
