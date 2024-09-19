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

#  DADOS TOTAIS
# Unir as tabelas coleta e posto pela chave FkPosto = IdPosto
df_merged1 = pd.merge(dados_tabela_coleta, dados_tabela_posto, left_on='FkPosto', right_on='IdPosto')
# Em seguida, unir com a tabela de combustivel pela chave FkCombustivel = IdCombustivel
# Usar groupby para contar as amostras por NomePosto e TipoCombustivel

dados_totais = pd.merge(df_merged1, dados_tabela_combustivel,  left_on='FkCombustivel', right_on='IdCombustivel')
# Converter a coluna para tipo numérico (float), forçando erros a serem transformados em NaN
# Substituir as vírgulas por pontos na coluna 'ValorCombustivel'
dados_totais['ValorCombustivel'] = dados_totais['ValorCombustivel'].str.replace(',', '.')
# Converter a coluna 'ValorCombustivel' para numérico (float)
dados_totais['ValorCombustivel'] = pd.to_numeric(dados_totais['ValorCombustivel'], errors='coerce')
dados_totais['DataColeta'] = pd.to_datetime(dados_totais['DataColeta'])
# Extrair apenas dia, mês e ano no formato desejado
dados_totais['DataColeta'] = dados_totais['DataColeta'].dt.strftime('%d-%m-%Y')


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
    # Seleção de parâmetros opcionais
    bairros_disponiveis = ['Todos'] + list(dados_totais['BairroPosto'].unique())
    tipos_combustivel_disponiveis = ['Todos'] + list(dados_totais['TipoCombustivel'].unique())

    bairro_selecionado = st.selectbox("Selecione um Bairro (opcional)", bairros_disponiveis, key="aba2_bairro_slect")
    combustivel_selecionado = st.selectbox("Selecione o Tipo de Combustível (opcional)", tipos_combustivel_disponiveis, key="aba2_combustivel_select")
    data_inicial = st.date_input("Data inicial (opcional)", None)
    data_final = st.date_input("Data final (opcional)", None)
   

    # Função para filtrar os dados
    def filtrar_dados(dados_totais, bairro=None, combustivel=None, data_inicial=None, data_final=None):
        if bairro and bairro != 'Todos':
            dados_totais = dados_totais[dados_totais['BairroPosto'] == bairro]
        if combustivel and combustivel != 'Todos':
            dados_totais = dados_totais[dados_totais['TipoCombustivel'] == combustivel]
        if data_inicial:
            dados_totais['DataColeta'] = pd.to_datetime(dados_totais['DataColeta'], format='%d-%m-%Y')
            dados_totais = dados_totais[dados_totais['DataColeta'] >= pd.to_datetime(data_inicial)]
        if data_final:
            dados_totais = dados_totais[dados_totais['DataColeta'] <= pd.to_datetime(data_final)]
        
        return dados_totais

    # Função para calcular o preço médio por combustível e posto
    def calcular_preco_medio_por_postos(dados_totais):
        # Agrupar por NomePosto e TipoCombustivel e calcular o preço médio
        dados_agrupados = dados_totais.groupby(['NomePosto', 'TipoCombustivel','BairroPosto','RuaPosto']).agg(
            PrecoMedio=('ValorCombustivel', 'mean')
        ).reset_index()

        return dados_agrupados

    # Filtrar os dados com base nos parâmetros
    dados_filtrados = filtrar_dados(dados_totais, bairro=bairro_selecionado, combustivel=combustivel_selecionado, data_inicial=data_inicial, data_final=data_final)

    # Verificar se há dados filtrados
    if not dados_filtrados.empty:
        # Calcular o preço médio por combustível e posto
        preco_medio_df = calcular_preco_medio_por_postos(dados_filtrados)
        
        # Mesclar a tabela de menor preço com a de preço médio (opcional, se quiser exibir ambos)
        menor_preco_df = obter_menor_preco(dados_filtrados)
        

            # Exibir a tabela com preço médio por combustível e posto
        st.write("Tabela com Preço Médio de cada Combustível por Posto:")
        st.dataframe(preco_medio_df)
    else:
        
        st.write("Não há dados disponíveis para os parâmetros informados.")
   
with aba3:
     # Seleção de parâmetros opcionais
    data_inicial = st.date_input("Data inicial", None,key='aba3_data_inicial')
    data_final = st.date_input("Data final", None,key='aba3_data_final')
   

    # Função para filtrar os dados
    def filtrar_dados(dados_totais, data_inicial=None, data_final=None):
        if data_inicial:
            dados_totais['DataColeta'] = pd.to_datetime(dados_totais['DataColeta'], format='%Y-%m-%d')
            dados_totais = dados_totais[dados_totais['DataColeta'] >= pd.to_datetime(data_inicial)]
        if data_final:
            dados_totais = dados_totais[dados_totais['DataColeta'] <= pd.to_datetime(data_final)]
        
        return dados_totais

    # Função para calcular o preço médio por combustível e posto
    def calcular_preco_medio_por_postos(dados_totais):
        # Agrupar por NomePosto e TipoCombustivel e calcular o preço médio
        dados_agrupados = dados_totais.groupby(['NomePosto','BairroPosto']).agg(
            QuantidadeAmostras=('IdColeta', 'count'),
            PrecoMedio=('ValorCombustivel', 'mean')
        ).reset_index()

        return dados_agrupados


    # Filtrar os dados com base nos parâmetros
    dados_filtrados = filtrar_dados(dados_totais,data_inicial=data_inicial, data_final=data_final)

    # Verificar se há dados filtrados
    if not dados_filtrados.empty:
        # Calcular o preço médio por combustível e posto
        preco_medio_df = calcular_preco_medio_por_postos(dados_filtrados)
            # Exibir a tabela com preço médio por combustível e posto
        st.write("Tabela com Preço Médio de cada Combustível por Posto:")
        st.dataframe(preco_medio_df)

    else:
        
        st.write("Não há dados disponíveis para os parâmetros informados.")
       
