import streamlit as st
import duckdb
import pandas as pd
import os

DB_PATH = "data/geih.duckdb"

@st.cache_resource
def get_connection():
    return duckdb.connect(DB_PATH, read_only=True)

@st.cache_data
def get_tables():
    con = get_connection()
    df = con.execute("SHOW TABLES").df()
    return df["name"].tolist()

@st.cache_data
def load_table(table_name, limit=5000):
    con = get_connection()
    query = f"SELECT * FROM {table_name} LIMIT {limit}"
    return con.execute(query).df()

# ============================
# UI
# ============================

st.title("📊 Explorador GEIH (2007–2025)")
st.write("Consulta tablas anuales de la GEIH usando DuckDB.")

# Obtener tablas
tables = get_tables()

# Selector de año
years = sorted({t.split("_")[1] for t in tables})
year = st.selectbox("Selecciona un año:", years)

# Filtrar categorías existentes para ese año
tables_year = [t for t in tables if f"_{year}_" in t]

# Categorías reales
categorias = sorted({t.split("_")[0] for t in tables_year})
categoria = st.selectbox("Categoría:", categorias)

# Tipos posibles (cabecera, resto, total)
tipos = sorted({t.split("_")[2] for t in tables_year if t.startswith(categoria + "_")})
tipo = st.selectbox("Tipo:", tipos)

# Tabla final
table_name = f"{categoria}_{year}_{tipo}"
st.subheader(f"📂 Tabla seleccionada: `{table_name}`")

# Cargar datos
df = load_table(table_name)
st.dataframe(df)

# Descargar CSV
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇ Descargar CSV",
    data=csv,
    file_name=f"{table_name}.csv",
    mime="text/csv"
)

# Consulta SQL opcional
st.markdown("### 🔍 Consulta SQL opcional")
query = st.text_area("Escribe una consulta SQL (opcional):", 
                     f"SELECT * FROM {table_name} LIMIT 100")

if st.button("Ejecutar consulta"):
    try:
        con = get_connection()
        df_sql = con.execute(query).df()
        st.dataframe(df_sql)
    except Exception as e:
        st.error(f"Error en consulta: {e}")

