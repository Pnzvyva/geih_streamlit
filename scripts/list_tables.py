import duckdb
import re

DB_PATH = "data/geih.duckdb"

# ============================================================
# Funciones auxiliares
# ============================================================

def conectar():
    return duckdb.connect(DB_PATH)


def listar_tablas(con):
    """
    Devuelve una lista con los nombres de todas las tablas en la base.
    """
    rows = con.execute("SHOW TABLES;").fetchall()
    return [r[0] for r in rows]


def filtrar_tablas(tablas, categoria=None, year=None, tipo=None):
    """
    Filtra por:
    - categoría: 'ocupados', 'hogar', 'caracteristicas', etc.
    - year: 2007, 2010, 2023...
    - tipo: 'cabecera', 'resto', 'total'

    Las tablas siguen formato:
    categoria_year_tipo
    """
    filtradas = tablas

    if categoria:
        filtradas = [t for t in filtradas if t.startswith(categoria + "_")]

    if year:
        filtradas = [t for t in filtradas if f"_{year}_" in t]

    if tipo:
        filtradas = [t for t in filtradas if t.endswith("_" + tipo)]

    return filtradas


def info_tabla(con, tabla):
    """
    Retorna info básica de una tabla: filas y columnas.
    """
    filas = con.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
    cols = con.execute(f"PRAGMA table_info('{tabla}')").fetchall()
    columnas = [c[1] for c in cols]
    return filas, columnas


# ============================================================
# Script principal
# ============================================================

def main():
    con = conectar()

    print("\n===================================")
    print("     LISTADO DE TABLAS GEIH")
    print("===================================\n")

    tablas = listar_tablas(con)
    print(f"Total tablas: {len(tablas)}\n")

    # Mostrar todas
    for t in tablas:
        print(f"- {t}")
    print("\n")

    # Modo interactivo (básico)
    print("Puedes aplicar filtros opcionales:")
    print("Ejemplos:")
    print("  categoria=ocupados")
    print("  year=2017")
    print("  tipo=cabecera")
    print("  categoria=hogar year=2020")
    print("  categoria=ocupados tipo=total")
    print("-----------------------------------")

    entrada = input("\nFiltros (o Enter para salir): ")

    if entrada.strip() == "":
        print("\nSaliendo...\n")
        return

    # Parsear filtros estilo "categoria=ocupados year=2020"
    filtros = dict(re.findall(r'(\w+)=([\w_]+)', entrada))

    categoria = filtros.get("categoria")
    year = int(filtros["year"]) if "year" in filtros else None
    tipo = filtros.get("tipo")

    print("\n--- RESULTADO FILTRADO ---\n")

    filtradas = filtrar_tablas(tablas, categoria, year, tipo)

    for t in filtradas:
        filas, columnas = info_tabla(con, t)
        print(f"Tabla: {t}")
        print(f"  Filas: {filas}")
        print(f"  Columnas: {len(columnas)} → {columnas[:6]}{'...' if len(columnas)>6 else ''}")
        print("")

    print("\nFin.\n")


if __name__ == "__main__":
    main()
