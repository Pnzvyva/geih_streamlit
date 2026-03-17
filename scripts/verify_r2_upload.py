"""Verifica los archivos subidos a R2"""
import boto3
from botocore.config import Config
import urllib3
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

# Listar objetos en el prefijo parquet
response = s3.list_objects_v2(Bucket=R2_BUCKET_NAME, Prefix='parquet/', MaxKeys=1000)
if 'Contents' in response:
    print(f'Total archivos subidos: {len(response["Contents"])}')
    # Contar por categoría
    categorias = {}
    for obj in response['Contents']:
        key = obj['Key']
        parts = key.split('/')
        if len(parts) >= 2:
            cat = parts[1]
            categorias[cat] = categorias.get(cat, 0) + 1

    print('\nArchivos por categoría:')
    for cat, count in sorted(categorias.items()):
        print(f'  {cat}: {count} archivos')
else:
    print('No se encontraron archivos')
