import streamlit as st
import duckdb
import pandas as pd
from scripts.db_metadata import get_available_categories_and_types
from scripts.ensure_duckdb import ensure_duckdb_exists
import base64
import os

DB_PATH = "data/geih.duckdb"

# Descargar base de datos desde R2 si no existe (solo al inicio)
@st.cache_resource
def init_database():
    """Inicializa la base de datos descargandola desde R2 si es necesario."""
    ensure_duckdb_exists()
    return True

# Inicializar
init_database()

st.set_page_config(page_title="Explorador GEIH", layout="wide")


# ============================
# Encabezado institucional
# ============================

AUTHOR = "Juan Camilo Pinedo"
ORG = "Observatorio de Condiciones Socioeconómicas (OCSA) – Universidad del Norte"
LOGO_PATH = "assets/OCSA-logo.png"

def load_logo_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64 = load_logo_base64(LOGO_PATH)

st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:16px; margin-bottom:25px;">
        <img src="data:image/png;base64,{logo_base64}" 
             alt="logo" 
             style="width:60px; border-radius:8px;" />
        <div>
            <h2 style="margin:0; padding:0;">Explorador GEIH (2007–2025)</h2>
            <p style="margin:0; padding:0; opacity:0.75;">
                Desarrollado por <strong>{AUTHOR}</strong> — {ORG}
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("Consulta tablas anuales de la GEIH usando DuckDB.")

# ====================================
# SELECTOR DE AÑO – SOLO AÑOS
# ====================================
YEARS = list(range(2007, 2026))

year = st.selectbox("Selecciona un año:", YEARS)

# Obtener categorías válidas para ese año
available = get_available_categories_and_types(year)

if not available:
    st.error("Este año no tiene datos disponibles.")
    st.stop()

categorias_disponibles = [cat for cat, _ in available]

# ====================================
# SELECTOR DE CATEGORÍA – SOLO VÁLIDAS
# ====================================
categoria = st.selectbox("Categoría:", categorias_disponibles)

# Obtener tipos válidos para esa categoría
tipos_disponibles = next(tipos for cat, tipos in available if cat == categoria)

# ====================================
# SELECTOR DE TIPO – SOLO VÁLIDOS
# ====================================
tipo = st.selectbox("Tipo:", tipos_disponibles)

# ====================================
# NOMBRE DE TABLA
# ====================================
table_name = f"{categoria}_{year}_{tipo}".replace(" ", "_")

st.markdown(f"### 📁 Tabla seleccionada: `{table_name}`")

# ====================================
# CONSULTA SQL
# ====================================
con = duckdb.connect(DB_PATH)

try:
    df = con.execute(f"SELECT * FROM {table_name} LIMIT 5000").df()
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error cargando la tabla: {e}")

# ============================
# 🔍 CONSULTA SQL AVANZADA
# ============================

st.markdown("---")
st.subheader("Consulta SQL avanzada (opcional)")

with st.expander("Abrir consulta SQL"):
    
    st.write("Puedes ejecutar consultas SQL directamente sobre la base de datos DuckDB.")
    st.write("Ejemplo:")
    st.code(f"SELECT COUNT(*) FROM {table_name}")

    user_sql = st.text_area(
        "Escribe tu consulta SQL:",
        height=150,
        placeholder="SELECT * FROM ocupados_2020_total LIMIT 50"
    )

    if st.button("Ejecutar SQL"):
        if not user_sql.strip():
            st.warning("⚠️ La consulta está vacía.")
            st.stop()

        # Seguridad básica: evitar drops y alters
        forbidden = ["drop ", "alter ", "delete ", "update ", "insert ", "create "]
        lower_sql = user_sql.lower()

        if any(bad in lower_sql for bad in forbidden):
            st.error("Esta consulta no está permitida por razones de seguridad.")
            st.stop()

        try:
            result = con.execute(user_sql).df()
            st.success("Consulta ejecutada correctamente.")
            st.dataframe(result, use_container_width=True)

            # Botón de descarga
            csv = result.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Descargar resultado en CSV",
                data=csv,
                file_name="resultado_sql.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"Error ejecutando la consulta SQL:\n\n{e}")
