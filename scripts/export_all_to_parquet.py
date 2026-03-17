"""
Exporta todas las tablas de geih.duckdb a archivos parquet organizados.
Estructura: parquet_export/{categoria}/{año}/{tipo}.parquet
"""
import duckdb
import os
import re
from pathlib import Path

DB_PATH = "data/geih.duckdb"
OUTPUT_BASE = "parquet_export"


def parse_table_name(table_name):
    """
    Parsea el nombre de tabla en formato: categoria_año_tipo
    Ejemplo: caracteristicas_2020_total -> (caracteristicas, 2020, total)
             ocupados_2019_cabecera -> (ocupados, 2019, cabecera)
    """
    # Patrón: categoria_año_tipo
    match = re.match(r'^(.+)_(\d{4})_(cabecera|resto|total)$', table_name)
    if match:
        categoria = match.group(1)
        year = match.group(2)
        tipo = match.group(3)
        return categoria, year, tipo
    return None, None, None


def export_table_to_parquet(con, table_name, output_path):
    """Exporta una tabla a archivo parquet."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    query = f"COPY (SELECT * FROM {table_name}) TO '{output_path}' (FORMAT PARQUET)"
    con.execute(query)
    print(f"  [OK] Exportado: {table_name} -> {output_path}")


def main():
    print("=" * 60)
    print("EXPORTACIÓN DE TABLAS GEIH A PARQUET")
    print("=" * 60)

    if not os.path.exists(DB_PATH):
        print(f"[ERROR] No se encontró {DB_PATH}")
        return

    # Conectar a la base de datos
    print(f"\nConectando a {DB_PATH}...")
    con = duckdb.connect(DB_PATH)

    # Obtener todas las tablas
    tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
    print(f"Total de tablas encontradas: {len(tables)}\n")

    # Crear directorio base
    os.makedirs(OUTPUT_BASE, exist_ok=True)

    # Contadores
    exported = 0
    errors = []

    # Exportar cada tabla
    for table in sorted(tables):
        categoria, year, tipo = parse_table_name(table)

        if categoria and year and tipo:
            # Construir ruta: parquet_export/categoria/año/tipo.parquet
            output_path = os.path.join(OUTPUT_BASE, categoria, year, f"{tipo}.parquet")

            try:
                export_table_to_parquet(con, table, output_path)
                exported += 1
            except Exception as e:
                error_msg = f"[ERROR] exportando {table}: {e}"
                print(f"  {error_msg}")
                errors.append(error_msg)
        else:
            print(f"  [WARN] Formato no reconocido: {table}")
            errors.append(f"Formato no reconocido: {table}")

    con.close()

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Tablas exportadas exitosamente: {exported}/{len(tables)}")

    if errors:
        print(f"Errores/Advertencias: {len(errors)}")
        for err in errors[:10]:  # Mostrar primeros 10 errores
            print(f"  - {err}")
        if len(errors) > 10:
            print(f"  ... y {len(errors) - 10} más")

    print(f"\nArchivos guardados en: {os.path.abspath(OUTPUT_BASE)}")
    print("Estructura: parquet_export/{categoria}/{año}/{tipo}.parquet")


if __name__ == "__main__":
    main()
