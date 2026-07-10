import geopandas as gpd
import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px
import os

pdk.settings.mapbox_api_key = os.environ["MAPBOX_API_KEY"]
#pdk.settings.mapbox_api_key = st.secrets["MAPBOX_API_KEY"]

st.set_page_config(page_title="SISTEMA AT EMT", layout="wide")

# Colunas usadas nos filtros/BI (ajuste se necessário)
COL_SE_ORIGEM = "DESCR"
COL_LDAT_NOME = "CT_COD_OP"
COLS_CONEXAO_LDAT = ["PN_CON_1", "PN_CON_2"]
COL_ID_PONT = "COD_ID"
COL_COMP = "COMP"
COL_TIPO_CABO = "BIT_FAS_1"
COL_TENSAO = "TEN_NOM"

# De-para dos códigos do PONNOT
dados_ponnot = {
    "TIP_PN": {"0": "Não informado", "PIS": "Ponto interno subestação", "PSA": "Ponto de saída de circuito de média tensão", "PSU": "Ponto subterrâneo", "POS": "Poste", "TOR": "Torre", "PSE": "Ponto de suporte de equipamento", "PSB": "Ponto de suporte de barramento", "PEC": "Ponto de entrada de condomínio", "PMF": "Ponto de medição de fronteira", "FLT": "Fly-tap", "PFL": "Ponto de fim de linha", "CXP": "Caixa de passagem", "PON": "Pontalete", "DRV": "Derivação"},
    "POS": {"0": "Não informado", "PD": "ENERGISA MATO GROSSO DISTRIBUIDORA", "OD": "Outro distribuidor", "T": "Transmissor", "G": "Gerador", "CS": "Consumidor", "CO": "Cooperativa", "A": "Autorizado", "O": "Outro agente"},
    "MAT": {"0": "Não informado ou não aplicável", "AC": "Aço", "CO": "Concreto", "CL": "Concreto leve", "EC": "Em compósito", "FE": "Ferro", "CQ": "Madeira", "ME": "Madeira eucalipto", "MQ": "Madeira quadrado", "MT": "Metálica", "AV": "Alvenaria"},
    "ESF": {"0": "Não informado ou não aplicável", "1": "50 daN", "2": "75 daN", "3": "90 daN", "4": "100 daN", "5": "150 daN", "6": "200 daN", "7": "300 daN", "8": "400 daN", "9": "500 daN", "10": "600 daN", "11": "700 daN", "12": "750 daN", "13": "800 daN", "14": "850 daN", "15": "900 daN", "16": "950 daN", "17": "1000 daN", "18": "1100 daN", "19": "1150 daN", "20": "1200 daN", "21": "1250 daN", "22": "1300 daN", "23": "1350 daN", "24": "1400 daN", "25": "1450 daN", "26": "1500 daN", "27": "1550 daN", "28": "1600 daN", "29": "1650 daN", "30": "1700 daN", "31": "1750 daN", "32": "1800 daN", "33": "1850 daN", "34": "1900 daN", "35": "2000 daN", "36": "2100 daN", "37": "2200 daN", "38": "2300 daN", "39": "2400 daN", "40": "2500 daN", "41": "2600 daN", "42": "2700 daN", "43": "2800 daN", "44": "2900 daN", "45": "3000 daN", "46": "3100 daN", "47": "3200 daN", "48": "3300 daN", "49": "3400 daN", "50": "3500 daN", "51": "3600 daN", "52": "3700 daN", "53": "3800 daN", "54": "3900 daN", "55": "4000 daN", "56": "4200 daN", "57": "4300 daN", "58": "4400 daN", "59": "4500 daN", "60": "4600 daN", "61": "4700 daN", "62": "4800 daN", "63": "4900 daN", "64": "5000 daN", "65": "5100 daN", "66": "5700 daN", "67": "Leve (Madeira)", "68": "Médio (Madeira)", "69": "Pesado (Madeira)", "70": "Extra Pesado (Madeira)", "71": "22 (Trilho)", "72": "42 (Trilho)"},
    "ALT": {"0": "Não informado ou não aplicável", "1": "4,3 m", "2": "4,5 m", "3": "5 m", "4": "6 m", "5": "7 m", "6": "7,5 m", "7": "8 m", "8": "8,5 m", "9": "9 m", "10": "10 m", "11": "10,5 m", "12": "11 m", "13": "12 m", "14": "13 m", "15": "14 m", "16": "15 m", "17": "16 m", "18": "17 m", "19": "17,5 m", "20": "18 m", "21": "19 m", "22": "20 m", "23": "20,5 m", "24": "21 m", "25": "21,5 m", "26": "22 m", "27": "23 m", "28": "23,5 m", "29": "24 m", "30": "24,6 m", "31": "25 m", "32": "26 m", "33": "26,6 m", "34": "27 m", "35": "27,6 m", "36": "27,7 m", "37": "28 m", "38": "28,6 m", "39": "28,7 m", "40": "29 m", "41": "29,6 m", "42": "29,7 m", "43": "30 m", "44": "30,2 m", "45": "31 m", "46": "32 m", "47": "33 m", "48": "34 m", "49": "35 m", "50": "36 m", "51": "37 m", "52": "38 m", "53": "39 m", "54": "40 m", "55": "43 m", "56": "44 m", "57": "45 m", "58": "46 m", "59": "46 m", "60": "47 m", "61": "48 m", "62": "49 m", "63": "50 m", "64": "51 m", "65": "52 m", "66": "56 m", "67": "64 m", "68": "66 m", "69": "84 m"},
    "ARE_LOC": {"0": "Não informado", "UB": "Urbano", "NU": "Não Urbano"},
    "MUN": {"5100102": "Acorizal", "5100201": "Água Boa", "5100250": "Alta Floresta", "5100300": "Alto Araguaia", "5100359": "Alto Boa Vista", "5100409": "Alto Garças", "5100508": "Alto Paraguai", "5100607": "Alto Taquari", "5100805": "Apiacás", "5101001": "Araguaiana", "5101209": "Araguainha", "5101258": "Araputanga", "5101308": "Arenápolis", "5101407": "Aripuanã", "5101605": "Barão de Melgaço", "5101704": "Barra do Bugres", "5101803": "Barra do Garças", "5101837": "Boa Esperança do Norte", "5101852": "Bom Jesus do Araguaia", "5101902": "Brasnorte", "5102504": "Cáceres", "5102603": "Campinápolis", "5102637": "Campo Novo do Parecis", "5102678": "Campo Verde", "5102686": "Campos de Júlio", "5102694": "Canabrava do Norte", "5102702": "Canarana", "5102793": "Carlinda", "5102850": "Castanheira", "5103007": "Chapada dos Guimarães", "5103056": "Cláudia", "5103106": "Cocalinho", "5103205": "Colíder", "5103254": "Colniza", "5103304": "Comodoro", "5103353": "Confresa", "5103361": "Conquista D'Oeste", "5103379": "Cotriguaçu", "5103403": "Cuiabá", "5103437": "Curvelândia", "5103452": "Denise", "5103502": "Diamantino", "5103601": "Dom Aquino", "5103700": "Feliz Natal", "5103809": "Figueirópolis D'Oeste", "5103858": "Gaúcha do Norte", "5103908": "General Carneiro", "5103957": "Glória D'Oeste", "5104104": "Guarantã do Norte", "5104203": "Guiratinga", "5104500": "Indiavaí", "5104526": "Ipiranga do Norte", "5104542": "Itanhangá", "5104559": "Itaúba", "5104609": "Itiquira", "5104807": "Jaciara", "5104906": "Jangada", "5105002": "Jauru", "5105101": "Juara", "5105150": "Juína", "5105176": "Juruena", "5105200": "Juscimeira", "5105234": "Lambari D'Oeste", "5105259": "Lucas do Rio Verde", "5105309": "Luciara", "5105580": "Marcelândia", "5105606": "Matupá", "5105622": "Mirassol d'Oeste", "5105903": "Nobres", "5106000": "Nortelândia", "5106109": "Nossa Senhora do Livramento", "5106158": "Nova Bandeirantes", "5106208": "Nova Brasilândia", "5106216": "Nova Canaã do Norte", "5108808": "Nova Guarita", "5106182": "Nova Lacerda", "5108857": "Nova Marilândia", "5108907": "Nova Maringá", "5108956": "Nova Monte Verde", "5106224": "Nova Mutum", "5106174": "Nova Nazaré", "5106232": "Nova Olímpia", "5106190": "Nova Santa Helena", "5106240": "Nova Ubiratã", "5106257": "Nova Xavantina", "5106273": "Novo Horizonte do Norte", "5106265": "Novo Mundo", "5106315": "Novo Santo Antônio", "5106281": "Novo São Joaquim", "5106299": "Paranaíta", "5106307": "Paranatinga", "5106372": "Pedra Preta", "5106422": "Peixoto de Azevedo", "5106455": "Planalto da Serra", "5106505": "Poconé", "5106653": "Pontal do Araguaia", "5106703": "Ponte Branca", "5106752": "Pontes e Lacerda", "5106778": "Porto Alegre do Norte", "5106828": "Porto Esperidião", "5106851": "Porto Estrela", "5106802": "Porto dos Gaúchos", "5107008": "Poxoréu", "5107040": "Primavera do Leste", "5107065": "Querência", "5107156": "Reserva do Cabaçal", "5107180": "Ribeirão Cascalheira", "5107198": "Ribeirãozinho", "5107206": "Rio Branco", "5107578": "Rondolândia", "5107602": "Rondonópolis", "5107701": "Rosário Oeste", "5107750": "Salto do Céu", "5107248": "Santa Carmem", "5107743": "Santa Cruz do Xingu", "5107768": "Santa Rita do Trivelato", "5107776": "Santa Terezinha", "5107263": "Santo Afonso", "5107800": "Santo Antônio de Leverger", "5107792": "Santo Antônio do Leste", "5107859": "São Félix do Araguaia", "5107297": "São José do Povo", "5107305": "São José do Rio Claro", "5107354": "São José do Xingu", "5107107": "São José dos Quatro Marcos", "5107404": "São Pedro da Cipa", "5107875": "Sapezal", "5107883": "Serra Nova Dourada", "5107909": "Sinop", "5107925": "Sorriso", "5107941": "Tabaporã", "5107958": "Tangará da Serra", "5108006": "Tapurah", "5108055": "Terra Nova do Norte", "5108105": "Tesouro", "5108204": "Torixoréu", "5108303": "União do Sul", "5108352": "Vale de São Domingos", "5108402": "Várzea Grande", "5108501": "Vera", "5105507": "Vila Bela da Santíssima Trindade", "5108600": "Vila Rica"},
    "SITCONT": {"0": "Não informado", "AT1": "Existente no campo e na contabilidade", "AT2": "Inexistente no campo e existente na contabilidade", "SF": "Existente no campo e inexistente na contabilidade", "AL": "Em trânsito ou almoxarifado"},
}


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


def de_para(series, mapa):
    """Traduz códigos -> rótulos. Se o valor não for um código conhecido, mantém como está."""
    def conv(v):
        if pd.isna(v):
            return None
        k = str(v)
        if k.endswith(".0"):
            k = k[:-2]
        return mapa.get(k, mapa.get(str(v), str(v)))
    return series.map(conv)


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


def grafico_contagem(df, col, titulo, top_n=None):
    if col is None or col not in df.columns or df.empty or df[col].dropna().empty:
        st.info(f"Sem dados para: {titulo}")
        return
    cont = df[col].dropna().value_counts().reset_index()
    cont.columns = [col, "Quantidade"]
    if top_n:
        cont = cont.nlargest(top_n, "Quantidade")
    try:
        cont["_ord"] = pd.to_numeric(cont[col])
        cont = cont.sort_values("_ord").drop(columns="_ord")
    except (ValueError, TypeError):
        cont = cont.sort_values("Quantidade", ascending=False)
    cont[col] = cont[col].astype(str)
    fig = px.bar(cont, x=col, y="Quantidade", title=titulo, text="Quantidade")
    fig.update_traces(textposition="outside")
    fig.update_layout(margin=dict(l=10, r=10, t=45, b=10), height=340, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)


def grafico_extensao(df, col, comp_col, titulo):
    if col not in df.columns or comp_col not in df.columns or df.empty:
        st.info(f"Sem dados para: {titulo}")
        return
    tmp = df[[col, comp_col]].copy()
    tmp[comp_col] = pd.to_numeric(tmp[comp_col], errors="coerce")
    tmp = tmp.dropna(subset=[comp_col])
    if tmp.empty:
        st.info(f"Sem dados para: {titulo}")
        return
    agg = tmp.groupby(col, dropna=True)[comp_col].sum().div(1000.0).reset_index()
    agg.columns = [col, "Extensão (km)"]
    agg[col] = agg[col].astype(str)
    agg = agg.sort_values("Extensão (km)", ascending=False)
    fig = px.bar(agg, x=col, y="Extensão (km)", title=titulo, text="Extensão (km)")
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(margin=dict(l=10, r=10, t=45, b=10), height=340, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)


@st.cache_data(show_spinner="Carregando e preparando dados...")
def preparar_dados(path_se, path_ldat, path_est, path_pont):
    gdf_se = gpd.read_file(path_se).to_crs(epsg=4326)
    gdf_ldat = gpd.read_file(path_ldat).to_crs(epsg=4326)
    gdf_est = gpd.read_file(path_est).to_crs(epsg=4326)
    gdf_pont = gpd.read_file(path_pont).to_crs(epsg=4326)

    gdf_se = gdf_se[gdf_se.geometry.notna() & ~gdf_se.geometry.is_empty].copy()
    gdf_ldat = gdf_ldat[gdf_ldat.geometry.notna() & ~gdf_ldat.geometry.is_empty].copy()
    gdf_est = gdf_est[gdf_est.geometry.notna() & ~gdf_est.geometry.is_empty].copy()
    gdf_pont = gdf_pont[gdf_pont.geometry.notna() & ~gdf_pont.geometry.is_empty].copy()

    gdf_se["coords"] = gdf_se.geometry.apply(extract_coords)
    gdf_ldat["coords"] = gdf_ldat.geometry.apply(extract_coords)
    gdf_est["coords"] = gdf_est.geometry.apply(extract_coords)

    gdf_se = gdf_se[gdf_se["coords"].notna()].copy()
    gdf_ldat = gdf_ldat[gdf_ldat["coords"].notna()].copy()
    gdf_est = gdf_est[gdf_est["coords"].notna()].copy()

    gdf_pont["longitude"] = gdf_pont.geometry.x
    gdf_pont["latitude"] = gdf_pont.geometry.y
    gdf_pont = gdf_pont.dropna(subset=["longitude", "latitude"]).copy()

    # traduz os códigos do PONNOT para rótulos legíveis
    for campo, mapa in dados_ponnot.items():
        if campo in gdf_pont.columns:
            gdf_pont[campo] = de_para(gdf_pont[campo], mapa)

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
        "\nÁrea: " + txt(gdf_pont["ARE_LOC"]) +
        "\nLocalidade: " + txt(gdf_pont["MUN"]) +
        "\nSituação contábil: " + txt(gdf_pont["SITCONT"])
    ).fillna("Sem dados")

    b_se, b_ldat, b_est = gdf_se.total_bounds, gdf_ldat.total_bounds, gdf_est.total_bounds
    minx = min(b_se[0], b_ldat[0], b_est[0]); miny = min(b_se[1], b_ldat[1], b_est[1])
    maxx = max(b_se[2], b_ldat[2], b_est[2]); maxy = max(b_se[3], b_ldat[3], b_est[3])
    bounds = (minx, miny, maxx, maxy)

    df_se  = pd.DataFrame(gdf_se[["coords", "tooltip"]])
    df_est = pd.DataFrame(gdf_est[["coords", "tooltip"]])

    keep_ldat = ["coords", "tooltip"] + [c for c in ([COL_LDAT_NOME, COL_SE_ORIGEM, COL_COMP, COL_TIPO_CABO, COL_TENSAO] + COLS_CONEXAO_LDAT) if c in gdf_ldat.columns]
    df_ldat = pd.DataFrame(gdf_ldat[keep_ldat])

    keep_pont = ["longitude", "latitude", "tooltip", COL_ID_PONT] + [c for c in ["ALT", "ESF", "MAT", "MUN"] if c in gdf_pont.columns]
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

# ------------------- FILTROS (SE de origem -> Nome da LDAT) -------------------
c1, c2 = st.columns(2)
with c1:
    sel_se = st.multiselect("SE de origem", opcoes(df_ldat, COL_SE_ORIGEM))
df_ldat_1 = aplicar(df_ldat, COL_SE_ORIGEM, sel_se)

with c2:
    sel_ldat = st.multiselect("Nome da LDAT", opcoes(df_ldat_1, COL_LDAT_NOME))
df_ldat_2 = aplicar(df_ldat_1, COL_LDAT_NOME, sel_ldat)

cols_ok = [c for c in COLS_CONEXAO_LDAT if c in df_ldat_2.columns]
if cols_ok:
    ids_estruturas = pd.unique(df_ldat_2[cols_ok].astype(str).values.ravel())
    df_pont_f = df_pont[df_pont[COL_ID_PONT].astype(str).isin(ids_estruturas)]
else:
    df_pont_f = df_pont

df_ldat_r = df_ldat_2[["coords", "tooltip"]]
df_pont_r = df_pont_f[["longitude", "latitude", "tooltip"]].dropna(subset=["longitude", "latitude"])

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

# ------------------- PAINEL B.I. (reflete os filtros) -------------------
st.divider()

qtd_estruturas = len(df_pont_f)
qtd_ldat = df_ldat_2[COL_LDAT_NOME].nunique() if COL_LDAT_NOME in df_ldat_2.columns else len(df_ldat_2)
qtd_se = df_ldat_2[COL_SE_ORIGEM].nunique() if COL_SE_ORIGEM in df_ldat_2.columns else 0
if COL_COMP in df_ldat_2.columns:
    ext_km = pd.to_numeric(df_ldat_2[COL_COMP], errors="coerce").sum() / 1000.0
else:
    ext_km = 0.0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Estruturas", f"{qtd_estruturas:,}".replace(",", "."))
k2.metric("Extensão total (km)", f"{ext_km:,.1f}".replace(",", "X").replace(".", ",").replace("X", "."))
k3.metric("LDAT (nº)", f"{qtd_ldat:,}".replace(",", "."))
k4.metric("SE de origem (nº)", f"{qtd_se:,}".replace(",", "."))

g1, g2 = st.columns(2)
with g1:
    grafico_contagem(df_pont_f, "ALT", "Estruturas por Altura")
with g2:
    grafico_contagem(df_pont_f, "ESF", "Estruturas por Esforço")

g3, g4 = st.columns(2)
with g3:
    grafico_extensao(df_ldat_2, COL_TIPO_CABO, COL_COMP, "Extensão por Tipo de Cabo (km)")
with g4:
    grafico_extensao(df_ldat_2, COL_TENSAO, COL_COMP, "Extensão por Tensão Nominal (km)")

g5, g6 = st.columns(2)
with g5:
    grafico_contagem(df_pont_f, "MAT", "Estruturas por Material")
with g6:
    grafico_contagem(df_pont_f, "MUN", "Estruturas por Município", top_n=20)

if df_ldat_r.empty and df_pont_r.empty:
    st.info("Nenhuma LDAT/estrutura corresponde aos filtros selecionados.")
