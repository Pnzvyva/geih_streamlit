# Configuración (config.py)

## Descripción

Módulo centralizado de configuración para la conexión a Cloudflare R2. Soporta tanto variables de entorno locales como Streamlit Secrets para despliegue en la nube.

## Funcionalidad Principal

### Soporte Dual de Configuración

El módulo detecta automáticamente si está corriendo en:
1. **Desarrollo local**: Lee desde archivo `.env`
2. **Streamlit Cloud**: Lee desde `st.secrets`

```python
# Prioridad de lectura:
1. Variables de entorno (os.getenv)
2. Streamlit Secrets (st.secrets['R2'])
3. Streamlit Secrets raíz (st.secrets)
4. Valores por defecto
```

## Variables de Configuración

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `R2_ENDPOINT_URL` | Endpoint de Cloudflare R2 | `https://1345c0d7da19b13339e8ff83529689ff.r2.cloudflarestorage.com` |
| `R2_ACCESS_KEY_ID` | Access Key de R2 | `None` (requerido) |
| `R2_SECRET_ACCESS_KEY` | Secret Key de R2 | `None` (requerido) |
| `R2_BUCKET_NAME` | Nombre del bucket | `microdata-geih-duckdb` |
| `R2_PUBLIC_URL` | URL pública (opcional) | `""` |

## Funciones

### `get_config(key, default=None)`

Obtiene configuración desde múltiples fuentes.

**Parámetros:**
- `key` (str): Nombre de la variable
- `default` (any): Valor por defecto si no existe

**Retorna:**
- Valor de la configuración o default

**Ejemplo:**
```python
endpoint = get_config("R2_ENDPOINT_URL")
```

### `validate_config()`

Valida que todas las credenciales necesarias estén configuradas.

**Excepciones:**
- `ValueError`: Si faltan variables requeridas

**Variables requeridas:**
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET_NAME`

**Ejemplo:**
```python
try:
    validate_config()
except ValueError as e:
    print(f"Error de configuración: {e}")
```

## Uso en Desarrollo Local

Crear archivo `.env` en la raíz:

```bash
R2_ENDPOINT_URL=https://tu-account-id.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=tu_access_key
R2_SECRET_ACCESS_KEY=tu_secret_key
R2_BUCKET_NAME=tu-bucket-name
```

## Uso en Streamlit Cloud

Configurar en **Settings → Secrets**:

```toml
[R2]
R2_ENDPOINT_URL = "https://tu-account-id.r2.cloudflarestorage.com"
R2_ACCESS_KEY_ID = "tu_access_key"
R2_SECRET_ACCESS_KEY = "tu_secret_key"
R2_BUCKET_NAME = "tu-bucket-name"
```

## Dependencias

```python
import os
from dotenv import load_dotenv
```

## Notas de Seguridad

- Nunca commitear archivos `.env` con credenciales reales
- El archivo `.env` debe estar en `.gitignore`
- Streamlit Secrets están encriptados en repos privados
- No imprimir credenciales en logs o output

## Archivos Relacionados

- `r2_connector.py`: Usa esta configuración para conectar
- `.env.example`: Plantilla para desarrollo local
- `.streamlit/secrets.toml.example`: Plantilla para Streamlit Cloud
