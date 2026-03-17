# Arquitectura General

## Visión de Alto Nivel

El GEIH Explorer es una aplicación web que permite explorar los datos de la Gran Encuesta Integrada de Hogares (GEIH) de Colombia desde 2007 hasta 2025.

## Componentes Principales

### 1. Frontend (Streamlit)
- **Archivo**: `app.py`
- **Función**: Interfaz de usuario web
- **Características**:
  - Selector de año (2007-2025)
  - Selector de categoría (9 categorías disponibles)
  - Selector de tipo (cabecera/resto/total)
  - Visualización de datos en tabla
  - Consulta SQL avanzada

### 2. Backend (DuckDB + R2)
- **Conector**: `scripts/r2_connector.py`
- **Almacenamiento**: Cloudflare R2 (S3-compatible)
- **Formato**: Apache Parquet
- **Ventajas**:
  - Consultas analíticas rápidas
  - Almacenamiento económico
  - Escalabilidad automática

### 3. Pipeline de Datos

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Datos CSV     │────▶│   DuckDB     │────▶│   Parquet   │
│   (Fuente DANE) │     │   (Local)    │     │   (Local)   │
└─────────────────┘     └──────────────┘     └──────┬──────┘
                                                    │
                                                    ▼
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Usuario Web   │◀────│   Streamlit  │◀────│   R2 Cloud  │
│                 │     │   (DuckDB)   │     │   (Parquet) │
└─────────────────┘     └──────────────┘     └─────────────┘
```

## Estructura de Datos en R2

```
parquet/
├── caracteristicas/
│   ├── 2007/
│   │   ├── cabecera.parquet
│   │   └── resto.parquet
│   ├── 2008/
│   │   ├── cabecera.parquet
│   │   └── resto.parquet
│   └── ...
├── hogar/
│   └── ...
├── fuerza_trabajo/
│   └── ...
├── ocupados/
│   └── ...
├── no_ocupados/
│   └── ...
├── inactivos/
│   └── ...
├── migracion/
│   └── ...
├── otras_actividades/
│   └── ...
└── otros_ingresos/
    └── ...
```

## Categorías de Datos

| Categoría | Descripción | Años Disponibles |
|-----------|-------------|------------------|
| caracteristicas | Datos demográficos, educación, salud | 2007-2025 |
| hogar | Información del hogar y vivienda | 2007-2025 |
| fuerza_trabajo | Población en edad de trabajar | 2007-2025 |
| ocupados | Personas con empleo | 2007-2025 |
| no_ocupados | Personas desempleadas | 2007-2025 |
| inactivos | Personas fuera de la fuerza laboral | 2007-2025 |
| migracion | Datos de migración | 2022-2025 |
| otras_actividades | Otras formas de trabajo | 2007-2025 |
| otros_ingresos | Ingresos adicionales e impuestos | 2007-2025 |

## Formatos por Año

- **2007-2021 (excepto 2020)**: Dividido en `cabecera` y `resto`
- **2020 y 2022+**: Formato `total` (unificado)

## Seguridad

- Las credenciales de R2 se almacenan en **Streamlit Secrets** (nunca en el código)
- Las consultas SQL tienen validación básica (no permiten DROP, ALTER, DELETE, etc.)
- El bucket R2 es de solo lectura para la app (recomendado)

## Tecnologías Clave

| Tecnología | Uso |
|------------|-----|
| Streamlit | Framework web |
| DuckDB | Base de datos analítica embebida |
| Apache Parquet | Formato de almacenamiento columnar |
| Cloudflare R2 | Almacenamiento en la nube (S3-compatible) |
| Boto3 | SDK de AWS para Python (compatible con R2) |
