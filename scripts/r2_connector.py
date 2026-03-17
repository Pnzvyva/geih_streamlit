"""
Módulo para conectar con R2 y leer archivos parquet usando DuckDB.
"""
import duckdb
import os
from scripts.config import (
    R2_ENDPOINT_URL,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME
)

# Extraer el host del endpoint
R2_HOST = R2_ENDPOINT_URL.replace("https://", "").replace("http://", "")


def get_r2_connection():
    """
    Crea una conexión DuckDB configurada para leer desde R2.
    Retorna la conexión y configura httpfs.
    """
    con = duckdb.connect(":memory:")

    # Instalar y cargar la extensión httpfs si no está instalada
    try:
        con.execute("INSTALL httpfs;")
    except:
        pass  # Ya está instalada
    con.execute("LOAD httpfs;")

    # Configurar credenciales S3 para R2
    con.execute(f"SET s3_endpoint='{R2_HOST}';")
    con.execute(f"SET s3_access_key_id='{R2_ACCESS_KEY_ID}';")
    con.execute(f"SET s3_secret_access_key='{R2_SECRET_ACCESS_KEY}';")
    con.execute("SET s3_use_ssl=true;")
    con.execute("SET s3_url_style='path';")
    con.execute(f"SET s3_region='auto';")

    return con


def get_parquet_path(categoria, year, tipo):
    """
    Genera la ruta S3 para un archivo parquet.
    Ejemplo: s3://bucket/parquet/caracteristicas/2020/total.parquet
    """
    return f"s3://{R2_BUCKET_NAME}/parquet/{categoria}/{year}/{tipo}.parquet"


def create_table_view(con, categoria, year, tipo):
    """
    Crea una vista en DuckDB que apunta al archivo parquet en R2.
    Retorna el nombre de la vista creada.
    """
    table_name = f"{categoria}_{year}_{tipo}"
    parquet_path = get_parquet_path(categoria, year, tipo)

    # Crear vista que lee desde el parquet en R2
    con.execute(f"""
        CREATE OR REPLACE VIEW {table_name} AS
        SELECT * FROM read_parquet('{parquet_path}')
    """)

    return table_name


def get_available_categories_and_types_from_r2(con, year):
    """
    Detecta categorías y tipos disponibles en R2 para un año específico.
    Verifica la existencia de los archivos parquet en R2.
    """
    from scripts.db_metadata import CATEGORIES

    disponibles = []

    for cat in CATEGORIES:
        tipos = []

        # Años 2007–2021 (EXCEPTO 2020)
        if 2007 <= year <= 2021 and year != 2020:
            try:
                parquet_path = get_parquet_path(cat, year, "cabecera")
                con.execute(f"SELECT 1 FROM read_parquet('{parquet_path}') LIMIT 1")
                tipos.append("cabecera")
            except:
                pass
            try:
                parquet_path = get_parquet_path(cat, year, "resto")
                con.execute(f"SELECT 1 FROM read_parquet('{parquet_path}') LIMIT 1")
                tipos.append("resto")
            except:
                pass

        # Años 2022+, Y TAMBIÉN 2020 → TOTAL
        if year >= 2022 or year == 2020:
            try:
                parquet_path = get_parquet_path(cat, year, "total")
                con.execute(f"SELECT 1 FROM read_parquet('{parquet_path}') LIMIT 1")
                tipos.append("total")
            except:
                pass

        if tipos:
            disponibles.append((cat, tipos))

    return disponibles
