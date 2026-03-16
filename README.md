# GEIH Streamlit - Procesador de Datos

Sistema de procesamiento y gestión de datos de la **Gran Encuesta Integrada de Hogares (GEIH)** de Colombia, utilizando DuckDB como base de datos analítica.

## Descripción

Este proyecto permite:
- Almacenar datos de la GEIH (2007-2025) en una base de datos DuckDB
- Procesar datos de diferentes categorías (características, hogar, fuerza de trabajo, ocupados, etc.)
- Gestionar almacenamiento en la nube (Cloudflare R2) - **solo el archivo `.duckdb`**

## Flujo de Trabajo

```
CSV (datos crudos)
    ↓
Parquet (formato intermedio, opcional)
    ↓
DuckDB (base de datos consolidada)
    ↓
Cloudflare R2 (almacenamiento en la nube)
```

**Nota importante**: Los archivos Parquet son un paso **intermedio opcional** en el procesamiento. El único archivo que se almacena en Cloudflare R2 es **`geih.duckdb`** (la base de datos consolidada).

## Estructura del Proyecto

```
.
├── assets/                     # Recursos visuales (logos)
├── data/
│   ├── dictionary/
│   │   └── mapping_files.json  # Mapeo de archivos por año y categoría
│   └── geih.duckdb            # Base de datos principal
├── logs/                       # Logs de ejecución
├── parquet_export/            # Archivos Parquet intermedios (no se suben a R2)
├── scripts/                   # Scripts de procesamiento
│   ├── add_2020.py           # Añade datos del año 2020
│   ├── config.py             # Configuración centralizada (R2)
│   ├── ensure_duckdb.py      # Descarga/subida de la base desde/hacia R2
│   ├── export_to_parquet.py  # Exporta tablas a formato Parquet (intermedio)
│   └── list_tables.py        # Lista y filtra tablas en la base
├── .env                       # Credenciales de R2 (NO subir a git)
├── .env.example              # Plantilla de variables de entorno
├── .gitignore                # Archivos ignorados por git
├── requirements.txt          # Dependencias del proyecto
└── README.md                 # Este archivo
```

## Categorías de Datos

El sistema maneja las siguientes categorías de la GEIH:

| Categoría | Descripción |
|-----------|-------------|
| `caracteristicas` | Características generales, seguridad social, salud y educación |
| `hogar` | Datos del hogar y la vivienda |
| `fuerza_trabajo` | Fuerza de trabajo |
| `ocupados` | Personas ocupadas |
| `no_ocupados` / `desocupados` | Personas desocupadas |
| `inactivos` | Personas inactivas |
| `migracion` | Datos de migración (a partir de 2022) |
| `otras_actividades` | Otras formas de trabajo |
| `otros_ingresos` | Otros ingresos e impuestos |

## Tipos de Área

Los datos se dividen en:
- **Cabecera**: Áreas urbanas (ciudades principales)
- **Resto**: Áreas rurales (resto del país)
- **Total**: Datos consolidados (a partir de 2022)

## Requisitos

- Python 3.8+
- Dependencias:
  ```
  streamlit
  duckdb
  pandas
  requests
  boto3
  python-dotenv
  ```

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd geih_streamlit
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. El archivo `.env` ya está configurado con las credenciales de R2.

## Configuración de Cloudflare R2

Las credenciales se configuran mediante **variables de entorno** en el archivo `.env` (que está en `.gitignore` para seguridad):

```bash
R2_ENDPOINT_URL=https://1345c0d7da19b13339e8ff83529689ff.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=7bc9fa25e0f234d02378575afd6896e3
R2_SECRET_ACCESS_KEY=88b0f7357bee0f8dc34a676727ae0f355f6eed8d1cb2449664b7e877a389c9fd
R2_BUCKET_NAME=microdata-geih-duckdb
```

**⚠️ Importante**: El archivo `.env` nunca se sube al repositorio (está en `.gitignore`).

## Uso

### 1. Descargar la base de datos desde R2

Descarga automáticamente la base de datos `geih.duckdb` desde Cloudflare R2 si no está presente localmente:

```bash
python scripts/ensure_duckdb.py
```

### 2. Subir la base de datos a R2

Después de actualizar la base de datos localmente, súbela a R2:

```bash
python -c "from scripts.ensure_duckdb import upload_duckdb_to_r2; upload_duckdb_to_r2()"
```

### 3. Listar tablas

Lista todas las tablas disponibles en la base de datos con opciones de filtrado:

```bash
python scripts/list_tables.py
```

Filtros disponibles:
- `categoria=<nombre>` - Filtrar por categoría
- `year=<año>` - Filtrar por año
- `tipo=<cabecera|resto|total>` - Filtrar por tipo de área

Ejemplos:
```
categoria=ocupados year=2020
categoria=hogar tipo=cabecera
```

### 4. Añadir datos del año 2020

```bash
python scripts/add_2020.py
```

### 5. Exportar a Parquet (opcional)

Exporta todas las tablas de la base de datos a archivos Parquet. Esto es útil como paso intermedio o para análisis externos:

```bash
python scripts/export_to_parquet.py
```

Los archivos se guardan en el directorio `parquet_export/`.

**Nota**: Estos archivos Parquet son intermedios y **no se suben a R2**. El objetivo final es tener todo consolidado en `geih.duckdb`.

## Formato de Nombres de Tablas

Las tablas siguen el formato:
```
{categoria}_{year}_{tipo}
```

Ejemplos:
- `ocupados_2020_cabecera`
- `hogar_2019_resto`
- `caracteristicas_2023_total`

## Cambios en el Formato de Datos

### Período 2007-2021
Los datos vienen separados en archivos CSV por:
- Categoría
- Tipo de área (Cabecera/Resto)

### Período 2022-2025
Los datos consolidan cabecera y resto en un solo archivo por categoría.

## Configuración de Mapeo

El archivo `data/dictionary/mapping_files.json` define la estructura de archivos para cada período:

```json
{
    "categorias": ["caracteristicas", "hogar", ...],
    "2007_2021": { ... },
    "2022_2025": { ... }
}
```

## Almacenamiento en la Nube

El proyecto está configurado para usar **Cloudflare R2** como almacenamiento:

- **Endpoint**: `https://1345c0d7da19b13339e8ff83529689ff.r2.cloudflarestorage.com`
- **Bucket**: `microdata-geih-duckdb`
- **Archivo almacenado**: `geih.duckdb` (base de datos consolidada)

**Lo que NO se almacena en R2**:
- ❌ Archivos CSV originales
- ❌ Archivos Parquet intermedios
- ❌ Logs de ejecución

R2 es compatible con la API de S3, por lo que se usa `boto3` para la conexión.

## Seguridad

- Las credenciales nunca deben estar hardcodeadas en los scripts
- Usa siempre el archivo `.env` para configuración sensible
- El archivo `.env` está en `.gitignore` para evitar subidas accidentales
- Si necesitas compartir el proyecto, solo comparte `.env.example` (sin credenciales reales)

## Licencia

Este proyecto es de uso académico/investigativo. Los datos de la GEIH son públicos y proporcionados por el DANE (Departamento Administrativo Nacional de Estadística) de Colombia.

## Contacto

Desarrollado para el procesamiento y análisis de datos de la GEIH.
