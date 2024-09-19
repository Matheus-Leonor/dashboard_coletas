import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout= 'wide')

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
dados_totais = pd.merge(df_merged1, dados_tabela_combustivel,  left_on='FkCombustivel', right_on='IdCombustivel')
# Substituir as vírgulas por pontos na coluna 'ValorCombustivel'
dados_totais['ValorCombustivel'] = dados_totais['ValorCombustivel'].str.replace(',', '.')
# Converter a coluna 'ValorCombustivel' para numérico (float)
dados_totais['ValorCombustivel'] = pd.to_numeric(dados_totais['ValorCombustivel'], errors='coerce')
dados_totais['DataColeta'] = pd.to_datetime(dados_totais['DataColeta'])
# Extrair apenas dia, mês e ano no formato desejado
dados_totais['DataColeta'] = dados_totais['DataColeta'].dt.strftime('%d-%m-%Y')



# Exemplo de gráfico usando Plotly
st.write("Gráfico Interativo de Preços por Tipo de Combustível")
tipo_combustivel_especifico = 'Gasolina Comum'
dados_filtrados = dados_totais[dados_totais['TipoCombustivel'] == tipo_combustivel_especifico ]
# Cria um gráfico de dispersão usando Plotly
fig = px.scatter(dados_totais, 
                 x='DataColeta', 
                 y='ValorCombustivel', 
                 color='TipoCombustivel',
                 title='Preço do Combustível ao Longo do Tempo')
st.plotly_chart(fig)

# Valor  da gasolina  comum
fig_bar = px.bar(dados_totais, 
             x='NomePosto',
             y='ValorCombustivel',
             color='ValorCombustivel', 
             color_continuous_scale='Viridis')  
fig_bar.update_layout(yaxis=dict(range=[6, 20]))
st.plotly_chart(fig_bar)
#Valor Minimo por combustivel
fig_valor_minimo = px.bar(dados_totais, 
                          x='NomePosto', 
                          y='ValorCombustivel', 
                          color='TipoCombustivel', 
                          color_continuous_scale='Viridis',
                          title="Menor Preço de Cada Combustível")
st.plotly_chart(fig_valor_minimo)


#calculando preco medio
preco_medio = dados_totais['ValorCombustivel'].mean()

# Adicionar uma nova coluna com o preço médio
dados_totais['PrecoMedio'] = preco_medio

#preco medio  geral
fig_preco_medio_geral = px.bar(dados_totais , 
    x='NomePosto', 
    y='PrecoMedio',  
    title="Preço Médio por Bairro")
st.plotly_chart(fig_preco_medio_geral)


fig_scatter  =  px . scatter ( dados_totais ,  
                              y = "NomePosto" ,  
                              x = "ValorCombustivel" ,  
                              color = "TipoCombustivel" ,  
                              symbol = "TipoCombustivel" ) 
fig . update_traces (marker_size=10 ) 
st.plotly_chart(fig_scatter)
