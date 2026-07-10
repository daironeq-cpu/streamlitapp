import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Polygon
import streamlit as st
import pydeck as pdk
import os

pdk.settings.mapbox_api_key = os.environ["MAPBOX_API_KEY"]
#MAPBOX_API_KEY = st.secrets["MAPBOX_API_KEY"]
#pdk.settings.mapbox_api_key = MAPBOX_API_KEY

st.set_page_config(page_title="SISTEMA AT EMT", layout="wide")


def extract_coords(geom):
    if geom.geom_type == "LineString":
        return list(geom.coords)
    elif geom.geom_type == "Polygon":
        return list(geom.exterior.coords)
    else:
        return None


def txt(series):
    # fillna ANTES do astype: trata NaN e pd.NA (dtypes nullable)
    return series.fillna("—").astype(str)


@st.cache_data
def carregar_dados(path1, path2, path3, path4):
    gdf_1 = gpd.read_file(path1).to_crs(epsg=4326)
    gdf_2 = gpd.read_file(path2).to_crs(epsg=4326)
    gdf_3 = gpd.read_file(path3).to_crs(epsg=4326)
    gdf_4 = gpd.read_file(path4).to_crs(epsg=4326)
    return gdf_1, gdf_2, gdf_3, gdf_4


gdf_se, gdf_ldat, gdf_est, gdf_pont = carregar_dados("SUB.shp", "SSDAT1.shp", "ARAT.shp", "PONNOT.shp")

gdf_se["coords"] = gdf_se.geometry.apply(extract_coords)
gdf_ldat["coords"] = gdf_ldat.geometry.apply(extract_coords)
gdf_est["coords"] = gdf_est.geometry.apply(extract_coords)

gdf_pont["longitude"] = gdf_pont.geometry.x
gdf_pont["latitude"] = gdf_pont.geometry.y

gdf_se["__layer__"]   = "Subestação"
gdf_ldat["__layer__"] = "Linha de Distribuição de Alta Tensão(LDAT)"
gdf_est["__layer__"]  = "Área (polígono)"
gdf_pont["__layer__"] = "Estrutura LDAT"

# DataFrames comuns (sem coluna geometry) para o pydeck resolver o {tooltip} corretamente
df_se   = gdf_se.drop(columns="geometry")
df_ldat = gdf_ldat.drop(columns="geometry")
df_est  = gdf_est.drop(columns="geometry")
df_pont = gdf_pont.drop(columns="geometry")

df_ldat["tooltip"] = (
    "Camada: " + txt(df_ldat["__layer__"]) +
    "\nCOD_ID: " + txt(df_ldat["COD_ID"]) +
    "\nNome LDAT: " + txt(df_ldat["CT_COD_OP"]) +
    "\nSE de Origem: " + txt(df_ldat["DESCR"]) +
    "\nTensão nominal: " + txt(df_ldat["TEN_NOM"]) +
    "\nComprimento do vão (m): " + txt(df_ldat["COMP"]) +
    "\nGeometria do condutor: " + txt(df_ldat["GEOM_CAB"]) +
    "\nBitola do condutor: " + txt(df_ldat["BIT_FAS_1"]) +
    "\nMaterial do condutor: " + txt(df_ldat["MAT_FAS_1"]) +
    "\nProprietário: " + txt(df_ldat["POS"]) +
    "\nODI : " + txt(df_ldat["ODI"]) +
    "\nSituação contábil : " + txt(df_ldat["SITCONT"])
).fillna("Sem dados")

df_se["tooltip"] = (
    "Camada: " + txt(df_se["__layer__"]) +
    "\nNome:" + txt(df_se["NOME"])
).fillna("Sem dados")

df_pont["tooltip"] = (
    txt(df_pont["__layer__"]) +
    "\nCOD_ID: " + txt(df_pont["COD_ID"]) +
    "\nLat: " + txt(df_pont["latitude"].round(5)) +
    "\nLon: " + txt(df_pont["longitude"].round(5)) +
    "\nTIP_PN: " + txt(df_pont["TIP_PN"]) +
    "\nProprietário: " + txt(df_pont["POS"]) +
    "\nMaterial: " + txt(df_pont["MAT"]) +
    "\nEsforço: " + txt(df_pont["ESF"]) +
    "\nAltura: " + txt(df_pont["ALT"]) +
    "\nPerímetro: " + txt(df_pont["ARE_LOC"]) +
    "\nLocalidade: " + txt(df_pont["MUN"]) +
    "\nODI: " + txt(df_pont["ODI"]) +
    " - TI: " + txt(df_pont["TI"]) +
    " - CM: " + txt(df_pont["CM"]) +
    "- TUC: " + txt(df_pont["TUC"]) +
    "\nSituação contábil: " + txt(df_pont["SITCONT"])
).fillna("Sem dados")

tg_ldat = st.sidebar.toggle("Traçado LDAT", value=False)
tg_estrut = st.sidebar.toggle("Estruturas", value=False)
tg_se = st.sidebar.toggle("Subestações", value=False)

# Camadas
if "layers" not in st.session_state:
    st.session_state.layers = {
    "path_layer_se": pdk.Layer(
        "PolygonLayer",
        data=df_se,
        get_polygon="coords",
        get_fill_color=[255, 140, 0, 10],
        get_line_color=[180, 90, 0, 200],
        get_line_width=1,
        line_width_units="pixels",
        line_width_min_pixels=1,
        line_width_max_pixels=2,
        stroked=True,
        filled=True,
        pickable=True,
        auto_highlight=True,
        extruded=False,
        visible=tg_se
    ),
    "path_layer_est": pdk.Layer(
        "PolygonLayer",
        data=df_est,
        get_polygon="coords",
        get_fill_color=[255, 255, 0, 255],
        get_line_color=[255, 255, 0, 255],
        get_line_width=1,
        line_width_units="pixels",
        line_width_min_pixels=1,
        line_width_max_pixels=2,
        stroked=True,
        filled=False,
        pickable=True,
        extruded=False,
    ),
    "path_layer_ldat": pdk.Layer(
        "PathLayer",
        data=df_ldat,
        get_path="coords",
        get_color=[0, 90, 255, 220],
        get_width=1,
        width_units="pixels",
        width_min_pixels=1,
        width_max_pixels=2,
        pickable=True,
        auto_highlight=True,
        visible=tg_ldat
    ),
    "path_layer_pont": pdk.Layer(
        "ScatterplotLayer",
        data=df_pont,
        get_position='[longitude, latitude]',
        get_radius=2,
        radius_min_pixels=1,
        radius_max_pixels=4,
        radius_units="pixels",
        get_color='[255, 80, 0, 180]',
        pickable=True,
        auto_highlight=True,
        visible=tg_estrut
    )
    }

layers = st.session_state.layers

st.session_state.layers["path_layer_ldat"].visible = tg_ldat
st.session_state.layers["path_layer_pont"].visible = tg_estrut
st.session_state.layers["path_layer_se"].visible = tg_se

# View centralizada
minx1, miny1, maxx1, maxy1 = gdf_se.total_bounds
minx2, miny2, maxx2, maxy2 = gdf_ldat.total_bounds
minx3, miny3, maxx3, maxy3 = gdf_est.total_bounds

minx, miny = min(minx1, minx2, minx3), min(miny1, miny2, miny3)
maxx, maxy = max(maxx1, maxx2, maxx3), max(maxy1, maxy2, maxy3)

view_state = pdk.ViewState(
    latitude=(miny + maxy) / 2,
    longitude=(minx + maxx) / 2,
    zoom=7
)

estilo_mapa = {"Dark_C": ["carto", "dark"],
               "Satellite_Streets": ["mapbox", "mapbox://styles/mapbox/satellite-streets-v12"],
               "Streets": ["mapbox", "mapbox://styles/mapbox/streets-v12"],
               "Outdoors": ["mapbox", "mapbox://styles/mapbox/outdoors-v12"],
               "Dark_M": ["mapbox", "mapbox://styles/mapbox/dark-v11"],
               "Light": ["mapbox", "mapbox://styles/mapbox/light-v11"],
               "Satellite": ["mapbox", "mapbox://styles/mapbox/satellite-v9"],
               "Navigation_Day": ["mapbox", "mapbox://styles/mapbox/navigation-day-v1"],
               "Navigation_Night": ["mapbox", "mapbox://styles/mapbox/navigation-night-v1"]
               }

select_map = st.sidebar.selectbox(
    "Estilo de mapa",
    estilo_mapa.keys(), index=1
)

st.markdown("### 🗺️ **Sistema de Alta Tensão - Energisa Mato Grosso**\n")
st.markdown("###### ⚙️ *BASE DE DADOS GEOGRÁFICA DA DISTRIBUIDORA – BDGD*\n")

deck = pdk.Deck(
    layers=[layers["path_layer_est"], layers["path_layer_se"], layers["path_layer_ldat"], layers["path_layer_pont"]],
    initial_view_state=view_state,
    map_provider=estilo_mapa[select_map][0],
    map_style=estilo_mapa[select_map][1],
    tooltip={"text": "{tooltip}"}
)

st.pydeck_chart(deck)
