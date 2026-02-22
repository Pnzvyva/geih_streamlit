import os
import requests

# =========================================================
# CONFIGURACIÓN
# =========================================================

# URL pública del archivo en Backblaze B2
REMOTE_URL = "https://f003.backblazeb2.com/file/geih-storage/geih.duckdb"

# Ruta local donde debe vivir el archivo
LOCAL_PATH = "data/geih.duckdb"


# =========================================================
# DESCARGA AUTOMÁTICA DEL ARCHIVO
# =========================================================

def ensure_duckdb_exists():
    """
    Descarga el archivo geih.duckdb desde Backblaze B2 si no existe localmente.
    No se vuelve a descargar en cada ejecución.
    Railway mantiene el archivo en el contenedor mientras viva el servicio.
    """
    os.makedirs("data", exist_ok=True)

    if os.path.exists(LOCAL_PATH):
        print("✔ geih.duckdb ya está presente.")
        return

    print("⬇ Descargando geih.duckdb desde Backblaze B2...")

    with requests.get(REMOTE_URL, stream=True) as r:
        r.raise_for_status()
        with open(LOCAL_PATH, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):  # 1MB
                f.write(chunk)

    print("✔ Descarga completada.")
