import geopandas as gpd
import pandas as pd
import streamlit as st
import pydeck as pdk
import os

pdk.settings.mapbox_api_key = os.environ["MAPBOX_API_KEY"]
#pdk.settings.mapbox_api_key = st.secrets["MAPBOX_API_KEY"]

st.set_page_config(page_title="SISTEMA AT EMT", layout="wide")

# Colunas usadas nos filtros (ajuste se necessário)
COL_SE_ORIGEM = "DESCR"
COL_LDAT_NOME = "CT_COD_OP"
COLS_CONEXAO_LDAT = ["PN_CON_1", "PN_CON_2"]
COL_ID_PONT = "COD_ID"
COLS_PONT_CASCATA = ["TIP_PN", "MAT", "ALT", "ESF"]


def extract_coords(geom):
    if geom is None or geom.is_empty:
        return None
    if geom.geom_type == "LineString":
        return list(geom.coords)
    elif geom.geom_type == "Polygon":
        return list(geom.exterior.coords)
    return None


def txt(series):
    return series.fillna("—").astype(str)


def opcoes(df, col):
    if col not in df.columns:
        return []
    s = df[col].dropna()
    try:
        return [str(v) for v in sorted(s.unique())]
    except TypeError:
        return sorted(s.astype(str).unique())


def aplicar(df, col, sel):
    if sel and col in df.columns:
        return df[df[col].astype(str).isin(sel)]
    return df


@st.cache_data(show_spinner="Carregando e preparando dados...")
def preparar_dados(path_se, path_ldat, path_est, path_pont):
    gdf_se = gpd.read_file(path_se).to_crs(epsg=4326)
    gdf_ldat = gpd.read_file(path_ldat).to_crs(epsg=4326)
    gdf_est = gpd.read_file(path_est).to_crs(epsg=4326)
    gdf_pont = gpd.read_file(path_pont).to_crs(epsg=4326)

    # remove geometrias nulas/vazias (fonte dos NaN que derrubam o deck.gl)
    gdf_se = gdf_se[gdf_se.geometry.notna() & ~gdf_se.geometry.is_empty].copy()
    gdf_ldat = gdf_ldat[gdf_ldat.geometry.notna() & ~gdf_ldat.geometry.is_empty].copy()
    gdf_est = gdf_est[gdf_est.geometry.notna() & ~gdf_est.geometry.is_empty].copy()
    gdf_pont = gdf_pont[gdf_pont.geometry.notna() & ~gdf_pont.geometry.is_empty].copy()

    gdf_se["coords"] = gdf_se.geometry.apply(extract_coords)
    gdf_ldat["coords"] = gdf_ldat.geometry.apply(extract_coords)
    gdf_est["coords"] = gdf_est.geometry.apply(extract_coords)

    # descarta o que não virou coords válido
    gdf_se = gdf_se[gdf_se["coords"].notna()].copy()
    gdf_ldat = gdf_ldat[gdf_ldat["coords"].notna()].copy()
    gdf_est = gdf_est[gdf_est["coords"].notna()].copy()

    gdf_pont["longitude"] = gdf_pont.geometry.x
    gdf_pont["latitude"] = gdf_pont.geometry.y
    gdf_pont = gdf_pont.dropna(subset=["longitude", "latitude"]).copy()

    gdf_se["__layer__"]   = "Subestação"
    gdf_ldat["__layer__"] = "Linha de Distribuição de Alta Tensão(LDAT)"
    gdf_est["__layer__"]  = "Área (polígono)"
    gdf_pont["__layer__"] = "Estrutura LDAT"

    gdf_ldat["tooltip"] = (
        "Camada: " + txt(gdf_ldat["__layer__"]) +
        "\nCOD_ID: " + txt(gdf_ldat["COD_ID"]) +
        "\nNome LDAT: " + txt(gdf_ldat["CT_COD_OP"]) +
        "\nSE de Origem: " + txt(gdf_ldat["DESCR"]) +
        "\nTensão nominal: " + txt(gdf_ldat["TEN_NOM"]) +
        "\nComprimento do vão (m): " + txt(gdf_ldat["COMP"]) +
        "\nGeometria do condutor: " + txt(gdf_ldat["GEOM_CAB"]) +
        "\nBitola do condutor: " + txt(gdf_ldat["BIT_FAS_1"]) +
        "\nMaterial do condutor: " + txt(gdf_ldat["MAT_FAS_1"]) +
        "\nProprietário: " + txt(gdf_ldat["POS"]) +
        "\nODI : " + txt(gdf_ldat["ODI"]) +
        "\nSituação contábil : " + txt(gdf_ldat["SITCONT"])
    ).fillna("Sem dados")

    gdf_se["tooltip"] = (
        "Camada: " + txt(gdf_se["__layer__"]) +
        "\nNome:" + txt(gdf_se["NOME"])
    ).fillna("Sem dados")

    gdf_est["tooltip"] = ("Camada: " + txt(gdf_est["__layer__"])).fillna("Sem dados")

    gdf_pont["tooltip"] = (
        txt(gdf_pont["__layer__"]) +
        "\nCOD_ID: " + txt(gdf_pont["COD_ID"]) +
        "\nLat: " + txt(gdf_pont["latitude"].round(5)) +
        "\nLon: " + txt(gdf_pont["longitude"].round(5)) +
        "\nTIP_PN: " + txt(gdf_pont["TIP_PN"]) +
        "\nProprietário: " + txt(gdf_pont["POS"]) +
        "\nMaterial: " + txt(gdf_pont["MAT"]) +
        "\nEsforço: " + txt(gdf_pont["ESF"]) +
        "\nAltura: " + txt(gdf_pont["ALT"]) +
        "\nPerímetro: " + txt(gdf_pont["ARE_LOC"]) +
        "\nLocalidade: " + txt(gdf_pont["MUN"]) +
        "\nODI: " + txt(gdf_pont["ODI"]) +
        " - TI: " + txt(gdf_pont["TI"]) +
        " - CM: " + txt(gdf_pont["CM"]) +
        "- TUC: " + txt(gdf_pont["TUC"]) +
        "\nSituação contábil: " + txt(gdf_pont["SITCONT"])
    ).fillna("Sem dados")

    b_se, b_ldat, b_est = gdf_se.total_bounds, gdf_ldat.total_bounds, gdf_est.total_bounds
    minx = min(b_se[0], b_ldat[0], b_est[0]); miny = min(b_se[1], b_ldat[1], b_est[1])
    maxx = max(b_se[2], b_ldat[2], b_est[2]); maxy = max(b_se[3], b_ldat[3], b_est[3])
    bounds = (minx, miny, maxx, maxy)

    df_se  = pd.DataFrame(gdf_se[["coords", "tooltip"]])
    df_est = pd.DataFrame(gdf_est[["coords", "tooltip"]])

    keep_ldat = ["coords", "tooltip"] + [c for c in ([COL_LDAT_NOME, COL_SE_ORIGEM] + COLS_CONEXAO_LDAT) if c in gdf_ldat.columns]
    df_ldat = pd.DataFrame(gdf_ldat[keep_ldat])

    keep_pont = ["longitude", "latitude", "tooltip", COL_ID_PONT] + [c for c in COLS_PONT_CASCATA if c in gdf_pont.columns]
    df_pont = pd.DataFrame(gdf_pont[keep_pont])

    return df_se, df_ldat, df_est, df_pont, bounds


df_se, df_ldat, df_est, df_pont, bounds = preparar_dados(
    "SUB.shp", "SSDAT1.shp", "ARAT.shp", "PONNOT.shp"
)

# ------------------- CONTROLE (barra lateral) -------------------
select_map = st.sidebar.selectbox("Estilo de mapa", [
    "Dark_C", "Satellite_Streets", "Streets", "Outdoors",
    "Dark_M", "Light", "Satellite", "Navigation_Day", "Navigation_Night"
], index=1)

# ------------------- CABEÇALHO -------------------
st.markdown("### 🗺️ **Sistema de Alta Tensão - Energisa Mato Grosso**\n")
st.markdown("###### ⚙️ *BASE DE DADOS GEOGRÁFICA DA DISTRIBUIDORA – BDGD*\n")

# ------------------- FILTRO EM CASCATA -------------------
c1, c2, c3 = st.columns(3)
with c1:
    sel_se = st.multiselect("SE de origem", opcoes(df_ldat, COL_SE_ORIGEM))
df_ldat_1 = aplicar(df_ldat, COL_SE_ORIGEM, sel_se)

with c2:
    sel_ldat = st.multiselect("Nome da LDAT", opcoes(df_ldat_1, COL_LDAT_NOME))
df_ldat_2 = aplicar(df_ldat_1, COL_LDAT_NOME, sel_ldat)

cols_ok = [c for c in COLS_CONEXAO_LDAT if c in df_ldat_2.columns]
if cols_ok:
    ids_estruturas = pd.unique(df_ldat_2[cols_ok].astype(str).values.ravel())
    df_pont_1 = df_pont[df_pont[COL_ID_PONT].astype(str).isin(ids_estruturas)]
else:
    df_pont_1 = df_pont

with c3:
    sel_tip = st.multiselect("TIP_PN", opcoes(df_pont_1, "TIP_PN"))
df_pont_2 = aplicar(df_pont_1, "TIP_PN", sel_tip)

c4, c5, c6 = st.columns(3)
with c4:
    sel_mat = st.multiselect("Material", opcoes(df_pont_2, "MAT"))
df_pont_3 = aplicar(df_pont_2, "MAT", sel_mat)

with c5:
    sel_alt = st.multiselect("Altura", opcoes(df_pont_3, "ALT"))
df_pont_4 = aplicar(df_pont_3, "ALT", sel_alt)

with c6:
    sel_esf = st.multiselect("Esforço", opcoes(df_pont_4, "ESF"))
df_pont_5 = aplicar(df_pont_4, "ESF", sel_esf)

# dados finais saneados (sem NaN de coordenada)
df_ldat_r = df_ldat_2[["coords", "tooltip"]]
df_pont_r = df_pont_5[["longitude", "latitude", "tooltip"]].dropna(subset=["longitude", "latitude"])

# ------------------- CAMADAS -------------------
layers = [
    pdk.Layer(
        "PolygonLayer", data=df_se, get_polygon="coords",
        get_fill_color=[255, 140, 0, 10], get_line_color=[180, 90, 0, 200],
        get_line_width=1, line_width_units="pixels", line_width_min_pixels=1, line_width_max_pixels=2,
        stroked=True, filled=True, pickable=True, auto_highlight=True, extruded=False, visible=True
    ),
    pdk.Layer(
        "PolygonLayer", data=df_est, get_polygon="coords",
        get_fill_color=[255, 255, 0, 255], get_line_color=[255, 255, 0, 255],
        get_line_width=1, line_width_units="pixels", line_width_min_pixels=1, line_width_max_pixels=2,
        stroked=True, filled=False, pickable=True, extruded=False, visible=True
    ),
]

if not df_ldat_r.empty:
    layers.append(pdk.Layer(
        "PathLayer", data=df_ldat_r, get_path="coords", get_color=[0, 90, 255, 220],
        get_width=1, width_units="pixels", width_min_pixels=1, width_max_pixels=2,
        pickable=True, auto_highlight=True, visible=True
    ))

if not df_pont_r.empty:
    layers.append(pdk.Layer(
        "ScatterplotLayer", data=df_pont_r, get_position='[longitude, latitude]',
        get_radius=2, radius_min_pixels=1, radius_max_pixels=4, radius_units="pixels",
        get_color='[255, 80, 0, 180]', pickable=True, auto_highlight=True, visible=True
    ))

minx, miny, maxx, maxy = bounds
view_state = pdk.ViewState(latitude=(miny + maxy) / 2, longitude=(minx + maxx) / 2, zoom=7)

estilo_mapa = {"Dark_C": ["carto", "dark"],
               "Satellite_Streets": ["mapbox", "mapbox://styles/mapbox/satellite-streets-v12"],
               "Streets": ["mapbox", "mapbox://styles/mapbox/streets-v12"],
               "Outdoors": ["mapbox", "mapbox://styles/mapbox/outdoors-v12"],
               "Dark_M": ["mapbox", "mapbox://styles/mapbox/dark-v11"],
               "Light": ["mapbox", "mapbox://styles/mapbox/light-v11"],
               "Satellite": ["mapbox", "mapbox://styles/mapbox/satellite-v9"],
               "Navigation_Day": ["mapbox", "mapbox://styles/mapbox/navigation-day-v1"],
               "Navigation_Night": ["mapbox", "mapbox://styles/mapbox/navigation-night-v1"]}

deck = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    map_provider=estilo_mapa[select_map][0],
    map_style=estilo_mapa[select_map][1],
    tooltip={"text": "{tooltip}"}
)

try:
    st.pydeck_chart(deck)
except Exception as e:
    st.error(f"Não foi possível renderizar o mapa: {e}")

if df_ldat_r.empty and df_pont_r.empty:
    st.info("Nenhuma LDAT/estrutura corresponde aos filtros selecionados.")
