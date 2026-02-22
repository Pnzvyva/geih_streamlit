import os
from b2sdk.v2 import InMemoryAccountInfo, B2Api

PARQUET_DIR = "parquet_export"  # donde están tus parquet
BUCKET_NAME = "tu-bucket"       # cámbialo

APPLICATION_KEY_ID = "YOUR_KEY_ID"
APPLICATION_KEY = "YOUR_APPLICATION_KEY"

def upload_all_parquets():
    # Autenticación
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)

    print("🔵 Autenticando con Backblaze B2...")
    b2_api.authorize_account("production", APPLICATION_KEY_ID, APPLICATION_KEY)

    # Seleccionar bucket
    bucket = b2_api.get_bucket_by_name(BUCKET_NAME)
    print(f"Subiendo archivos a Bucket: {BUCKET_NAME}\n")

    # Recorrer directorio exportado
    for root, dirs, files in os.walk(PARQUET_DIR):
        for filename in files:
            if not filename.endswith(".parquet"):
                continue

            local_path = os.path.join(root, filename)
            remote_path = f"parquet/{filename}"  # carpeta remota lógica

            print(f"⬆ Subiendo: {filename} ...")

            bucket.upload_local_file(
                local_file=local_path,
                file_name=remote_path
            )

    print("Subida completada a Backblaze B2.")

if __name__ == "__main__":
    upload_all_parquets()
