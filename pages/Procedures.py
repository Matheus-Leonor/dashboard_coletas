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
dados_tabela_posto = pd.read_csv('./data/tabela_posto.csv', names=colunas_posto, sep=';')

#   COMBUSTIVEL
# definindo nome das colunas
colunas_combustivel = ['IdCombustivel','TipoCombustivel']
# transformando csv em dataframe
dados_tabela_combustivel = pd.read_csv('./data/tabela_combustivel.csv', names=colunas_combustivel, sep=';')

#   COLETA
# definindo nome das colunas
colunas_coleta = ['IdColeta','DataColeta', 'FkPosto', 'FkCombustivel','ValorCombustivel' ]
# transformando csv em dataframe
dados_tabela_coleta = pd.read_csv('./data/tabela_coleta.csv', names=colunas_coleta, sep=';')

#  DADOS TOAIS
# Unir as tabelas coleta e posto pela chave FkPosto = IdPosto
df_merged1 = pd.merge(dados_tabela_coleta, dados_tabela_posto, left_on='FkPosto', right_on='IdPosto')
# Em seguida, unir com a tabela de combustivel pela chave FkCombustivel = IdCombustivel
# Usar groupby para contar as amostras por NomePosto e TipoCombustivel

dados_totais = pd.merge(df_merged1, dados_tabela_combustivel,  left_on='FkCombustivel', right_on='IdCombustivel')


# Interface Streamlit       
aba1, aba2, aba3 = st.tabs(['Menor Valor de Combustível ', 'Preço Médio Geral',  'Listagem Preço Médio c/ Amostras'])

with aba1:
   # Seleção de parâmetros opcionais
    bairros_disponiveis = ['Todos'] + list(dados_totais['BairroPosto'].unique())
    tipos_combustivel_disponiveis = ['Todos'] + list(dados_totais['TipoCombustivel'].unique())

    bairro_selecionado = st.selectbox("Selecione um Bairro (opcional)", bairros_disponiveis)
    combustivel_selecionado = st.selectbox("Selecione o Tipo de Combustível (opcional)", tipos_combustivel_disponiveis)

    # Função para filtrar os dados
    def filtrar_dados(dados_totais, bairro=None, combustivel=None):
        if bairro and bairro != 'Todos':
            dados_totais = dados_totais[dados_totais['BairroPosto'] == bairro]
        if combustivel and combustivel != 'Todos':
            dados_totais = dados_totais[dados_totais['TipoCombustivel'] == combustivel]
        
        return dados_totais

    # Função para encontrar o menor preço por combustível, posto e bairro
    def obter_menor_preco(dados_totais):
        # Agrupar por NomePosto, TipoCombustivel, BairroPosto e encontrar o menor ValorCombustivel
        dados_agrupados = dados_totais.groupby(['NomePosto', 'TipoCombustivel', 'BairroPosto']).agg({
            'ValorCombustivel': 'min',  # Menor preço por agrupamento
            'DataColeta': 'min',        # Data da coleta associada ao menor preço
            'RuaPosto': 'first'         # Manter a rua do posto
        }).reset_index()
        
        return dados_agrupados

    # Filtrar os dados com base nos parâmetros
    dados_filtrados = filtrar_dados(dados_totais, bairro=bairro_selecionado, combustivel=combustivel_selecionado)

    # Obter o menor preço de cada combustível por posto e bairro
    if not dados_filtrados.empty:
        menor_preco_df = obter_menor_preco(dados_filtrados)
        st.dataframe(menor_preco_df)
    else:
        st.write("Não há dados disponíveis para os parâmetros informados.")

with aba2:
    st.title("Preço Médio de Combustível")

    data_inicial = st.date_input("Data Inicial")
    data_final = st.date_input("Data Final")

    if st.button("Buscar preço"):
        # Chama a função com ou sem parâmetros
        df = listar_preco_medio(dados_totais, data_inicial if data_inicial else None, data_final if data_final else None)
    else:
        # Se não clicar, exibe todos os dados sem filtro
        df = listar_preco_medio(dados_totais)

    # Exibir dataframe
    st.dataframe(df, use_container_width = True)

    # Exibir gráfico se dados foram carregados
    if not df.empty:
        fig = px.bar(df, x='Posto', y='PrecoMedio', color='TipoCombustivel', title='Preço Médio por Posto')
        st.plotly_chart(fig)
with aba3:
    # Interface Streamlit
    st.title("Listagem de Preço Médio de Combustível")

    data_inicial = st.date_input("Data Inicial", key="data_inicial_lista")
    data_final = st.date_input("Data Final", key="data_final_lista")

    if st.button("Buscar", key="buscar_lista"):
        # Chama a função com ou sem parâmetros
        df = listagem_preco_medio(dados_tabela_posto, dados_tabela_combustivel, dados_tabela_coleta,data_inicial, data_final)
    else:
        # Se não clicar, exibe todos os dados sem filtro
        df = listagem_preco_medio(dados_tabela_posto, dados_tabela_combustivel, dados_tabela_coleta)

    # Exibir dataframe
    st.dataframe(df)

    # Exibir gráfico se dados foram carregados
    if not df.empty:
        fig = px.bar(df, x='Posto', y='PrecoMedio', color='TipoCombustivel', title='Preço Médio por Posto e Tipo de Combustível')
        st.plotly_chart(fig)
       
