# Conector R2 (r2_connector.py)

## Descripción

Módulo para conectar con Cloudflare R2 y leer archivos Parquet usando DuckDB. Proporciona una interfaz simplificada para acceder a los datos de la GEIH almacenados en la nube.

## Funciones Principales

### `get_r2_connection()`

Crea una conexión DuckDB configurada para leer desde R2.

**Retorna:**
- `duckdb.DuckDBPyConnection`: Conexión configurada

**Configuración aplicada:**
- Instala y carga extensión `httpfs`
- Configura endpoint S3 (R2)
- Establece credenciales de acceso
- Habilita SSL
- Usa estilo de URL path

**Ejemplo:**
```python
con = get_r2_connection()
df = con.execute("SELECT * FROM read_parquet('s3://bucket/file.parquet')").df()
```

### `get_parquet_path(categoria, year, tipo)`

Genera la ruta S3 para un archivo Parquet.

**Parámetros:**
- `categoria` (str): Nombre de la categoría (ej: "caracteristicas")
- `year` (int): Año de los datos (ej: 2020)
- `tipo` (str): Tipo de datos ("cabecera", "resto", "total")

**Retorna:**
- `str`: Ruta S3 completa

**Ejemplo:**
```python
path = get_parquet_path("caracteristicas", 2020, "total")
# Retorna: s3://microdata-geih-duckdb/parquet/caracteristicas/2020/total.parquet
```

### `create_table_view(con, categoria, year, tipo)`

Crea una vista en DuckDB que apunta al archivo Parquet en R2.

**Parámetros:**
- `con`: Conexión DuckDB
- `categoria` (str): Categoría de datos
- `year` (int): Año
- `tipo` (str): Tipo de datos

**Retorna:**
- `str`: Nombre de la vista creada

**Ejemplo:**
```python
con = get_r2_connection()
table_name = create_table_view(con, "ocupados", 2020, "total")
# Crea vista: ocupados_2020_total
df = con.execute(f"SELECT * FROM {table_name}").df()
```

### `get_available_categories_and_types_from_r2(con, year)`

Detecta qué categorías y tipos están disponibles en R2 para un año específico.

**Parámetros:**
- `con`: Conexión DuckDB
- `year` (int): Año a consultar

**Retorna:**
- `list`: Lista de tuplas `(categoria, [tipos])`

**Ejemplo:**
```python
available = get_available_categories_and_types_from_r2(con, 2020)
# Retorna: [("caracteristicas", ["total"]), ("hogar", ["total"]), ...]
```

**Lógica de detección:**
- Años 2007-2021 (excepto 2020): Busca `cabecera` y `resto`
- Años 2022+ y 2020: Busca `total`

## Constantes

### `R2_HOST`

Host extraído del endpoint URL (sin https://).

## Dependencias

```python
import duckdb
import os
from scripts.config import (
    R2_ENDPOINT_URL,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME
)
```

## Flujo de Uso Típico

```python
# 1. Obtener conexión
con = get_r2_connection()

# 2. Verificar disponibles
available = get_available_categories_and_types_from_r2(con, 2020)

# 3. Crear vista para tabla específica
table_name = create_table_view(con, "caracteristicas", 2020, "total")

# 4. Consultar datos
df = con.execute(f"SELECT * FROM {table_name} LIMIT 100").df()
```

## Manejo de Errores

Las funciones usan try/except para manejar errores de forma silenciosa:
- Si un archivo no existe, se ignora (no se incluye en disponibles)
- Errores de conexión se propagan al llamador

## Rendimiento

- Las consultas son lazy (DuckDB solo lee lo necesario)
- Parquet permite lectura columnar eficiente
- HTTPFS permite streaming desde R2 sin descargar archivos completos

## Archivos Relacionados

- `config.py`: Provee credenciales de R2
- `db_metadata.py`: Define las categorías disponibles
- `app.py`: Usa este módulo para mostrar datos
