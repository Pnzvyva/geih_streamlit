import os
import duckdb
import datetime
from read_files import iter_year_data, ensure_unique_columns

# ============================================================
# CONFIGURACIÓN
# ============================================================

DB_PATH = "data/geih.duckdb"
LOGS_DIR = "logs"

YEARS = list(range(2007, 2026))  # 2007–2025

# Crear carpeta logs si no existe
os.makedirs(LOGS_DIR, exist_ok=True)

# Preparar archivo de log con fecha
log_path = os.path.join(
    LOGS_DIR,
    f"build_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.log"
)
log_file = open(log_path, "w", encoding="utf-8")


def log(msg: str):
    """
    Guarda en archivo y muestra en pantalla.
    """
    print(msg)
    log_file.write(msg + "\n")


# ============================================================
# FUNCIONES AUXILIARES PARA DUCKDB
# ============================================================

def create_table_if_needed(df, table_name, con):
    """
    Crea la tabla con las columnas del DataFrame.
    Solo se ejecuta si la tabla NO existe.
    """
    columns = ", ".join([f'"{c}" TEXT' for c in df.columns])
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"
    con.execute(sql)


def insert_into_table(df, table_name, con):
    """
    Inserta el DataFrame completo de forma optimizada.
    """
    # Registrar el DF en memoria
    con.register("temp_df", df)

    # Insertar en DuckDB
    con.execute(f"INSERT INTO {table_name} SELECT * FROM temp_df")

    # Liberar registro
    con.unregister("temp_df")


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

log("=================================================")
log("   CREACIÓN DE BASE DE DATOS GEIH (DuckDB)")
log("=================================================\n")

log(f"Conectando a {DB_PATH}...\n")
con = duckdb.connect(DB_PATH)

for year in YEARS:

    log(f"\n==============================")
    log(f"Procesando año {year}")
    log("==============================")

    for categoria, tipo, table_name, df in iter_year_data(year):

        # ============================================
        # 🔥 PASO CRÍTICO: GARANTIZAR COLUMNAS ÚNICAS
        # ============================================
        df = df.copy()

        # eliminar posiciones en blanco, '\ufeff', espacios invisibles
        df.columns = [c.strip().replace("\ufeff", "") for c in df.columns]

        # renombrado de duplicados
        df = ensure_unique_columns(df)


        log(f"\n→ Tabla: {table_name}")
        log(f"   Categoría: {categoria}")
        log(f"   Tipo: {tipo}")
        log(f"   Filas: {len(df)}")
        log(f"   Columnas: {len(df.columns)}")

        try:
            log(f"   Columnas con las que se crea la tabla: {df.columns.tolist()}")
            create_table_if_needed(df, table_name, con)
            insert_into_table(df, table_name, con)
            log("✔ Insertado correctamente")
        except Exception as e:
            log(f"❌ ERROR INSERTANDO: {e}")

log("\n===========================================")
log(" Construcción finalizada correctamente.")
log(f" Archivo log: {log_path}")
log("===========================================\n")

log_file.close()
con.close()

