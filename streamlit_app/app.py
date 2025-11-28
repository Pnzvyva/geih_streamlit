import streamlit as st
import duckdb
import json

# Cargar mapping
with open("data/dictionary/mapping_files.json", "r", encoding="utf-8") as f:
    MAPPING = json.load(f)

con = duckdb.connect("data/db/geih.duckdb", read_only=True)

st.title("Explorador GEIH Consolidado (2007–2025)")
st.write("Selecciona categoría y año para cargar datos desde la base DuckDB.")

year = st.selectbox("Año", list(range(2007, 2026)))

# filtrar categorías válidas para el año
scheme = "2007_2021" if year <= 2021 else "2022_2025"
categorias_validas = list(MAPPING[scheme].keys())

categoria = st.selectbox("Categoría disponible", categorias_validas)

query = f"SELECT * FROM {categoria} WHERE ano = {year}"
df = con.execute(query).df()

st.write(f"### Resultados: {categoria} ({year})")
st.write(f"Total filas: {len(df):,}")
st.dataframe(df, height=500)

