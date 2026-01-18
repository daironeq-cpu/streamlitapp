import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sqlite3

px.set_mapbox_access_token(st.secrets["MAPBOX_TOKEN"])

st.set_page_config(page_title="Capex", layout="wide")

DB_PATH = "banco_d_pma/dados_capex.db"
TABLE_NAME = "capex_26_28"
SOMA_VLR_COL = [
    "vlr_jan",
    "vlr_fev",
    "vlr_mar",
    "vlr_abr",
    "vlr_mai",
    "vlr_jun",
    "vlr_jul",
    "vlr_ago",
    "vlr_set",
    "vlr_out",
    "vlr_nov",
    "vlr_dez"
    ]
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

@st.cache_data(show_spinner=False)
def load_data(db_path: str, table_name: str) -> pd.DataFrame:
    query = f'SELECT * FROM "{table_name}"'
    with sqlite3.connect(db_path) as con:
        return pd.read_sql_query(query, con)

try:
    df = load_data(DB_PATH, TABLE_NAME)
except Exception as e:
    st.error(f"Erro ao carregar dados do banco: {e}")

@st.cache_data(show_spinner=False)
def add_col_vlr_tot(df: pd.DataFrame ,soma_vlr_col: list[str]) -> pd.DataFrame:

    df_out = df.copy()
    df_out["vlr_total"] = df[soma_vlr_col].fillna(0).sum(axis=1)

    return df_out

@st.cache_data(show_spinner=False)
def tot_proj(df: pd.DataFrame, dados_tot: list[str]) -> pd.DataFrame:

    return (
        df
        .groupby((["num_projeto", "ano"] + dados_tot), as_index=False)
        .agg(
            nome_proj=('nom_projeto', 'first'),
            tot_ano=('vlr_total', 'sum'),
            subest=('subest', 'first'),
            ano_energiz=('ano_energiz', 'first'),
            obj=('codcap_obj', 'first'),
            dest=('codcap_dest', 'first'),
            jan=('vlr_jan', 'sum'),
            fev=('vlr_fev', 'sum'),
            mar=('vlr_mar', 'sum'),
            abr=('vlr_abr', 'sum'),
            mai=('vlr_mai', 'sum'),
            jun=('vlr_jun', 'sum'),
            jul=('vlr_jul', 'sum'),
            ago=('vlr_ago', 'sum'),
            set=('vlr_set', 'sum'),
            out=('vlr_out', 'sum'),
            nov=('vlr_nov', 'sum'),
            dez=('vlr_dez', 'sum'),
            latitude=('latitude', 'first'),
            longitude=('longitude', 'first'),
        )
        )

@st.cache_data(show_spinner=False)
def load_excel(excel_path: str) -> pd.DataFrame:
    return pd.read_excel(excel_path)

#Filtros
filtro_ano = sorted(df["ano"].dropna().unique())
filtro_nom_projeto = sorted(df["nom_projeto"].dropna().unique())
dados_tot = ["nom_obra_recurso", "dscntz_lct"]

df_excel = load_excel("Projetos_26-28.xlsx")

df1 = add_col_vlr_tot(df, SOMA_VLR_COL)

df1 = df1.merge(
    df_excel[["num_projeto", "longitude", "latitude", "subest", "ano_energiz", "tipo_obra"]],
    on="num_projeto",
    how="left",
    validate="many_to_one" 
)

dados_sel = st.sidebar.pills("Incluir na Totalização", dados_tot,selection_mode="multi")
df1 = tot_proj(df1, dados_sel)

#Filtro
sel_ano = st.sidebar.multiselect("Selecionar Ano Orçamentário", filtro_ano, default=2026)
if not sel_ano:
    st.warning("Selecione ao menos um campo para Ano.")
    st.stop()
df1 = df1[df1["ano"].isin(sel_ano)]

filtro_ano_energiz = sorted(df1["ano_energiz"].dropna().unique())
sel_ano_energiz = st.sidebar.multiselect("Selecionar Ano de Energização", filtro_ano_energiz, default=filtro_ano_energiz)
df1 = df1[df1["ano_energiz"].isin(sel_ano_energiz)]

filtro_num_projeto = sorted(df1["num_projeto"].dropna().unique())
options_num_projeto = ["Todos"] + filtro_num_projeto
sel_num_projeto = st.sidebar.selectbox("Selecionar nº SIGCO do Projeto", options_num_projeto)
if sel_num_projeto == "Todos":
    sel_num_projeto = filtro_num_projeto
else:
    sel_num_projeto = [sel_num_projeto]
df1 = df1[df1["num_projeto"].isin(sel_num_projeto)]

filtro_subest = sorted(df1["subest"].dropna().unique())
options_subest = ["Todos"] + filtro_subest
sel_subest = st.sidebar.selectbox("Selecionar Subestação", options_subest)
if sel_subest == "Todos":
    sel_subest = filtro_subest
else:
    sel_subest = [sel_subest]
df1 = df1[df1["subest"].isin(sel_subest)]

if "nom_obra_recurso" in df1.columns:
    filtro_nom_obra_recurso = sorted(df1["nom_obra_recurso"].dropna().unique())
    options_nom_obra_recurso = ["Todos"] + filtro_nom_obra_recurso
    sel_nom_obra_recurso = st.sidebar.selectbox("Selecionar Obra", options_nom_obra_recurso)
    if sel_nom_obra_recurso == "Todos":
        sel_nom_obra_recurso = filtro_nom_obra_recurso
    else:
        sel_nom_obra_recurso = [sel_nom_obra_recurso]
    df1 = df1[df1["nom_obra_recurso"].isin(sel_nom_obra_recurso)]

if "dscntz_lct" in df1.columns:
    filtro_ntz = sorted(df1["dscntz_lct"].dropna().unique())
    options_ntz = ["Todos"] + filtro_ntz
    sel_ntz = st.sidebar.selectbox("Selecionar Serviço/Material", options_ntz)
    if sel_ntz == "Todos":
        sel_ntz = filtro_ntz
    else:
        sel_ntz = [sel_ntz]
    df1 = df1[df1["dscntz_lct"].isin(sel_ntz)]

df1["latitude"]  = pd.to_numeric(df1["latitude"].astype(str).str.replace(",", "."), errors="coerce")
df1["longitude"] = pd.to_numeric(df1["longitude"].astype(str).str.replace(",", "."), errors="coerce")
df1["tot_ano"] = pd.to_numeric(df1["tot_ano"], errors="coerce")
df1["num_projeto"] = df1["num_projeto"].astype(str)

# Cria o mapa
fig = px.scatter_mapbox(
    df1,
    lat="latitude",
    lon="longitude",
    hover_name="nome_proj",
    color = "tot_ano",
    text= "subest",
    size = "tot_ano",
    color_continuous_scale="rainbow",
    size_max=40,
    zoom=5,
    height=600,
    labels={"tot_ano": "Total CAPEX (R$)", "subest": "Subestação", "num_projeto": "nº SIGCO", "ano_energiz": "Ano de Energização"},
    hover_data={
    "num_projeto": True,
    "tot_ano": ":,.2f",
    "latitude": False,
    "longitude": False,
    "ano_energiz": True
}
)

# Define o estilo do mapa
fig.update_layout(
    mapbox_style="mapbox://styles/mapbox/satellite-streets-v12",
    margin={"r":0,"t":0,"l":0,"b":0}
)

fig.update_traces(textposition="middle center",textfont=dict(size=8, color="gold", weight=900))

# Exibe no Streamlit
st.plotly_chart(
    fig,
    use_container_width=True,
    config={"scrollZoom": True}
)

#st.dataframe(df1, use_container_width=True)

dados_id_vars = ["num_projeto", "ano"] + dados_sel

#Organizar dados para geração de dados
df_graph = df1.melt(
    id_vars=dados_id_vars,
    value_vars=MESES,
    var_name="mes",
    value_name="capex"
)

#Ordenar meses
ordem_meses = {m: i for i, m in enumerate(MESES, start=1)}
df_graph["mes"] = df_graph["mes"].map(ordem_meses)
df_graph["data"] = pd.to_datetime(df_graph["ano"].astype(str) + "-" + df_graph["mes"].astype(str) + "-01")

df_total_mes_1 = (
    df_graph
    .groupby(["data"], as_index=False)
    .agg(
            capex=("capex", 'sum'),
        )
)

df_total_mes = (
    df_graph
    .groupby(["data", "num_projeto"], as_index=False)
    .agg(
            capex=("capex", 'sum'),
        )
)

if "dscntz_lct" in dados_id_vars:
    df_total_mes_3 = (
        df_graph
        .groupby(["data", "dscntz_lct"], as_index=False)
        .agg(
                capex=("capex", 'sum'),
            )
    )
    df_total_mes_3 = df_total_mes_3.sort_values("data")

if "nom_obra_recurso" in dados_id_vars:
    df_total_mes_4 = (
        df_graph
        .groupby(["data", "nom_obra_recurso"], as_index=False)
        .agg(
                capex=("capex", 'sum'),
            )
    )
    df_total_mes_4 = df_total_mes_4.sort_values("data")

df_total_mes_1 = df_total_mes_1.sort_values("data")
df_total_mes = df_total_mes.sort_values("data")
df_total_mes_1["capex_acum"] = df_total_mes_1["capex"].cumsum()


col1, col2 = st.columns(2)
with col1:
    fig_graph = go.Figure()
    fig_graph.add_trace(
        go.Bar(
            x=df_total_mes_1["data"],
            y=df_total_mes_1["capex"],
            name="CAPEX"
        )
    )
    fig_graph.add_trace(
        go.Scatter(
            x=df_total_mes_1["data"],
            y=df_total_mes_1["capex_acum"],
            mode="lines+markers",
            name="CAPEX Acumulado",
        )
    )
    fig_graph.update_layout(
        title="CAPEX Mensal",
        xaxis=dict(
            title="Mês",
            type="date",
            dtick="M1",
            tickformat="%b/%Y",
            fixedrange=False,
            rangeslider=dict(visible=False)
        ),
        yaxis=dict(
            title="CAPEX mensal (R$)",
            fixedrange=False
        ),
        hovermode="x unified",
        barmode="overlay",
        uirevision="capex_zoom",
        height=700
    )
    st.plotly_chart(
        fig_graph,
        use_container_width=True,
        config={"scrollZoom": True, "displaylogo": False}

    )
with col2:
    fig_graph_2 = go.Figure()
    for proj in df_total_mes["num_projeto"].sort_values().unique():
        df_p = df_total_mes[df_total_mes["num_projeto"] == proj]

        fig_graph_2.add_trace(
            go.Bar(
                x=df_p["data"],
                y=df_p["capex"],
                name=str(proj),
                hovertemplate=(
                    "Projeto: %{fullData.name}<br>"
                    "R$ %{y:,.2f}<extra></extra>"
                )
            )
        )
    fig_graph_2.add_trace(
        go.Scatter(
            x=df_total_mes_1["data"],
            y=df_total_mes_1["capex_acum"],
            mode="lines+markers",
            name="CAPEX Acumulado",
            yaxis="y2"
        )
    )
    fig_graph_2.update_layout(
        title="CAPEX Mensal",
        xaxis=dict(
            title="Mês",
            type="date",
            dtick="M1",
            tickformat="%b/%Y",
            fixedrange=False,
            rangeslider=dict(visible=False)
        ),
        yaxis=dict(
            title="CAPEX mensal (R$)",
            fixedrange=False
        ),
        yaxis2=dict(
            title="CAPEX Acumulado",
            overlaying="y",
            side="right",
            fixedrange=False
        ),
        hovermode="x unified",
        barmode="group",
        uirevision="capex_zoom",
        height=700
    )
    st.plotly_chart(
        fig_graph_2,
        use_container_width=True,
        config={"scrollZoom": True, "displaylogo": False}
    )

col3, col4 = st.columns(2)
if "dscntz_lct" in dados_id_vars:
    with col3:
        fig_graph_3 = go.Figure()
        for proj3 in df_total_mes_3["dscntz_lct"].sort_values().unique():
            df_p3 = df_total_mes_3[df_total_mes_3["dscntz_lct"] == proj3]

            fig_graph_3.add_trace(
                go.Bar(
                    x=df_p3["data"],
                    y=df_p3["capex"],
                    name=str(proj3),
                    hovertemplate=(
                        "Natureza: %{fullData.name}<br>"
                        "R$ %{y:,.2f}<extra></extra>"
                    )
                )
            )
        fig_graph_3.add_trace(
            go.Scatter(
                x=df_total_mes_1["data"],
                y=df_total_mes_1["capex_acum"],
                mode="lines+markers",
                name="CAPEX Acumulado",
            )
        )
        fig_graph_3.update_layout(
            title="CAPEX Mensal por Natureza",
            xaxis=dict(
                title="Mês",
                type="date",
                dtick="M1",
                tickformat="%b/%Y",
                fixedrange=False,
                rangeslider=dict(visible=False)
            ),
            yaxis=dict(
                title="CAPEX mensal (R$)",
                fixedrange=False
            ),
            hovermode="x unified",
            barmode="stack",
            uirevision="capex_zoom",
            height=700
        )
        st.plotly_chart(
            fig_graph_3,
            use_container_width=True,
            config={"scrollZoom": True, "displaylogo": False}
        )

if "nom_obra_recurso" in dados_id_vars:
    with col4:
        fig_graph_4 = go.Figure()
        for proj4 in df_total_mes_4["nom_obra_recurso"].sort_values().unique():
            df_p3 = df_total_mes_4[df_total_mes_4["nom_obra_recurso"] == proj4]

            fig_graph_4.add_trace(
                go.Bar(
                    x=df_p3["data"],
                    y=df_p3["capex"],
                    name=str(proj4),
                    hovertemplate=(
                        "Obra: %{fullData.name}<br>"
                        "R$ %{y:,.2f}<extra></extra>"
                    )
                )
            )
        fig_graph_4.add_trace(
            go.Scatter(
                x=df_total_mes_1["data"],
                y=df_total_mes_1["capex_acum"],
                mode="lines+markers",
                name="CAPEX Acumulado",
            )
        )
        fig_graph_4.update_layout(
            title="CAPEX Mensal por Obra",
            xaxis=dict(
                title="Mês",
                type="date",
                dtick="M1",
                tickformat="%b/%Y",
                fixedrange=False,
                rangeslider=dict(visible=False)
            ),
            yaxis=dict(
                title="CAPEX mensal (R$)",
                fixedrange=False
            ),
            hovermode="x unified",
            barmode="stack",
            uirevision="capex_zoom",
            height=700
        )
        st.plotly_chart(
            fig_graph_4,
            use_container_width=True,
            config={"scrollZoom": True, "displaylogo": False}
        )