import pyodbc
import pandas as pd
import streamlit as st
import plotly.express as px

# Injetando CSS para usar a fonte JetBrains Mono
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&display=swap');
    .stTitle {
        font-family: 'JetBrains Mono', monospace;
        font-optical-sizing: auto;
        font-size: 36px;
        font-weight: 700;
        font-style: normal;
    }
    /* Aplicando a fonte JetBrains Mono ao corpo da página */
    body {
        font-family: 'JetBrains Mono', monospace;
    }
    </style>
    """, unsafe_allow_html=True)
st.markdown('<p class="stTitle">Dashboard Coleta de Combustível</p>', unsafe_allow_html=True)


# Função para conectar ao banco de dados usando autenticação do Windows
def conectar_bd():
    conexao = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-SUCSSF7\SQLEXPRESS;'
        'DATABASE=AOP_Banco_de_dados;'
        'Trusted_Connection=yes;'
    )
    return conexao

# Função para carregar dados da tabela coleta com informações das outras tabelas
def carregar_dados(query_select):
    conexao = conectar_bd()
    consulta_sql = query_select
    dados = pd.read_sql(consulta_sql, conexao)
    conexao.close()
    return dados

# Dataframe coleta
dados_coleta = carregar_dados("""
    SELECT *
    FROM Tabela_Coleta
    """)
#Dataframe posto
dados_posto = carregar_dados("""
    SELECT *
    FROM Tabela_Posto
    """)
#Dataframe combustivel
dados_combustivel = carregar_dados("""
    SELECT *
    FROM Tabela_Combustivel
    """)



# Selectbox para o usuário selecionar qual tabela quer visualizar
tabelas = {
    'Dados do Posto' : dados_posto,
    'Dados da Coleta' : dados_coleta,
    'Dados do Combustivel' : dados_combustivel
    
}
tabela_selecionada = st.selectbox('Selecione a tabela', list(tabelas.keys()))

# Exibe a tabela de dados na interface
st.write('Dashboard de Coleta de Combustível')
st.dataframe(tabelas[tabela_selecionada])
