import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3


def pma():

    st.set_page_config(page_title="PMAs", layout="wide")
    
    con = sqlite3.connect("banco_d_pma/dados_pmas.db")

    cursor = con.cursor()

# Listar tabelas do banco de dados
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

# Tranformar lista de tuplas retornada em uma lista comum utilizando list comprehension
    tabelas = [t[0] for t in cursor.fetchall()]

# Filtro para seleção dos dados
    box0 = st.sidebar.selectbox("Selecionar Dados", tabelas, index=len(tabelas) - 1)

    query = f'SELECT * FROM "{box0}"'

    df = pd.read_sql_query(query, con)

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

    df["status_p_o"] = df["numocm_pma_mat"]
    df.loc[df["status_p_o"].notna(), "status_p_o"] = "OCM"
    df.loc[df["status_p_o"].isna(), "status_p_o"] = "PMA"

    df["cont_pma"] = 1

#criar coluna no dataframe com o valor total do PMA
    df["Valor Total"] = df["qtd_pma_ent"]*df["preco_unitario"]

    list_lot = sorted(set(list(df["num_projeto_sigco"])))

    Opcoes = ["Todos"] + list_lot

    box1 = st.sidebar.selectbox("Selecionar Projeto SIGCO", Opcoes)
    
    flag1 = True

    if box1 == "Todos":
        box1 = list_lot
        flag1 = True
    else:
        box1 = [box1]
        flag1 = False

    list_lot2 = sorted(set(list(df.loc[df["num_projeto_sigco"].isin(box1), "dscapc_pma"])))

    box2 = st.sidebar.multiselect("Selecionar Obra", list_lot2, default=list_lot2)

    list_lot3 = sorted(set(list(df.loc[(df["num_projeto_sigco"].isin(box1)) & (df["dscapc_pma"].isin(box2)), "dsccls_mat"])))

    box3 = st.sidebar.multiselect("Selecionar Classe do Material", list_lot3, default=list_lot3)
    
    check_canc = st.sidebar.checkbox("Mostrar Cancelados")
    if check_canc:
        pass
    else:
        df = df.loc[df["status"].isin(["Em andamento", "Concluído"])]

    filtro_sigco = df.loc[(df["num_projeto_sigco"].isin(box1)) & (df["dscapc_pma"].isin(box2)) & (df["dsccls_mat"].isin(box3)), [
        "codmat", "dscmat", "numpma_pma", "dscapc_pma", "qtd_pma_ent", "preco_unitario", "Valor Total"]]
    
    filtro_sigco2 = df.loc[(df["num_projeto_sigco"].isin(box1)) & (df["dscapc_pma"].isin(box2)) & (df["dsccls_mat"].isin(box3))]

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

    
    with col10:
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


    if flag1:
        st.markdown(
        f"## 🏗️ Todos os Projetos")
        st.write("")
    else:
        st.markdown(
        f"## 🏗️ Projeto {box1[0]}")
        st.write("")

    event = st.dataframe(filtro_sigco, column_config={
        "preco_unitario": st.column_config.ProgressColumn("Preço unitário", width="small", format="R$ %.2f", min_value=df['preco_unitario'].min(), max_value=df['preco_unitario'].max()),
        "Valor Total": st.column_config.ProgressColumn("Valor Total", width="small", format="R$ %.2f", min_value=df['Valor Total'].min(), max_value=df['Valor Total'].max()),
        "qtd_pma_ent": st.column_config.NumberColumn("Quantidade"),
        "dscapc_pma": st.column_config.TextColumn("Obra"),
        "dscmat": st.column_config.TextColumn("Descrição do Material"),
        "codmat": st.column_config.TextColumn("Cód. do Material"),
        "numpma_pma": st.column_config.TextColumn("Cód. do Material")
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

if __name__ == "__main__":
    pma()
