import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sqlite3

px.set_mapbox_access_token(st.secrets["MAPBOX_TOKEN"])

st.set_page_config(page_title="Capex", layout="wide")

DB_PATH = "banco_d_pma/obras.db"
TABLE_NAME = "obras_26-28"

@st.cache_data(show_spinner=False)
def load_data(db_path: str, table_name: str) -> pd.DataFrame:
    query = f'SELECT * FROM "{table_name}"'
    with sqlite3.connect(db_path) as con:
        return pd.read_sql_query(query, con)

try:
    df = load_data(DB_PATH, TABLE_NAME)
except Exception as e:
    st.error(f"Erro ao carregar dados do banco: {e}")


df["latitude"]  = pd.to_numeric(df["latitude"].astype(str).str.replace(",", "."), errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"].astype(str).str.replace(",", "."), errors="coerce")
df["num_projeto"] = df["num_projeto"].astype(str)

# Cria o mapa
fig = px.scatter_mapbox(
    df,
    lat="latitude",
    lon="longitude",
    hover_name="nome_proj",
    #color = "tot_ano",
    text= "subest",
    size = "size",
    color_continuous_scale="rainbow",
    size_max=40,
    zoom=5,
    height=600,
    labels={"subest": "Subestação", 
            "num_projeto": 
            "nº SIGCO", 
            "ano_energiz": "Ano de Energização",
            "tipo_obra": "Tipo de Obra",
            "lote_SPCS_cab": "Lote de Contratação Serv. SPCS",
            "lote_SPCS_TAF": "Lote de Contratação Serv. TAF e TAC",
            "longitude": "Longitude",
            "latitude": "Latitude"
            },
    hover_data={
    "num_projeto": True,
    "subest": True,
    "ano_energiz": True,
    "tipo_obra": True,
    "lote_SPCS_cab": True,
    "lote_SPCS_TAF": True,
    "latitude": True,
    "longitude": True,
    "size": False 
}
)

# Define o estilo do mapa
fig.update_layout(
    mapbox_style="mapbox://styles/mapbox/navigation-night-v1",
    margin={"r":0,"t":0,"l":0,"b":0}
)

fig.update_traces(textposition="middle center",textfont=dict(size=8, color="gold", weight=900))

# Exibe no Streamlit
st.plotly_chart(
    fig,
    use_container_width=True,
    config={"scrollZoom": True}
)
