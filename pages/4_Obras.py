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

list_ano_energiz = sorted(df["ano_energiz"].dropna().unique())
sel_ano_energiz = st.sidebar.multiselect("Selecionar Ano de Energização", list_ano_energiz, default=2026)

list_tip_obra = sorted(df.loc[(df["ano_energiz"].isin(sel_ano_energiz)),
                            "tipo_obra"].dropna().unique())
list_tip_obra = ["Todos"] + list_tip_obra
sel_tip_obra = st.sidebar.selectbox("Selecionar Tipo de Obra", list_tip_obra)
if sel_tip_obra == "Todos":
    sel_tip_obra = list_tip_obra
else:
    sel_tip_obra = [sel_tip_obra]

list_num_proj = sorted(df.loc[(df["ano_energiz"].isin(sel_ano_energiz))&
                              (df["tipo_obra"].isin(sel_tip_obra)),
                            "num_projeto"].dropna().unique())
list_num_proj = ["Todos"] + list_num_proj
sel__num_proj = st.sidebar.selectbox("Selecionar nº Projeto", list_num_proj)
if sel__num_proj == "Todos":
    sel__num_proj = list_num_proj
else:
    sel__num_proj = [sel__num_proj]

list_subest = sorted(df.loc[(df["ano_energiz"].isin(sel_ano_energiz))&
                            (df["tipo_obra"].isin(sel_tip_obra))&
                            (df["num_projeto"].isin(sel__num_proj)),
                            "subest"].dropna().unique())
list_subest = ["Todos"] + list_subest
sel__subest = st.sidebar.selectbox("Selecionar Subestação", list_subest)
if sel__subest == "Todos":
    sel__subest = list_subest
else:
    sel__subest = [sel__subest]

list_spcs_serv = sorted(df.loc[(df["ano_energiz"].isin(sel_ano_energiz))&
                            (df["tipo_obra"].isin(sel_tip_obra))&
                            (df["num_projeto"].isin(sel__num_proj))&
                            (df["subest"].isin(sel__subest)),
                            "lote_SPCS_cab"].dropna().unique())
list_spcs_serv = ["Todos"] + list_spcs_serv
sel__spcs_serv = st.sidebar.selectbox("Selecionar Lote dos Serviços de Campo", list_spcs_serv)
if sel__spcs_serv == "Todos":
    sel__spcs_serv = list_spcs_serv
else:
    sel__spcs_serv = [sel__spcs_serv]

list_spcs_taf = sorted(df.loc[(df["ano_energiz"].isin(sel_ano_energiz))&
                            (df["tipo_obra"].isin(sel_tip_obra))&
                            (df["num_projeto"].isin(sel__num_proj))&
                            (df["subest"].isin(sel__subest))&
                            (df["lote_SPCS_cab"].isin(sel__spcs_serv)),
                            "lote_SPCS_TAF"].dropna().unique())
list_spcs_taf = ["Todos"] + list_spcs_taf
sel__spcs_taf = st.sidebar.selectbox("Selecionar Lote dos Serviços de TAF/TAC", list_spcs_taf)
if sel__spcs_taf == "Todos":
    sel__spcs_taf = list_spcs_taf
else:
    sel__spcs_taf = [sel__spcs_taf]

df = df.loc[(df["ano_energiz"].isin(sel_ano_energiz))&
            (df["tipo_obra"].isin(sel_tip_obra))&
            (df["num_projeto"].isin(sel__num_proj))&
            (df["subest"].isin(sel__subest))&
            (df["lote_SPCS_cab"].isin(sel__spcs_serv))&
            df["lote_SPCS_TAF"].isin(sel__spcs_taf)]

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
