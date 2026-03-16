"""
Script para probar la conexion a Cloudflare R2.
Verifica que las credenciales esten configuradas correctamente.
"""
import sys
from config import (
    R2_ENDPOINT_URL,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME,
    validate_config
)


def test_connection():
    """Prueba la conexion a Cloudflare R2."""
    print("=" * 60)
    print("TEST DE CONEXION A CLOUDFLARE R2")
    print("=" * 60)

    # 1. Validar configuracion
    print("\n1. Validando configuracion...")
    try:
        validate_config()
        print("   [OK] Configuracion valida")
    except ValueError as e:
        print(f"   [ERROR] {e}")
        return False

    # Mostrar configuracion (ocultando credenciales sensibles)
    print(f"\n   Endpoint URL: {R2_ENDPOINT_URL}")
    print(f"   Access Key ID: {'*' * 8}{R2_ACCESS_KEY_ID[-4:] if R2_ACCESS_KEY_ID else 'NO CONFIGURADO'}")
    print(f"   Secret Key: {'*' * 20} (oculto)")
    print(f"   Bucket: {R2_BUCKET_NAME}")

    # 2. Probar conexion con boto3
    print("\n2. Probando conexion con R2...")
    try:
        import boto3
        from botocore.config import Config

        s3 = boto3.client(
            "s3",
            endpoint_url=R2_ENDPOINT_URL,
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4")
        )
        print("   [OK] Cliente S3 creado exitosamente")

        # 3. Verificar acceso al bucket especifico (sin listar todos los buckets)
        print(f"\n3. Verificando acceso al bucket '{R2_BUCKET_NAME}'...")
        try:
            # Intentar listar objetos del bucket especifico
            response = s3.list_objects_v2(Bucket=R2_BUCKET_NAME, MaxKeys=1)
            print(f"   [OK] Acceso al bucket '{R2_BUCKET_NAME}' confirmado")
        except Exception as e:
            error_msg = str(e)
            if "NoSuchBucket" in error_msg:
                print(f"   [ERROR] El bucket '{R2_BUCKET_NAME}' no existe")
            elif "AccessDenied" in error_msg:
                print(f"   [ERROR] Acceso denegado al bucket '{R2_BUCKET_NAME}'")
                print(f"   Verifica que el token tenga permisos para este bucket")
            else:
                print(f"   [ERROR] {e}")
            return False

        # 4. Listar objetos en el bucket
        print(f"\n4. Listando objetos en '{R2_BUCKET_NAME}'...")
        try:
            response = s3.list_objects_v2(Bucket=R2_BUCKET_NAME)

            if 'Contents' in response and response['Contents']:
                print(f"   [OK] {len(response['Contents'])} objeto(s) encontrado(s):\n")
                for obj in response['Contents'][:10]:  # Mostrar maximo 10
                    size_mb = obj['Size'] / (1024 * 1024)
                    print(f"      - {obj['Key']} ({size_mb:.2f} MB)")

                if len(response['Contents']) > 10:
                    print(f"      ... y {len(response['Contents']) - 10} mas")
            else:
                print("   [INFO] Bucket vacio (sin objetos)")

        except Exception as e:
            print(f"   [ERROR] Error al listar objetos: {e}")
            return False

        print("\n" + "=" * 60)
        print("[OK] TODAS LAS PRUEBAS PASARON CORRECTAMENTE")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"   [ERROR] Error de conexion: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
