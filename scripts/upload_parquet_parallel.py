"""
Sube todos los archivos parquet al bucket R2 manteniendo la estructura de carpetas.
Versión paralela para mayor velocidad.
Estructura en R2: parquet/{categoria}/{año}/{tipo}.parquet
"""
import os
import boto3
import urllib3
from botocore.config import Config
from concurrent.futures import ThreadPoolExecutor, as_completed
from scripts.config import (
    R2_ENDPOINT_URL,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME,
    validate_config
)

LOCAL_PARQUET_DIR = "parquet_export"
R2_PREFIX = "parquet"
MAX_WORKERS = 10  # Número de hilos paralelos


def get_r2_client():
    """Crea y retorna un cliente de S3 configurado para R2."""
    validate_config()
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


def upload_single_file(args):
    """Sube un archivo individual a R2."""
    local_path, r2_key = args
    try:
        s3 = get_r2_client()
        s3.upload_file(local_path, R2_BUCKET_NAME, r2_key)
        return (True, local_path, None)
    except Exception as e:
        return (False, local_path, str(e))


def upload_parquet_files():
    """Sube todos los archivos parquet al bucket R2 en paralelo."""
    print("=" * 60)
    print("SUBIDA PARALELA DE ARCHIVOS PARQUET A R2")
    print("=" * 60)

    if not os.path.exists(LOCAL_PARQUET_DIR):
        print(f"[ERROR] No se encontró el directorio {LOCAL_PARQUET_DIR}")
        return

    print(f"\nConectando a R2...")

    # Contar archivos (solo los que están en subcarpetas)
    files_to_upload = []
    for root, dirs, files in os.walk(LOCAL_PARQUET_DIR):
        for file in files:
            if file.endswith('.parquet'):
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, LOCAL_PARQUET_DIR)
                if os.path.dirname(rel_path):
                    r2_key = f"{R2_PREFIX}/{rel_path}".replace("\\", "/")
                    files_to_upload.append((local_path, r2_key))

    total_files = len(files_to_upload)
    print(f"Total de archivos a subir: {total_files}")
    print(f"Hilos paralelos: {MAX_WORKERS}\n")

    # Subir en paralelo
    uploaded = 0
    errors = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(upload_single_file, args): args for args in files_to_upload}

        for future in as_completed(futures):
            success, local_path, error = future.result()
            rel_path = os.path.relpath(local_path, LOCAL_PARQUET_DIR)

            if success:
                uploaded += 1
                print(f"  [{uploaded}/{total_files}] OK: {rel_path}")
            else:
                print(f"  [ERROR] {rel_path}: {error}")
                errors.append((rel_path, error))

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Archivos subidos exitosamente: {uploaded}/{total_files}")

    if errors:
        print(f"Errores: {len(errors)}")
        for path, err in errors[:10]:
            print(f"  - {path}: {err}")
        if len(errors) > 10:
            print(f"  ... y {len(errors) - 10} más")

    print(f"\nEstructura en R2: s3://{R2_BUCKET_NAME}/{R2_PREFIX}/")


if __name__ == "__main__":
    upload_parquet_files()
