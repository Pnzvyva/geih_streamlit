# Aplicación Principal (app.py)

## Descripción

Archivo principal de la aplicación Streamlit. Proporciona una interfaz web para explorar los datos de la GEIH almacenados en Cloudflare R2.

## Funcionalidades

### 1. Encabezado Institucional
- Muestra el logo de OCSA (Observatorio de Condiciones Socioeconómicas)
- Información del autor y organización
- Diseño responsive con HTML/CSS

### 2. Selectores de Datos

#### Selector de Año
```python
YEARS = list(range(2007, 2026))  # 2007-2025
```

#### Selector de Categoría
Muestra solo las categorías disponibles para el año seleccionado.

#### Selector de Tipo
- `cabecera`: Áreas urbanas principales
- `resto`: Resto de áreas urbanas
- `total`: Datos unificados (2020, 2022+)

### 3. Visualización de Datos
- Muestra hasta 5000 registros en una tabla interactiva
- Usa DuckDB para leer directamente desde Parquet en R2

### 4. Consulta SQL Avanzada
Permite ejecutar consultas SQL personalizadas con:
- Validación de seguridad (bloquea DROP, ALTER, DELETE, etc.)
- Descarga de resultados en CSV
- Mensajes de error descriptivos

## Caché

La conexión a R2 se cachea para mejorar rendimiento:
```python
@st.cache_resource
def init_r2_connection():
    return get_r2_connection()
```

## Dependencias

```python
import streamlit as st
import duckdb
import pandas as pd
from scripts.r2_connector import (
    get_r2_connection,
    create_table_view,
    get_available_categories_and_types_from_r2
)
import base64
import os
```

## Flujo de Ejecución

1. **Configurar página**: `st.set_page_config()`
2. **Mostrar encabezado**: Logo + información institucional
3. **Inicializar conexión**: Conectar a R2 vía DuckDB
4. **Seleccionar año**: Usuario elige año (2007-2025)
5. **Cargar disponibles**: Detectar categorías/tipos existentes en R2
6. **Seleccionar categoría**: Mostrar solo opciones válidas
7. **Seleccionar tipo**: Filtrar por disponibilidad
8. **Crear vista**: DuckDB crea vista virtual apuntando al Parquet
9. **Mostrar datos**: Ejecutar query y mostrar DataFrame
10. **SQL Avanzado**: Opcionalmente permitir consultas personalizadas

## Seguridad

### Validación de SQL
```python
forbidden = ["drop ", "alter ", "delete ", "update ", "insert ", "create "]
if any(bad in lower_sql for bad in forbidden):
    st.error("Esta consulta no está permitida por razones de seguridad.")
```

## Estructura de la Interfaz

```
┌─────────────────────────────────────────┐
│  [LOGO]  Explorador GEIH (2007–2025)   │
│          Desarrollado por...            │
├─────────────────────────────────────────┤
│  Selecciona un año: [2007 ▼]            │
│  Categoría: [caracteristicas ▼]         │
│  Tipo: [cabecera ▼]                     │
├─────────────────────────────────────────┤
│  📁 Tabla seleccionada: caracteristicas_2007_cabecera
├─────────────────────────────────────────┤
│  [Tabla de datos...]                    │
├─────────────────────────────────────────┤
│  Consulta SQL avanzada (opcional)      │
│  [Abrir consulta SQL ▼]               │
│  [Text area para SQL]                   │
│  [Ejecutar SQL]                         │
└─────────────────────────────────────────┘
```

## Variables de Entorno Requeridas

Configuradas vía Streamlit Secrets:
- `R2_ENDPOINT_URL`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET_NAME`

## Archivos Relacionados

- `scripts/r2_connector.py`: Conexión a R2
- `scripts/config.py`: Configuración de credenciales
- `assets/OCSA-logo.png`: Logo institucional
