import duckdb
from read_files import iter_year_data, ensure_unique_columns

DB_PATH = "data/geih.duckdb"

print("Conectando a la base existente...")
con = duckdb.connect(DB_PATH)

print("\n=== Procesando año 2020 ===\n")

for categoria, tipo, table_name, df in iter_year_data(2020):
    print(f"Cargando tabla: {table_name}")

    # asegurar nombres seguros
    df = df.copy()
    df.columns = [c.strip().replace("\ufeff","") for c in df.columns]
    df = ensure_unique_columns(df)

    # crear tabla si no existe
    cols = ", ".join([f'"{c}" TEXT' for c in df.columns])
    con.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({cols});")

    # insert bulk
    con.register("temp_df", df)
    con.execute(f"INSERT INTO {table_name} SELECT * FROM temp_df")
    con.unregister("temp_df")

con.close()

print("Año 2020 añadido correctamente.")
