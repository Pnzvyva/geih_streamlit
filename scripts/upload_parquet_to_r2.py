"""
Sube todos los archivos parquet al bucket R2 manteniendo la estructura de carpetas.
Estructura en R2: parquet/{categoria}/{año}/{tipo}.parquet
"""
import os
import boto3
from botocore.config import Config
from pathlib import Path
from scripts.config import (
    R2_ENDPOINT_URL,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME,
    validate_config
)

LOCAL_PARQUET_DIR = "parquet_export"
R2_PREFIX = "parquet"  # Prefijo en el bucket


def get_r2_client():
    """Crea y retorna un cliente de S3 configurado para R2."""
    validate_config()

    # Deshabilitar verificación SSL para evitar errores de certificado
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    s3 = boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT_URL,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        verify=False
    )
    return s3


def upload_parquet_files():
    """Sube todos los archivos parquet al bucket R2."""
    print("=" * 60)
    print("SUBIDA DE ARCHIVOS PARQUET A R2")
    print("=" * 60)

    if not os.path.exists(LOCAL_PARQUET_DIR):
        print(f"[ERROR] No se encontró el directorio {LOCAL_PARQUET_DIR}")
        return

    # Obtener cliente R2
    print("\nConectando a R2...")
    s3 = get_r2_client()

    # Contar archivos (solo los que están en subcarpetas, no en raíz)
    parquet_files = []
    for root, dirs, files in os.walk(LOCAL_PARQUET_DIR):
        for file in files:
            if file.endswith('.parquet'):
                local_path = os.path.join(root, file)
                # Solo incluir archivos que estén dentro de subcarpetas (categoria/año/)
                rel_path = os.path.relpath(local_path, LOCAL_PARQUET_DIR)
                if os.path.dirname(rel_path):  # Tiene directorio padre
                    parquet_files.append(local_path)

    print(f"Total de archivos parquet encontrados: {len(parquet_files)}")

    # Subir cada archivo
    uploaded = 0
    errors = []

    for local_path in sorted(parquet_files):
        # Calcular la ruta relativa y la clave en R2
        # parquet_export/caracteristicas/2007/cabecera.parquet -> parquet/caracteristicas/2007/cabecera.parquet
        rel_path = os.path.relpath(local_path, LOCAL_PARQUET_DIR)
        r2_key = f"{R2_PREFIX}/{rel_path}".replace("\\", "/")  # Normalizar separadores

        try:
            print(f"  Subiendo: {rel_path} -> s3://{R2_BUCKET_NAME}/{r2_key}")
            s3.upload_file(local_path, R2_BUCKET_NAME, r2_key)
            uploaded += 1
        except Exception as e:
            error_msg = f"[ERROR] Subiendo {rel_path}: {e}"
            print(f"  {error_msg}")
            errors.append(error_msg)

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Archivos subidos exitosamente: {uploaded}/{len(parquet_files)}")

    if errors:
        print(f"Errores: {len(errors)}")
        for err in errors[:10]:
            print(f"  - {err}")
        if len(errors) > 10:
            print(f"  ... y {len(errors) - 10} más")

    print(f"\nEstructura en R2: s3://{R2_BUCKET_NAME}/{R2_PREFIX}/")
    print("  {categoria}/{año}/{tipo}.parquet")


if __name__ == "__main__":
    upload_parquet_files()
