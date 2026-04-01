import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from io import BytesIO

st.markdown("""
    <style>
    /* Remove borda/caixa do expander (fechado e aberto) */
    div[data-testid="stExpander"] details,
    div[data-testid="stExpander"] details[open] {
    border: 0 !important;
    box-shadow: none !important;
    background: transparent !important;
    }

    /* TÍTULO do expander — sem borda, sem fundo */
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] details[open] summary {
    border: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    outline: none !important;
    }

    /* Remove fundo no hover */
    div[data-testid="stExpander"] summary:hover {
    background: transparent !important;
    }

    /* Remove fundo quando recebe foco (clique/teclado) */
    div[data-testid="stExpander"] summary:focus,
    div[data-testid="stExpander"] summary:focus-visible {
    background: transparent !important;
    outline: none !important;
    box-shadow: none !important;
    }

    /* Remove a linha separadora que aparece ao expandir */
    div[data-testid="stExpander"] details > div,
    div[data-testid="stExpander"] details[open] > div {
    border-top: 0 !important;
    box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="PMAs", layout="wide")

DB_PATH = "banco_d_pma/dados_pmas.db"

@st.cache_data(show_spinner=False)
def list_tables(db_path: str) -> list[str]:
    with sqlite3.connect(db_path) as con:
        cursor = con.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        return [t[0] for t in cursor.fetchall()]

@st.cache_data(show_spinner=False)
def load_df(db_path: str, tab_name: str) -> pd.DataFrame:
    query = f'SELECT * FROM "{tab_name}"'
    with sqlite3.connect(db_path) as con:
        return pd.read_sql_query(query, con)

tabelas = list_tables(DB_PATH)

box0 = st.sidebar.selectbox("Selecionar Dados", tabelas, index=len(tabelas) - 1)

df = load_df(DB_PATH, box0)

#Substituir os valores Null quando não há OCM pelo valor orçado
df.loc[df["preco_unitario"].isna(), "preco_unitario"] = df["valor_orcado"]

#Susbstitur os elementos da coluna    
subst = {
    "C": "Cancelado",
    "E": "Em andamento",
    "S": "Concluído"
}

df["status"] = df["sit_pma"]
df["status"] = df["status"].map(subst)

#criar coluna no dataframe com status do PMA (PMA ou OCM)
df["status_p_o"] = df["numocm_pma_mat"]
df["status_p_o"] = df["status_p_o"].astype("string")
df.loc[df["status_p_o"].notna(), "status_p_o"] = "OCM"
df.loc[df["status_p_o"].isna(), "status_p_o"] = "PMA"

#Criar coluna no dataframe pra contagem do número de PMAs
df["cont_pma"] = 1

#criar coluna no dataframe com o valor total do PMA
df["Valor Total"] = df["qtd_pma_ent"]*df["preco_unitario"]

#Converter datas para pd.datetime e criar nova coluna
df["abert_pma"] = pd.to_datetime(df["dth_pmacriacao"]).dt.normalize()
df["prev_rec_pma"] = pd.to_datetime(df["data_previsao"]).dt.normalize()
df["recebim_pma"] = pd.to_datetime(df["data_pma_rec"]).dt.normalize()

#Criar os itens do filtro Número do projeto
list_lot = sorted(df["num_projeto_sigco"].dropna().unique())

#Concatenar duas listas
Opcoes = ["Todos"] + list_lot

box1 = st.sidebar.selectbox("Selecionar Projeto SIGCO", Opcoes)

flag1 = True

if box1 == "Todos":
    box1 = list_lot
    flag1 = True
else:
    box1 = [box1]
    flag1 = False

list_lot_cc = sorted(set(list(df.loc[df["num_projeto_sigco"].isin(box1), "codarea_pma"])))

box_cc = st.sidebar.multiselect("Selecionar Centro de Custo", list_lot_cc, default=[150600000, 193203000])


list_lot2 = sorted(set(list(df.loc[df["num_projeto_sigco"].isin(box1) & df["codarea_pma"].isin(box_cc), "dscapc_pma"])))

box2 = st.sidebar.multiselect("Selecionar Obra", list_lot2, default=list_lot2)


list_lot3 = sorted(set(list(df.loc[(df["num_projeto_sigco"].isin(box1)) & (df["codarea_pma"].isin(box_cc)) & (df["dscapc_pma"].isin(box2)), "dsccls_mat"])))

box3 = st.sidebar.multiselect("Selecionar Classe do Material", list_lot3, default=list_lot3)

check_canc = st.sidebar.checkbox("Mostrar Cancelados")
if check_canc:
    pass
else:
    df = df.loc[df["status"].isin(["Em andamento", "Concluído"])]


if flag1:
    st.markdown(
    f"## Todos os Projetos")
    st.write("")
else:
    st.markdown(
    f"## Projeto {box1[0]}")
    st.write("")

df.loc[df["nomecdr"].isna(), "nomecdr"] = "xVAZIOx"
df.loc[df["nomecpa"].isna(), "nomecpa"] = "xVAZIOx"
df.loc[df["pedido_ws"].isna(), "pedido_ws"] = 0
df.loc[df["numocm_pma_mat"].isna(), "numocm_pma_mat"] = 0


with st.expander("Filtrar", expanded=True):
    col13, col14, col15, col16, col17 = st.columns(5)
    with col13:
        list_f_codcta_pma = sorted(df.loc[(df["num_projeto_sigco"].isin(box1)) & 
                                          (df["codarea_pma"].isin(box_cc)) &
                                          (df["dscapc_pma"].isin(box2)) & 
                                          (df["dsccls_mat"].isin(box3)),
                                          "codcta_pma"].dropna().unique())
        list_f_codcta_pma = ["Todos"] + list_f_codcta_pma
        box_codcta_pma = st.selectbox("Selecionar Conta", list_f_codcta_pma)
        if box_codcta_pma == "Todos":
            box_codcta_pma = list_f_codcta_pma
        else:
            box_codcta_pma = [box_codcta_pma]
    with col14:
        list_f_codsct_pma = sorted(df.loc[(df["num_projeto_sigco"].isin(box1)) & 
                                          (df["codarea_pma"].isin(box_cc)) &
                                          (df["dscapc_pma"].isin(box2)) & 
                                          (df["dsccls_mat"].isin(box3)) &
                                          (df["codcta_pma"].isin(box_codcta_pma)),
                                          "codsct_pma"].dropna().unique())
        list_f_codsct_pma = ["Todos"] + list_f_codsct_pma
        box_codsct_pma = st.selectbox("Selecionar SubConta", list_f_codsct_pma)
        if box_codsct_pma == "Todos":
            box_codsct_pma = list_f_codsct_pma
        else:
            box_codsct_pma = [box_codsct_pma]
    with col15:
        list_f_status = sorted(df.loc[(df["num_projeto_sigco"].isin(box1)) & 
                                          (df["codarea_pma"].isin(box_cc)) &
                                          (df["dscapc_pma"].isin(box2)) & 
                                          (df["dsccls_mat"].isin(box3)) &
                                          (df["codcta_pma"].isin(box_codcta_pma)) &
                                          (df["codsct_pma"].isin(box_codsct_pma)),
                                          "status"].dropna().unique())
        list_f_status = ["Todos"] + list_f_status
        box_status = st.selectbox("Selecionar Status do PMA", list_f_status)
        if box_status == "Todos":
            box_status = list_f_status
        else:
            box_status = [box_status]
    with col16:
        list_f_nomecdr = sorted(df.loc[(df["num_projeto_sigco"].isin(box1)) & 
                                          (df["codarea_pma"].isin(box_cc)) &
                                          (df["dscapc_pma"].isin(box2)) &
                                          (df["dsccls_mat"].isin(box3)) &
                                          (df["codcta_pma"].isin(box_codcta_pma)) &
                                          (df["codsct_pma"].isin(box_codsct_pma)) &
                                          (df["status"].isin(box_status)),
                                          "nomecdr"].dropna().unique())
        list_f_nomecdr = ["Todos"] + list_f_nomecdr
        box_list_f_nomecdr = st.selectbox("Selecionar Fornecedor", list_f_nomecdr)
        if box_list_f_nomecdr == "Todos":
            box_list_f_nomecdr = list_f_nomecdr
        else:
            box_list_f_nomecdr = [box_list_f_nomecdr]
    with col17:
        list_f_nomecpa = sorted(df.loc[(df["num_projeto_sigco"].isin(box1)) & 
                                          (df["codarea_pma"].isin(box_cc)) &
                                          (df["dscapc_pma"].isin(box2)) & 
                                          (df["dsccls_mat"].isin(box3)) &
                                          (df["codcta_pma"].isin(box_codcta_pma)) &
                                          (df["codsct_pma"].isin(box_codsct_pma)) &
                                          (df["status"].isin(box_status)) &
                                          (df["nomecdr"].isin(box_list_f_nomecdr)),
                                          "nomecpa"].dropna().unique())
        list_f_nomecpa = ["Todos"] + list_f_nomecpa
        box_list_f_nomecpa = st.selectbox("Selecionar Comprador", list_f_nomecpa)
        if box_list_f_nomecpa == "Todos":
            box_list_f_nomecpa = list_f_nomecpa
        else:
            box_list_f_nomecpa = [box_list_f_nomecpa]
    
    col18, col19, col20, col21, col22 = st.columns(5)
    with col18:
        list_f_pedido_ws = sorted(df.loc[(df["num_projeto_sigco"].isin(box1)) & 
                                          (df["codarea_pma"].isin(box_cc)) &
                                          (df["dscapc_pma"].isin(box2)) & 
                                          (df["dsccls_mat"].isin(box3)) &
                                          (df["codcta_pma"].isin(box_codcta_pma)) &
                                          (df["codsct_pma"].isin(box_codsct_pma)) &
                                          (df["status"].isin(box_status)) &
                                          (df["nomecdr"].isin(box_list_f_nomecdr)) &
                                          (df["nomecpa"].isin(box_list_f_nomecpa)),
                                          "pedido_ws"].dropna().unique())
        list_f_pedido_ws = ["Todos"] + list_f_pedido_ws
        box_pedido_ws = st.selectbox("Selecionar nº Websupply", list_f_pedido_ws)
        if box_pedido_ws == "Todos":
            box_pedido_ws = list_f_pedido_ws
        else:
            box_pedido_ws = [box_pedido_ws]
    with col19:
        list_f_numpma_pma = sorted(df.loc[(df["num_projeto_sigco"].isin(box1)) & 
                                          (df["codarea_pma"].isin(box_cc)) &
                                          (df["dscapc_pma"].isin(box2)) &
                                          (df["dsccls_mat"].isin(box3)) &
                                          (df["codcta_pma"].isin(box_codcta_pma)) &
                                          (df["codsct_pma"].isin(box_codsct_pma)) &
                                          (df["status"].isin(box_status)) &
                                          (df["nomecdr"].isin(box_list_f_nomecdr)) &
                                          (df["nomecpa"].isin(box_list_f_nomecpa)) &
                                          (df["pedido_ws"].isin(box_pedido_ws)),
                                          "numpma_pma"].dropna().unique())
        list_f_numpma_pma = ["Todos"] + list_f_numpma_pma
        box_numpma_pma = st.selectbox("Selecionar nº PMA", list_f_numpma_pma)
        if box_numpma_pma == "Todos":
            box_numpma_pma = list_f_numpma_pma
        else:
            box_numpma_pma = [box_numpma_pma]
    with col20:
        list_f_numocm_pma_mat = sorted(df.loc[(df["num_projeto_sigco"].isin(box1)) & 
                                          (df["codarea_pma"].isin(box_cc)) &
                                          (df["dscapc_pma"].isin(box2)) & 
                                          (df["dsccls_mat"].isin(box3)) &
                                          (df["codcta_pma"].isin(box_codcta_pma)) &
                                          (df["codsct_pma"].isin(box_codsct_pma)) &
                                          (df["status"].isin(box_status)) &
                                          (df["nomecdr"].isin(box_list_f_nomecdr)) &
                                          (df["nomecpa"].isin(box_list_f_nomecpa)) &
                                          (df["pedido_ws"].isin(box_pedido_ws)) &
                                          (df["numpma_pma"].isin(box_numpma_pma)),
                                          "numocm_pma_mat"].dropna().unique())
        list_f_numocm_pma_mat = ["Todos"] + list_f_numocm_pma_mat
        box_list_f_numocm_pma_mat = st.selectbox("Selecionar nº OCM", list_f_numocm_pma_mat)
        if box_list_f_numocm_pma_mat == "Todos":
            box_list_f_numocm_pma_mat = list_f_numocm_pma_mat
        else:
            box_list_f_numocm_pma_mat = [box_list_f_numocm_pma_mat]
    with col21:
        list_f_codmat = sorted(df.loc[(df["num_projeto_sigco"].isin(box1)) & 
                                          (df["codarea_pma"].isin(box_cc)) &
                                          (df["dscapc_pma"].isin(box2)) & 
                                          (df["dsccls_mat"].isin(box3)) &
                                          (df["codcta_pma"].isin(box_codcta_pma)) &
                                          (df["codsct_pma"].isin(box_codsct_pma)) &
                                          (df["status"].isin(box_status)) &
                                          (df["nomecdr"].isin(box_list_f_nomecdr)) &
                                          (df["nomecpa"].isin(box_list_f_nomecpa)) &
                                          (df["pedido_ws"].isin(box_pedido_ws)) &
                                          (df["numpma_pma"].isin(box_numpma_pma)) &
                                          (df["numocm_pma_mat"].isin(box_list_f_numocm_pma_mat)),
                                          "codmat"].dropna().unique())
        list_f_codmat = ["Todos"] + list_f_codmat
        box_list_f_codmat = st.selectbox("Selecionar Cód. do Material", list_f_codmat)
        if box_list_f_codmat == "Todos":
            box_list_f_codmat = list_f_codmat
        else:
            box_list_f_codmat = [box_list_f_codmat]
    with col22:
        list_f_dscmat = sorted(df.loc[(df["num_projeto_sigco"].isin(box1)) & 
                                          (df["codarea_pma"].isin(box_cc)) &
                                          (df["dscapc_pma"].isin(box2)) & 
                                          (df["dsccls_mat"].isin(box3)) &
                                          (df["codcta_pma"].isin(box_codcta_pma)) &
                                          (df["codsct_pma"].isin(box_codsct_pma)) &
                                          (df["status"].isin(box_status)) &
                                          (df["nomecdr"].isin(box_list_f_nomecdr)) &
                                          (df["nomecpa"].isin(box_list_f_nomecpa)) &
                                          (df["pedido_ws"].isin(box_pedido_ws)) &
                                          (df["numpma_pma"].isin(box_numpma_pma)) &
                                          (df["numocm_pma_mat"].isin(box_list_f_numocm_pma_mat)) &
                                          (df["codmat"].isin(box_list_f_codmat)),
                                          "dscmat"].dropna().unique())
        list_f_dscmat = ["Todos"] + list_f_dscmat
        box_list_f_dscmat = st.selectbox("Selecionar Material", list_f_dscmat)
        if box_list_f_dscmat == "Todos":
            box_list_f_dscmat = list_f_dscmat
        else:
            box_list_f_dscmat = [box_list_f_dscmat]
    
    df_filtrada = df.loc[(df["num_projeto_sigco"].isin(box1)) & 
                        (df["codarea_pma"].isin(box_cc)) &
                        (df["dscapc_pma"].isin(box2)) & 
                        (df["dsccls_mat"].isin(box3)) &
                        (df["numpma_pma"].isin(box_numpma_pma)) & 
                        (df["numocm_pma_mat"].isin(box_list_f_numocm_pma_mat)) &
                        (df["codmat"].isin(box_list_f_codmat)) &
                        (df["dscmat"].isin(box_list_f_dscmat)) &
                        (df["nomecdr"].isin(box_list_f_nomecdr)) &
                        (df["nomecpa"].isin(box_list_f_nomecpa)) &
                        (df["codcta_pma"].isin(box_codcta_pma)) &
                        (df["codsct_pma"].isin(box_codsct_pma)) &
                        (df["status"].isin(box_status)) &
                        (df["pedido_ws"].isin(box_pedido_ws))]

    options_per = ["Abertura de PMA", "Previsão de Recebimento", "Data de Recebimento"]
    selection_per = st.pills("Filtrar por Período de:", options_per, selection_mode="single")

    if selection_per == "Abertura de PMA":
        list_date = (
            df_filtrada["abert_pma"]
            .dropna()
            .sort_values()
            .unique()
        )

        data_min = list_date[0]
        data_max = list_date[-1]

        start_date, end_date = st.select_slider(
            "Selecionar Previsão de Recebimento",
            options=list_date,
            value=(data_min, data_max),
            format_func=lambda x: x.strftime("%d/%m/%Y")
        )

        df_filtrada = df_filtrada.loc[
            df_filtrada["abert_pma"].between(start_date, end_date)
        ]

    elif selection_per == "Previsão de Recebimento":
        list_date_rec = (
            df_filtrada["prev_rec_pma"]
            .dropna()
            .sort_values()
            .unique()
        )

        data_min_rec = list_date_rec[0]
        data_max_rec = list_date_rec[-1]

        start_date, end_date = st.select_slider(
            "Selecionar Previsão de Recebimento",
            options=list_date_rec,
            value=(data_min_rec, data_max_rec),
            format_func=lambda x: x.strftime("%d/%m/%Y")
        )

        df_filtrada = df_filtrada.loc[
            df_filtrada["prev_rec_pma"].between(start_date, end_date)
        ]

    elif selection_per == "Data de Recebimento":
        list_date = (
            df_filtrada["recebim_pma"]
            .dropna()
            .sort_values()
            .unique()
        )

        data_min = list_date[0]
        data_max = list_date[-1]

        start_date, end_date = st.select_slider(
            "Selecionar Previsão de Recebimento",
            options=list_date,
            value=(data_min, data_max),
            format_func=lambda x: x.strftime("%d/%m/%Y")
        )

        df_filtrada = df_filtrada.loc[
            df_filtrada["recebim_pma"].between(start_date, end_date)
        ]

filtro_sigco = df_filtrada.loc[:, [
                        "codmat", 
                        "dscmat", 
                        "numpma_pma", 
                        "dscapc_pma", 
                        "num_projeto_sigco", 
                        "qtd_pma_ent", 
                        "preco_unitario", 
                        "Valor Total",
                        "dsccls_mat",
                        "numocm_pma_mat",
                        "nomecdr",
                        "nomecpa",
                        "codcta_pma",
                        "codsct_pma",
                        "status",
                        "pedido_ws",
                        "abert_pma",
                        "prev_rec_pma",
                        "recebim_pma",
                        "codarea_pma"
                        ]
                        ]

filtro_sigco2 = df_filtrada.copy()

data = dict(
status=filtro_sigco2["status"],
status_comp=filtro_sigco2["status_p_o"],
categoria=filtro_sigco2["dsccls_mat"],
sigco=filtro_sigco2["num_projeto_sigco"],
item=filtro_sigco2["numpma_pma"],
valor_t=filtro_sigco2["Valor Total"],
quantidade=filtro_sigco2["cont_pma"]
)

col9, col10 = st.columns(2)

with col9:
    
    with st.expander("Gráfico Radial Hierárquico"):
        col11, col12 = st.columns(2)
        with col11:
            fig1 = px.sunburst(
            data_frame=data,
            path=["status", "status_comp","categoria", "sigco","item"],
            values="valor_t"
            )

            fig1.update_traces(
            hovertemplate="<b>%{label}</b><br>" +
                        "Valor: R$ %{value:,.2f}<br>" +
                        "Perc: %{percentParent:.1%} do nível pai" +
                        "<extra></extra>",
            marker=dict(line=dict(color="white", width=2)),
            insidetextorientation="radial"
            )

            fig1.update_layout(
            margin=dict(t=60, l=0, r=0, b=0),
            uniformtext=dict(minsize=11, mode="hide")
            )

            st.plotly_chart(fig1, use_container_width=True, key="fig1")

        
        with col12:
            fig2 = px.sunburst(
            data_frame=data,
            path=["status", "status_comp","categoria", "sigco","item"],
            values="quantidade"
            )

            fig2.update_traces(
            hovertemplate="<b>%{label}</b><br>" +
                        "Quant.:  %{value:.0f}<br>" +
                        "Perc: %{percentParent:.1%} do nível pai" +
                        "<extra></extra>",
            marker=dict(line=dict(color="white", width=2)),
            insidetextorientation="radial"
            )

            fig2.update_layout(
            margin=dict(t=60, l=0, r=0, b=0),
            uniformtext=dict(minsize=11, mode="hide")
            )

            st.plotly_chart(fig2, use_container_width=True, key="fig2")
    
    #with col10:
        

event = st.dataframe(filtro_sigco, column_config={
    "preco_unitario": st.column_config.ProgressColumn("Preço unitário", width="small", format="R$ %.2f", min_value=df['preco_unitario'].min(), max_value=df['preco_unitario'].max()),
    "Valor Total": st.column_config.ProgressColumn("Valor Total", width="small", format="R$ %.2f", min_value=df['Valor Total'].min(), max_value=df['Valor Total'].max()),
    "qtd_pma_ent": st.column_config.NumberColumn("Quantidade"),
    "dscapc_pma": st.column_config.TextColumn("Obra"),
    "dscmat": st.column_config.TextColumn("Descrição do Material"),
    "codmat": st.column_config.TextColumn("Cód. do Material"),
    "numpma_pma": st.column_config.TextColumn("Num. PMA"),
    "num_projeto_sigco": st.column_config.TextColumn("Num. SIGCO"),
    "dsccls_mat": st.column_config.TextColumn("Classe do Material"),
    "numocm_pma_mat": st.column_config.TextColumn("Núm. OCM"),
    "nomecdr": st.column_config.TextColumn("Fornecedor"),
    "nomecpa": st.column_config.TextColumn("Comprador"),
    "codcta_pma": st.column_config.TextColumn("Conta"),
    "codsct_pma": st.column_config.TextColumn("SubConta"),
    "codarea_pma": st.column_config.TextColumn("Centro de Custo"),
},
    hide_index=True,
    use_container_width=True,
    on_select="rerun",
    selection_mode="single-row"
)

df_sel = filtro_sigco2.iloc[event.selection.rows]

col1, col2, col3, col4 = st.columns(4)

with col1:
    if df_sel.empty:
        valor = ""
    else:
        valor = df_sel["numpma_pma"].iloc[0]
        valor = str(valor)

    st.session_state["pma_num_1"] = valor
        
    txt = st.text_area("Número do PMA", key="pma_num_1", height=60, disabled=True)

with col2:
    if df_sel.empty:
        valor = ""
    else:
        valor = df_sel["dth_pmacriacao"].iloc[0]
        valor = str(valor)

    st.session_state["pma_num_2"] = valor
        
    txt = st.text_area("Data de Abertura PMA", key="pma_num_2", height=60, disabled=True)

with col3:
    if df_sel.empty:
        valor = ""
    else:
        valor = df_sel["numocm_pma_mat"].iloc[0]
        valor = str(valor)

    st.session_state["pma_num_3"] = valor
        
    txt = st.text_area("Número de OCM", key="pma_num_3", height=60, disabled=True)

with col4:
    if df_sel.empty:
        valor = ""
    else:
        valor = df_sel["dth_ocm_confirmada"].iloc[0]
        valor = str(valor)

    st.session_state["pma_num_4"] = valor
        
    txt = st.text_area("Data OCM", key="pma_num_4", height=60, disabled=True)

col5, col6, col7, col8 = st.columns(4)

with col5:
    if df_sel.empty:
        valor = ""
    else:
        valor = df_sel["sit_pma"].iloc[0]
        valor = str(valor)
        if valor == "C":
            valor = "Cancelado"
        elif valor == "E":
            valor = "Em andamento"
        elif valor == "S":
            valor = "Concluído"

    st.session_state["pma_num_5"] = valor
        
    txt = st.text_area("Status do PMA", key="pma_num_5", height=60, disabled=True)

with col6:
    if df_sel.empty:
        valor = ""
    else:
        valor = df_sel["data_previsao"].iloc[0]
        valor = str(valor)

    st.session_state["pma_num_6"] = valor
        
    txt = st.text_area("Previsão de Recebimento", key="pma_num_6", height=60, disabled=True)

with col7:
    if df_sel.empty:
        valor = ""
    else:
        valor = df_sel["nomecdr"].iloc[0]
        valor = str(valor)

    st.session_state["pma_num_7"] = valor
        
    txt = st.text_area("Fornecedor", key="pma_num_7", height=60, disabled=True)

with col8:
    if df_sel.empty:
        valor = ""
    else:
        valor = df_sel["data_pma_rec"].iloc[0]
        valor = str(valor)

    st.session_state["pma_num_8"] = valor
        
    txt = st.text_area("Data de Recebimento", key="pma_num_8", height=60, disabled=True)

# df_sel = filtro_sigco.iloc[event.selection.rows]
st.dataframe(df_sel)

buf = BytesIO()
filtro_sigco.to_excel(buf, index=False, sheet_name="PMAs")
buf.seek(0)

st.download_button(
    "Download .xlsx",
    data=buf,
    file_name="Planilha_PMAs.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)