# Metadatos de Base de Datos (db_metadata.py)

## Descripción

Define las categorías de datos disponibles y proporciona funciones para detectar qué tablas existen en la base de datos DuckDB local.

## Uso Principal

Este módulo se usa principalmente en:
- `r2_connector.py`: Para la detección de categorías disponibles en R2
- Scripts de mantenimiento: Para iterar sobre categorías

## Constantes

### `CATEGORIES`

Lista de las 9 categorías de datos de la GEIH:

```python
CATEGORIES = [
    "caracteristicas",      # Datos demográficos, educación, salud
    "hogar",               # Información del hogar y vivienda
    "fuerza_trabajo",      # Población en edad de trabajar
    "ocupados",            # Personas con empleo
    "no_ocupados",         # Personas desempleadas
    "inactivos",           # Personas fuera de la fuerza laboral
    "migracion",           # Datos de migración (desde 2022)
    "otras_actividades",   # Otras formas de trabajo
    "otros_ingresos"       # Ingresos adicionales e impuestos
]
```

### `DB_PATH`

Ruta a la base de datos DuckDB local:
```python
DB_PATH = "data/geih.duckdb"
```

## Funciones

### `list_tables()`

Lista todas las tablas en la base de datos DuckDB local.

**Retorna:**
- `list`: Lista de nombres de tablas

**Ejemplo:**
```python
tablas = list_tables()
# Retorna: ["caracteristicas_2007_cabecera", "caracteristicas_2007_resto", ...]
```

### `get_available_categories_and_types(year)`

Detecta categorías y tipos existentes en DuckDB local para un año específico.

**Parámetros:**
- `year` (int): Año a consultar

**Retorna:**
- `list`: Lista de tuplas `(categoria, [tipos])`

**Lógica:**
- Años 2007-2021 (excepto 2020): Busca tablas `_cabecera` y `_resto`
- Años 2022+ y 2020: Busca tablas `_total`

**Ejemplo:**
```python
# Para año 2019
disponibles = get_available_categories_and_types(2019)
# Retorna: [("caracteristicas", ["cabecera", "resto"]), ...]

# Para año 2020
disponibles = get_available_categories_and_types(2020)
# Retorna: [("caracteristicas", ["total"]), ...]
```

## Notas

- Este módulo trabaja con la base de datos **local** (DuckDB)
- Para R2, usar `r2_connector.get_available_categories_and_types_from_r2()`
- La constante `CATEGORIES` es usada por ambos módulos

## Archivos Relacionados

- `r2_connector.py`: Usa `CATEGORIES` para detección en R2
- `build_duckdb.py`: Crea las tablas que este módulo lista
