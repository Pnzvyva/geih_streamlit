---
title: GEIH Explorer
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
license: mit
---

# GEIH Explorer

Explorador de datos de la Gran Encuesta Integrada de Hogares (GEIH) de Colombia.

## Descripción

Esta aplicación permite explorar los datos de la GEIH desde 2007 hasta 2025, incluyendo:

- **Características**: Datos demográficos, educación, salud
- **Hogar**: Información del hogar y vivienda
- **Fuerza de Trabajo**: Población en edad de trabajar
- **Ocupados**: Personas con empleo
- **No Ocupados**: Personas desempleadas
- **Inactivos**: Personas fuera de la fuerza laboral
- **Migración**: Datos de migración (desde 2022)
- **Otras Actividades**: Otras formas de trabajo
- **Otros Ingresos**: Ingresos adicionales e impuestos

## Tecnologías

- **Streamlit**: Framework para aplicaciones web de datos
- **DuckDB**: Base de datos analítica embebida
- **Cloudflare R2**: Almacenamiento en la nube

## Despliegue en Streamlit Cloud

### 1. Preparar el repositorio

Asegúrate de que estos archivos estén en tu repositorio de GitHub:
- `app.py` - Archivo principal de la aplicación
- `requirements.txt` - Dependencias de Python
- `.streamlit/config.toml` - Configuración de Streamlit
- `scripts/` - Módulos de conexión a R2
- `assets/` - Logo y recursos estáticos

### 2. Configurar Secrets en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io/) e inicia sesión
2. Crea una nueva app conectando tu repositorio de GitHub
3. Ve a **Settings → Secrets** de tu aplicación
4. Agrega las credenciales de R2 en formato TOML:

```toml
[R2]
R2_ENDPOINT_URL = "https://tu-account-id.r2.cloudflarestorage.com"
R2_ACCESS_KEY_ID = "tu_access_key"
R2_SECRET_ACCESS_KEY = "tu_secret_key"
R2_BUCKET_NAME = "tu-bucket-name"
```

> **Nota**: Nunca subas las credenciales directamente al código. Usa siempre el sistema de secrets de Streamlit Cloud.

### 3. Desplegar

Streamlit Cloud detectará automáticamente `app.py` como punto de entrada y desplegará la aplicación.

## Desarrollo Local

1. Clona el repositorio
2. Instala dependencias: `pip install -r requirements.txt`
3. Crea un archivo `.env` basado en `.env.example` con tus credenciales de R2
4. Ejecuta: `streamlit run app.py`

## Desarrollo

Desarrollado por Juan Camilo Pinedo - Observatorio de Condiciones Socioeconómicas (OCSA) – Universidad del Norte

Datos proporcionados por el DANE - Departamento Administrativo Nacional de Estadística de Colombia.
