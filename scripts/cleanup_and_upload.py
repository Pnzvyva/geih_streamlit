"""Limpia archivos mal subidos y sube los faltantes"""
import boto3
from botocore.config import Config
import urllib3
import os
from scripts.config import (
    R2_ENDPOINT_URL,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME
)

urllib3.disable_warnings()

s3 = boto3.client(
    's3',
    endpoint_url=R2_ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    config=Config(signature_version='s3v4'),
    verify=False
)

# 1. Eliminar archivos con nombres incorrectos (que contienen ______)
print("Eliminando archivos con nombres incorrectos...")
response = s3.list_objects_v2(Bucket=R2_BUCKET_NAME, Prefix='parquet/', MaxKeys=1000)
if 'Contents' in response:
    for obj in response['Contents']:
        key = obj['Key']
        if '______' in key or (key.endswith('.parquet') and key.count('/') == 1):
            print(f"  Eliminando: {key}")
            s3.delete_object(Bucket=R2_BUCKET_NAME, Key=key)

# 2. Verificar qué archivos faltan
print("\nVerificando archivos locales vs R2...")
response = s3.list_objects_v2(Bucket=R2_BUCKET_NAME, Prefix='parquet/', MaxKeys=1000)
r2_files = set()
if 'Contents' in response:
    for obj in response['Contents']:
        key = obj['Key']
        if key.endswith('.parquet') and '______' not in key:
            r2_files.add(key)

LOCAL_PARQUET_DIR = "parquet_export"
local_files = []
for root, dirs, files in os.walk(LOCAL_PARQUET_DIR):
    for file in files:
        if file.endswith('.parquet') and '______' not in file:
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, LOCAL_PARQUET_DIR)
            if os.path.dirname(rel_path):
                r2_key = f"parquet/{rel_path}".replace("\\", "/")
                local_files.append((local_path, r2_key))

# 3. Subir archivos faltantes
print(f"\nArchivos en R2: {len(r2_files)}")
print(f"Archivos locales: {len(local_files)}")

missing = [(lp, rk) for lp, rk in local_files if rk not in r2_files]
print(f"Archivos faltantes: {len(missing)}")

if missing:
    print("\nSubiendo archivos faltantes...")
    for local_path, r2_key in missing:
        print(f"  Subiendo: {r2_key}")
        try:
            s3.upload_file(local_path, R2_BUCKET_NAME, r2_key)
        except Exception as e:
            print(f"    [ERROR] {e}")

print("\nListo!")
