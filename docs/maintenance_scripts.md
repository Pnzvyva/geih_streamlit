# Scripts de Mantenimiento

Estos scripts se usan para construir y actualizar los datos en R2. No son necesarios para el funcionamiento de la aplicación web, pero son esenciales para el mantenimiento de los datos.

## Pipeline de Actualización

```
Datos CSV → build_duckdb.py → export_all_to_parquet.py → upload_parquet_parallel.py → R2
```

---

## build_duckdb.py

### Descripción

Construye la base de datos DuckDB local a partir de los archivos CSV fuente.

### Funcionalidad

1. Lee archivos CSV de cada año (2007-2025)
2. Procesa datos por categoría y tipo (cabecera/resto/total)
3. Crea tablas en DuckDB con nombres normalizados
4. Maneja columnas duplicadas y caracteres especiales
5. Genera logs de construcción

### Configuración

```python
DB_PATH = "data/geih.duckdb"
LOGS_DIR = "logs"
YEARS = list(range(2007, 2026))  # 2007-2025
```

### Uso

```bash
python scripts/build_duckdb.py
```

### Salida

- Base de datos: `data/geih.duckdb`
- Archivo log: `logs/build_YYYYMMDD_HHMM.log`

### Funciones Principales

- `log(msg)`: Escribe a consola y archivo log
- `create_table_if_needed(df, table_name, con)`: Crea tabla con estructura del DataFrame
- `insert_into_table(df, table_name, con)`: Inserta datos de forma optimizada

---

## export_all_to_parquet.py

### Descripción

Exporta todas las tablas de la base de datos DuckDB a archivos Parquet organizados.

### Estructura de Salida

```
parquet_export/
├── {categoria}/
│   ├── {año}/
│   │   └── {tipo}.parquet
```

### Funcionalidad

1. Conecta a `data/geih.duckdb`
2. Lista todas las tablas
3. Parsea nombres: `categoria_año_tipo`
4. Exporta cada tabla a Parquet manteniendo estructura de carpetas

### Uso

```bash
python scripts/export_all_to_parquet.py
```

### Funciones Principales

- `parse_table_name(table_name)`: Extrae categoria, año, tipo del nombre de tabla
- `export_table_to_parquet(con, table_name, output_path)`: Exporta usando COPY

### Salida

- Archivos Parquet en `parquet_export/`
- Resumen en consola con conteo de éxitos y errores

---

## upload_parquet_parallel.py

### Descripción

Sube todos los archivos Parquet al bucket R2 de forma paralela para mayor velocidad.

### Configuración

```python
LOCAL_PARQUET_DIR = "parquet_export"
R2_PREFIX = "parquet"
MAX_WORKERS = 10  # Hilos paralelos
```

### Funcionalidad

1. Escanea `parquet_export/` recursivamente
2. Construye lista de archivos a subir
3. Usa ThreadPoolExecutor para subida paralela
4. Muestra progreso en tiempo real
5. Reporta errores al final

### Uso

```bash
python scripts/upload_parquet_parallel.py
```

### Funciones Principales

- `get_r2_client()`: Crea cliente S3 configurado para R2
- `upload_single_file(args)`: Sube un archivo individual
- `upload_parquet_files()`: Coordina la subida paralela

### Salida

- Archivos en R2: `s3://bucket/parquet/{categoria}/{año}/{tipo}.parquet`
- Resumen con archivos subidos y errores

---

## cleanup_and_upload.py

### Descripción

Utilidad para limpiar archivos mal subidos y sincronizar archivos faltantes.

### Funcionalidad

1. **Limpieza**: Elimina archivos con nombres incorrectos (contienen "______")
2. **Verificación**: Compara archivos locales vs R2
3. **Sincronización**: Sube archivos que faltan en R2

### Uso

```bash
python scripts/cleanup_and_upload.py
```

### Casos de Uso

- Corregir subidas fallidas
- Eliminar archivos corruptos
- Sincronizar después de actualizar datos localmente

---

## verify_r2_upload.py

### Descripción

Verifica que los archivos se hayan subido correctamente a R2.

### Funcionalidad

1. Lista objetos en R2 con prefijo `parquet/`
2. Cuenta archivos totales
3. Agrupa por categoría
4. Muestra distribución

### Uso

```bash
python -m scripts.verify_r2_upload
```

### Salida

```
Total archivos subidos: 252

Archivos por categoría:
  caracteristicas: 33 archivos
  hogar: 33 archivos
  ...
```

---

## read_files.py

### Descripción

Módulo de utilidad para leer archivos CSV de datos de la GEIH.

### Funciones Principales

- `iter_year_data(year)`: Itera sobre todas las categorías y tipos de un año
- `ensure_unique_columns(df)`: Renombra columnas duplicadas
- `read_csv_robust(path)`: Lee CSV manejando errores de encoding

### Uso

Usado principalmente por `build_duckdb.py` para cargar datos.

---

## Flujo de Actualización Completo

Para actualizar los datos en R2 (ej: agregar año 2026):

```bash
# 1. Actualizar datos CSV fuente
# 2. Reconstruir base de datos local
python scripts/build_duckdb.py

# 3. Exportar a Parquet
python scripts/export_all_to_parquet.py

# 4. Subir a R2
python scripts/upload_parquet_parallel.py

# 5. Verificar subida
python -m scripts.verify_r2_upload
```

## Notas Importantes

- Estos scripts requieren credenciales de R2 configuradas
- Los archivos CSV fuente no están en el repositorio (datos DANE)
- El proceso completo puede tomar varias horas dependiendo del volumen
- Se recomienda hacer backup de `geih.duckdb` antes de reconstruir
