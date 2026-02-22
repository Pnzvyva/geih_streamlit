import duckdb

DB_PATH = "data/geih.duckdb"

con = duckdb.connect(DB_PATH)

CATEGORIES = [
    "caracteristicas",
    "hogar",
    "fuerza_trabajo",
    "ocupados",
    "no_ocupados",
    "inactivos",
    "migracion",
    "otras_actividades",
    "otros_ingresos"
]


def list_tables():
    return [t[0] for t in con.execute("SHOW TABLES").fetchall()]


def get_available_categories_and_types(year: int):
    """
    Detecta categorías y tipos EXISTENTES dentro de DuckDB.
    Incluye excepción: 2020 usa formato TOTAL igual que 2022+.
    """
    tablas = list_tables()
    disponibles = []

    for cat in CATEGORIES:
        tipos = []

        # Años 2007–2021 (EXCEPTO 2020)
        if 2007 <= year <= 2021 and year != 2020:
            if f"{cat}_{year}_cabecera" in tablas:
                tipos.append("cabecera")
            if f"{cat}_{year}_resto" in tablas:
                tipos.append("resto")

        # Años 2022+, Y TAMBIÉN 2020 → TOTAL
        if year >= 2022 or year == 2020:
            if f"{cat}_{year}_total" in tablas:
                tipos.append("total")

        if tipos:
            disponibles.append((cat, tipos))

    return disponibles

