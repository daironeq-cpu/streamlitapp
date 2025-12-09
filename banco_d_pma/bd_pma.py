import sqlite3
import pandas as pd


# Adicionar tabela do Excel ao banco de dados
def criar_tab_exc(name_arq_excel, name_bd, name_tab):
    # Ler planilha Excel
    sisup = pd.read_excel(name_arq_excel)

    # Conectar ao banco SQLite
    con = sqlite3.connect(name_bd)

    # Inserir ou substituir tabela
    sisup.to_sql(
        name_tab,
        con,
        if_exists="replace",
        index=False
    )

    # Fechar conexão
    con.close()


# Remover tabela do banco de dados
def del_tab_bd(name_bd, name_tab):
    # Conectar ao banco
    con = sqlite3.connect(name_bd)
    cur = con.cursor()

    # Remover tabela (com proteção IF EXISTS)
    cur.execute(f'DROP TABLE IF EXISTS "{name_tab}"')

    # Salvar mudanças e fechar
    con.commit()
    con.close()




