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

#   POSTO
# definindo nome das colunas
colunas_posto = ['IdPosto','NomePosto', 'CidadePosto', 'BairroPosto', 'RuaPosto', 'NumeroPosto']
# transformando csv em dataframe
dados_tabela_posto = pd.read_csv('./tabelas/tabela_posto.csv', names=colunas_posto, sep=';')

#   COMBUSTIVEL
# definindo nome das colunas
colunas_combustivel = ['IdCombustivel','TipoCombustivel']
# transformando csv em dataframe
dados_tabela_combustivel = pd.read_csv('./tabelas/tabela_combustivel.csv', names=colunas_combustivel, sep=';')

#   COLETA
# definindo nome das colunas
colunas_coleta = ['IdColeta','DataColeta', 'FkPosto', 'FkCombustivel','ValorCombustivel' ]
# transformando csv em dataframe
dados_tabela_coleta = pd.read_csv('./tabelas/tabela_coleta.csv', names=colunas_coleta, sep=';')

# Selectbox para o usuário selecionar qual tabela quer visualizar
tabelas = {
    'Dados do Posto' : dados_tabela_posto,
    'Dados da Coleta' : dados_tabela_coleta ,
    'Dados do Combustivel' : dados_tabela_combustivel
    
}
tabela_selecionada = st.selectbox('Selecione a tabela', list(tabelas.keys()))

# Exibe a tabela de dados na interface
st.write('Dashboard de Coleta de Combustível')
st.dataframe(tabelas[tabela_selecionada])
