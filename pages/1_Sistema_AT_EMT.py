import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Polygon
import streamlit as st
import pydeck as pdk
import os

#pdk.settings.mapbox_api_key = os.environ["MAPBOX_API_KEY"]
MAPBOX_API_KEY = st.secrets["MAPBOX_API_KEY"]
pdk.settings.mapbox_api_key = MAPBOX_API_KEY

st.set_page_config(page_title="SISTEMA AT EMT", layout="wide")

def extract_coords(geom):
    if geom.geom_type == "LineString":
        return list(geom.coords)
    elif geom.geom_type == "Polygon":
        return list(geom.exterior.coords)
    else:
        return None
    
@st.cache_data
def carregar_dados(path1, path2, path3, path4):
    gdf_1 = gpd.read_file(path1).to_crs(epsg=4326)
    gdf_2 = gpd.read_file(path2).to_crs(epsg=4326)
    gdf_3 = gpd.read_file(path3).to_crs(epsg=4326)
    gdf_4 = gpd.read_file(path4).to_crs(epsg=4326)

    return gdf_1, gdf_2, gdf_3, gdf_4

gdf_se, gdf_ldat, gdf_est, gdf_pont = carregar_dados("SUB.shp", "SSDAT1.shp", "ARAT.shp", "PONNOT.shp")
    

#gdf_se = gpd.read_file("SUB.shp").to_crs(epsg=4326)
#gdf_ldat = gpd.read_file("SSDAT1.shp").to_crs(epsg=4326)
#gdf_est = gpd.read_file("ARAT.shp").to_crs(epsg=4326)
#gdf_pont = gpd.read_file("PONNOT.shp").to_crs(epsg=4326)


gdf_se["coords"] = gdf_se.geometry.apply(extract_coords)
gdf_ldat["coords"] = gdf_ldat.geometry.apply(extract_coords)
gdf_est["coords"] = gdf_est.geometry.apply(extract_coords)


#geojson_amaz = gdf_amaz.__geo_interface__


gdf_pont["longitude"] = gdf_pont.geometry.x
gdf_pont["latitude"] = gdf_pont.geometry.y

gdf_se["__layer__"]   = "Subestação"
gdf_ldat["__layer__"] = "Linha de Distribuição de Alta Tensão(LDAT)"
gdf_est["__layer__"]  = "Área (polígono)"
gdf_pont["__layer__"] = "Estrutura LDAT"

gdf_ldat["tooltip"] = (
    "Camada: " + gdf_ldat["__layer__"] +
    "\nCOD_ID: " + gdf_ldat["COD_ID"].astype(str) +
    "\nNome LDAT: " + gdf_ldat["CT_COD_OP"].astype(str) +
    "\nSE de Origem: " + gdf_ldat["DESCR"].astype(str) +
    "\nTensão nominal: " + gdf_ldat["TEN_NOM"].astype(str) +
    "\nComprimento do vão (m): " + gdf_ldat["COMP"].astype(str) +
    "\nGeometria do condutor: " + gdf_ldat["GEOM_CAB"].astype(str) +
    "\nBitola do condutor: " + gdf_ldat["BIT_FAS_1"].astype(str) +
    "\nMaterial do condutor: " + gdf_ldat["MAT_FAS_1"].astype(str) +
    "\nProprietário: " + gdf_ldat["POS"].astype(str) +
    "\nODI : " + gdf_ldat["ODI"].astype(str) +
    "\nSituação contábil : " + gdf_ldat["SITCONT"].astype(str)
    # + "\nCircuito: " + gdf_ldat["CIRCUITO"].astype(str)  # exemplo
)

gdf_se["tooltip"] = (
    "Camada: " + gdf_se["__layer__"] +
    "\nNome:" + gdf_se["NOME"]
    # + "\nÁrea: " + gdf_est["AREA_HA"].round(2).astype(str) + " ha"  # exemplo
)


gdf_pont["tooltip"] = (
    "" + gdf_pont["__layer__"].astype(str) +
    "\nCOD_ID: " + gdf_pont["COD_ID"].astype(str) +
    "\nLat: " + gdf_pont["latitude"].round(5).astype(str) +
    "\nLon: " + gdf_pont["longitude"].round(5).astype(str) +
    "\nTIP_PN: " + gdf_pont["TIP_PN"].astype(str) +
    "\nProprietário: " + gdf_pont["POS"].astype(str) +
    "\nMaterial: " + gdf_pont["MAT"].astype(str) +
    "\nEsforço: " + gdf_pont["ESF"].astype(str) +
    "\nAltura: " + gdf_pont["ALT"].astype(str) +
    "\nPerímetro: " + gdf_pont["ARE_LOC"].astype(str) +
    "\nLocalidade: " + gdf_pont["MUN"].astype(str) +
    "\nODI: " + gdf_pont["ODI"].astype(str) +
    " - TI: " + gdf_pont["TI"].astype(str) +
    " - CM: " + gdf_pont["CM"].astype(str) +
    "- TUC: " + gdf_pont["TUC"].astype(str) +
    "\nSituação contábil: " + gdf_pont["SITCONT"].astype(str)
)

tg_ldat = st.sidebar.toggle("Traçado LDAT", value=False)
tg_estrut = st.sidebar.toggle("Estruturas", value=False)
tg_se = st.sidebar.toggle("Subestações", value=False)

# Polígonos

if "layers" not in st.session_state:
    st.session_state.layers = {

    "path_layer_se": pdk.Layer(
        "PolygonLayer",
        data=gdf_se,
        get_polygon="coords",
        get_fill_color=[255, 140, 0, 10],
        get_line_color=[180, 90, 0, 200],
        get_line_width=5,
        line_width_units="pixels",
        line_width_min_pixels=1,
        stroked=True,
        filled=True,
        pickable=True,
        auto_highlight=True,
        extruded=False,
        visible=tg_se
    ),
    "path_layer_est": pdk.Layer(
        "PolygonLayer",
        data=gdf_est,
        get_polygon="coords",
        get_fill_color=[255, 255, 0, 255],
        get_line_color=[255, 255, 0, 255],
        get_line_width=3,
        line_width_units="pixels",
        line_width_min_pixels=1,
        stroked=True,
        filled=False,
        pickable=True,
        extruded=False,
    ),
    "path_layer_ldat": pdk.Layer(
        "PathLayer",                       # <- usar PathLayer
        data=gdf_ldat,
        get_path="coords",
        get_color=[0, 90, 255, 220],
        get_width=3,
        width_units="pixels",
        width_min_pixels=2,
        pickable=True,
        auto_highlight=True,
        visible=tg_ldat
    ),
    "path_layer_pont": pdk.Layer(
        "ScatterplotLayer",
        data=gdf_pont,                               # pode ser GeoDataFrame direto
        get_position='[longitude, latitude]',   # usa as colunas que você criou
        get_radius=10,
        radius_min_pixels=2,                         # metros (se usar 'meters' como units)
        radius_units="pixels",                  # ou "meters"
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

print("layer finalizada")
# View centralizada considerando as duas camadas
minx1, miny1, maxx1, maxy1 = gdf_se.total_bounds
minx2, miny2, maxx2, maxy2 = gdf_ldat.total_bounds
minx3, miny3, maxx3, maxy3 = gdf_est.total_bounds
#minx4, miny4, maxx4, maxy4 = gdf_pont.total_bounds


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
    api_keys={"mapbox": MAPBOX_API_KEY},
    tooltip={"text": "{tooltip}"}
)

print("Deck finalizada")

st.pydeck_chart(deck)
