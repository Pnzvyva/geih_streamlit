import duckdb
import os

DB_PATH = "data/geih.duckdb"       # tu base original
OUTPUT_DIR = "parquet_export"      # carpeta donde se guardarán los parquet

# Crear carpeta si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("🔵 Conectando a DuckDB...")
con = duckdb.connect(DB_PATH)

print("Exportando todas las tablas a Parquet...")
con.execute(f"EXPORT DATABASE '{OUTPUT_DIR}' (FORMAT PARQUET);")

print("Exportación completada.")
print(f"Archivos generados en: {OUTPUT_DIR}")
