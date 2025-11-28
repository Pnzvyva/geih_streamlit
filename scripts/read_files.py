import os
import json
import pandas as pd
import re
import unicodedata

# ============================================================
# 1. RUTAS BASE (OneDrive + Microdatos_GEIH)
# ============================================================

def get_onedrive_path() -> str:
    """
    Devuelve la ruta base del OneDrive institucional.
    Primero intenta con la variable de entorno OneDriveCommercial.
    Si no existe, intenta con la ruta típica de Windows.
    """
    path = os.environ.get("OneDriveCommercial")

    if not path:
        home = os.path.expanduser("~")
        candidate = os.path.join(home, "OneDrive - Universidad del Norte (1)")
        if os.path.exists(candidate):
            path = candidate
        else:
            raise EnvironmentError(
                "No se pudo detectar la ruta de OneDrive.\n"
                "Verifica que OneDrive esté configurado o ajusta manualmente esta función."
            )
    return path


def get_base_path() -> str:
    """
    Ruta base donde está la carpeta Microdatos_GEIH dentro de OneDrive.
    Ejemplo:
    C:/Users/juank/OneDrive - Universidad del Norte (1)/Microdatos_GEIH
    """
    return os.path.join(get_onedrive_path(), "Microdatos_GEIH")


# ============================================================
# 2. CARGA DEL MAPPING DE ARCHIVOS
# ============================================================

def load_mapping() -> dict:
    """
    Carga el diccionario de nombres de archivos desde:
    data/dictionary/mapping_files.json
    """
    mapping_path = os.path.join("data", "dictionary", "mapping_files.json")
    if not os.path.exists(mapping_path):
        raise FileNotFoundError(
            f"No se encontró mapping_files.json en {mapping_path}. "
            "Asegúrate de que exista y tenga el formato correcto."
        )

    with open(mapping_path, "r", encoding="utf-8") as f:
        return json.load(f)


MAPPING = load_mapping()

# MAPPING tiene esta estructura (resumen):
# {
#   "categorias": ["caracteristicas", "hogar", "ocupados", ...],
#   "2007_2021": {
#       "caracteristicas": [
#           "Caracteristicas_Cabecera_Anual.csv",
#           "Caracteristicas_Resto_Anual.csv"
#       ],
#       ...
#   },
#   "2022_2025": {
#       "caracteristicas": "Caracteristicas_generales_seguridad_social_Anual.csv",
#       ...
#   }
# }


# ============================================================
# 3. LECTURA FLEXIBLE DE CSV (delimitador automático)
# ============================================================

def read_csv_flexible(path: str) -> pd.DataFrame:
    """
    Lee un CSV permitiendo detectar automáticamente el delimitador.
    Usa engine='python' para que sep=None funcione.

    Todas las columnas se leen como texto (dtype=str) para evitar
    problemas de tipos entre años.
    """
    return pd.read_csv(
        path,
        sep=None,           # autodetección de delimitador
        engine="python",    # necesario para sep=None
        dtype=str
    )


# ============================================================
# 4. UTILIDADES PARA CATEGORÍAS/TIPOS POR AÑO
# ============================================================

def _get_scheme_for_year(year: int) -> str:
    # 2020 tiene el mismo formato que 2022-2025
    if year == 2020:
        return "2022_2025"
    return "2007_2021" if year <= 2021 else "2022_2025"



def get_year_folder(year: int) -> str:
    """
    Devuelve la ruta de la carpeta del año dentro de Microdatos_GEIH.
    Ejemplo:
    C:/.../Microdatos_GEIH/2007/Consolidado_Anual
    """
    return os.path.join(get_base_path(), str(year), "Consolidado_Anual")


def get_available_categories_and_types(year: int):
    """
    Devuelve una lista de tuplas (categoria, [tipos]) para las que
    REALMENTE existen archivos en disco para ese año.

    tipos puede ser:
    - 'cabecera', 'resto'    (para 2007-2021)
    - 'total'                (para 2022-2025, un solo archivo)
    """
    scheme = _get_scheme_for_year(year)
    year_path = get_year_folder(year)

    if not os.path.exists(year_path):
        # Si ni siquiera existe la carpeta del año, devolvemos vacío
        return []

    categorias_validas = []

    for categoria in MAPPING["categorias"]:
        if categoria not in MAPPING[scheme]:
            # Esa categoría no aplica en este esquema
            continue

        entry = MAPPING[scheme][categoria]

        tipos_existentes = []

        # Caso 2007_2021: lista [Cabecera, Resto]
        if isinstance(entry, list):
            nombres = entry

            # idx 0 = cabecera
            cabecera_path = os.path.join(year_path, nombres[0])
            if os.path.exists(cabecera_path):
                tipos_existentes.append("cabecera")

            # idx 1 = resto
            if len(nombres) > 1:
                resto_path = os.path.join(year_path, nombres[1])
                if os.path.exists(resto_path):
                    tipos_existentes.append("resto")

        # Caso 2022_2025: un solo archivo "total"
        else:
            total_path = os.path.join(year_path, entry)
            if os.path.exists(total_path):
                tipos_existentes.append("total")

        if tipos_existentes:
            categorias_validas.append((categoria, tipos_existentes))

    return categorias_validas


# ============================================================
# 5. OBTENER RUTA DE ARCHIVO PARA (AÑO, CATEGORÍA, TIPO)
# ============================================================

def get_file_path(year: int, categoria: str, tipo: str | None = None) -> tuple[str, str]:
    """
    Devuelve la ruta al archivo CSV correspondiente a (año, categoría, tipo).

    - Para 2007-2021:
        tipo debe ser 'cabecera' o 'resto'.
    - Para 2022-2025:
        tipo puede ser None o 'total' (internamente se usa 'total').

    Retorna:
        (ruta_archivo, tipo_final)
    """
    scheme = _get_scheme_for_year(year)
    year_path = get_year_folder(year)

    if categoria not in MAPPING[scheme]:
        raise ValueError(f"La categoría '{categoria}' no existe en el esquema {scheme}.")

    entry = MAPPING[scheme][categoria]

    # Años 2007-2021: lista [cabecera, resto]
    if isinstance(entry, list):
        if tipo not in ("cabecera", "resto"):
            raise ValueError(
                f"Para el año {year}, la categoría '{categoria}' requiere tipo "
                "='cabecera' o 'resto'."
            )
        idx = 0 if tipo == "cabecera" else 1
        filename = entry[idx]
        path = os.path.join(year_path, filename)
        tipo_final = tipo

    # Años 2022-2025: un solo archivo 'total'
    else:
        filename = entry
        path = os.path.join(year_path, filename)
        tipo_final = "total"

    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    return path, tipo_final


#RENOMBRE DE COLUMNA DUPLICADA
def normalize_for_duckdb(col):
    """
    Convierte nombres a un formato seguro para DuckDB:
    - minúsculas
    - alfanuméricos y guiones
    """
    col = col.strip()
    col = col.replace("\ufeff", "")   # BOM
    col = unicodedata.normalize("NFKD", col)
    col = col.lower()
    col = re.sub(r"[^a-z0-9_]", "_", col)
    return col


def ensure_unique_columns(df):
    """
    Crea un mapping seguro para DuckDB:
    nombres originales → nombres seguros y únicos
    """
    new_cols = []
    seen = {}

    for col in df.columns:
        base = normalize_for_duckdb(col)

        if base in seen:
            seen[base] += 1
            safe = f"{base}_{seen[base]}"
        else:
            seen[base] = 0
            safe = base

        new_cols.append(safe)

    # guardamos el mapping original → seguro
    df.columns = new_cols
    return df

# ============================================================
# 6. CARGA DE DATAFRAME PARA (AÑO, CATEGORÍA, TIPO)
# ============================================================

def load_category(year: int, categoria: str, tipo: str | None = None) -> pd.DataFrame:
    """
    Carga los datos de una combinación (año, categoría, tipo) en un DataFrame.

    - Lee el CSV correcto desde OneDrive.
    - No intenta alinear columnas con otros años.
    - Agrega columnas de metadato: 'ano', 'categoria', 'tipo'.

    Ejemplos de uso:
        df = load_category(2007, "ocupados", "cabecera")
        df = load_category(2019, "hogar", "resto")
        df = load_category(2023, "ocupados")  # tipo 'total' implícito
    """
    path, tipo_final = get_file_path(year, categoria, tipo)

    print(f"Leyendo {path}")
    df = read_csv_flexible(path)

    # Metadatos
    df["ano"] = year
    df["categoria"] = categoria
    df["tipo"] = tipo_final

    # Ahora SÍ aplicar renombrado de duplicados (incluyendo metadatos)
    df = ensure_unique_columns(df)

    return df


# ============================================================
# 7. UTILIDAD: GENERAR NOMBRE DE TABLA PARA DUCKDB
# ============================================================

def make_table_name(categoria: str, year: int, tipo: str) -> str:
    """
    Genera un nombre de tabla estable para DuckDB a partir de:
    - categoria: 'ocupados', 'hogar', 'caracteristicas', etc.
    - year: 2007, 2010, 2023...
    - tipo: 'cabecera', 'resto' o 'total'

    Ejemplo:
        make_table_name("ocupados", 2007, "cabecera") -> "ocupados_2007_cabecera"
    """
    return f"{categoria}_{year}_{tipo}".replace(" ", "_")


# ============================================================
# 8. UTILIDAD: ITERAR TODAS LAS COMBINACIONES VÁLIDAS DE UN AÑO
# ============================================================

def iter_year_data(year: int):
    """
    Generador que recorre todas las combinaciones (categoria, tipo)
    para las que existen archivos en disco para un año dado, y
    devuelve (categoria, tipo, table_name, df).

    Esto será muy útil en build_duckdb.py para poblar la base.
    """
    cat_tipos = get_available_categories_and_types(year)

    for categoria, tipos in cat_tipos:
        for tipo in tipos:
            df = load_category(year, categoria, tipo)
            df = ensure_unique_columns(df)    # renombrado aquí sí o sí
            table_name = make_table_name(categoria, year, tipo)
            yield categoria, tipo, table_name, df



