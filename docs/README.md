# Documentación del Proyecto GEIH Explorer

## Índice

1. [Arquitectura General](architecture.md) - Visión de alto nivel del sistema
2. [Aplicación Principal](app.md) - Documentación de `app.py`
3. [Módulos Core](config.md) - Configuración y conexión a R2
4. [Scripts de Mantenimiento](maintenance_scripts.md) - Actualización de datos
5. [Metadatos](db_metadata.md) - Estructura de categorías y tipos

## Estructura del Proyecto

```
geih_streamlit/
├── app.py                      # Aplicación Streamlit principal
├── requirements.txt            # Dependencias de Python
├── README.md                   # Documentación principal
├── .streamlit/
│   ├── config.toml            # Configuración de Streamlit
│   └── secrets.toml.example   # Ejemplo de secrets (no subir)
├── scripts/
│   ├── config.py              # Configuración de R2
│   ├── r2_connector.py        # Conector a Cloudflare R2
│   ├── db_metadata.py         # Metadatos de categorías
│   ├── build_duckdb.py        # Construcción de base local
│   ├── export_all_to_parquet.py  # Exportación a Parquet
│   ├── upload_parquet_parallel.py # Subida a R2
│   ├── cleanup_and_upload.py  # Limpieza y sincronización
│   ├── verify_r2_upload.py    # Verificación de subida
│   └── read_files.py          # Lectura de archivos fuente
├── assets/
│   └── OCSA-logo.png          # Logo institucional
└── docs/                      # Esta documentación
```

## Flujo de Datos

1. **Datos Fuente** → `build_duckdb.py` → **DuckDB Local**
2. **DuckDB Local** → `export_all_to_parquet.py` → **Archivos Parquet**
3. **Parquet Local** → `upload_parquet_parallel.py` → **Cloudflare R2**
4. **R2** → `app.py` (via `r2_connector.py`) → **Usuario Final**

## Despliegue

Ver [README.md](../README.md) para instrucciones de despliegue en Streamlit Cloud.
