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
dados_tabela_posto['Lat'] = None
dados_tabela_posto['Lon'] = None
# Atribuindo os valores para o posto específico
# Exemplo: Para o posto Ale Itaguaçu
dados_tabela_posto.loc[dados_tabela_posto['NomePosto'] == 'Ale', ['Lat', 'Lon']] = [-19.802004, -40.857304]
# Atribuindo os valores para o Posto Petrobras
dados_tabela_posto.loc[dados_tabela_posto['NomePosto'] == 'Petrobras', ['Lat', 'Lon']] = [-20.3671632, -40.3020814]
dados_tabela_posto.loc[dados_tabela_posto['NomePosto'] == 'Shell', ['Lat', 'Lon']] = [-20.3544455, -40.2990284]


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

# GASOLINA COMUM ##
# Filtrar os dados para gasolina comum
gasolina_comum = dados_totais[dados_totais['TipoCombustivel'] == 'Gasolina Comum']
# Converter 'DataColeta' para datetime se não estiver
gasolina_comum['DataColeta'] = pd.to_datetime(gasolina_comum['DataColeta'], format='%d-%m-%Y')
# Extrair ano e mês
gasolina_comum['AnoMes'] = gasolina_comum['DataColeta'].dt.to_period('M')
# Agrupar por ano e mês e calcular a média do valor
variacao_mensal = gasolina_comum.groupby('AnoMes')['ValorCombustivel'].mean().reset_index()
# Converter de Period para datetime para plotagem
variacao_mensal['AnoMes'] = variacao_mensal['AnoMes'].dt.to_timestamp()

# Criando o gráfico de barras
fig_cariacao_gasolina_comum = px.bar(
    variacao_mensal,
    x='AnoMes',
    y='ValorCombustivel',
    color='ValorCombustivel',  # A cor das barras será definida pela variação do valor
    color_continuous_scale='Viridis',  # Escala de cores contínua
    labels={'AnoMes': 'Mês e Ano', 'ValorCombustivel': 'Preço Médio da Gasolina Comum (R$)'},
    title='Variação do Preço Médio da Gasolina Comum ao Longo do Tempo'
)

# Personalizando o gráfico (opcional)
fig_cariacao_gasolina_comum .update_layout(
    xaxis_title_text='Mês e Ano',
    yaxis_title_text='Preço Médio (R$)',
    xaxis_tickangle=-45  # Rotacionar os rótulos do eixo x para melhor visualização
)
# Mapa de calor (assumindo que você tem dados geográficos mais detalhados)
fig_mapa_calor = px.density_mapbox(dados_totais, 
                                   lat='Lat', 
                                   lon='Lon', 
                                   z='ValorCombustivel',
                       mapbox_style="carto-positron", 
                       center={"lat": -19, "lon": -40}, 
                       zoom=10)

# FIG preco por posto
fig_bar_preço_posto = px.bar(dados_totais, 
             x='NomePosto',
             y='ValorCombustivel',
             title="Preço por posto",
             color='ValorCombustivel', 
             color_continuous_scale='Viridis')  
fig_bar_preço_posto.update_layout(yaxis=dict(range=[6, 20]))

#calculando preco medio
preco_medio = dados_totais['ValorCombustivel'].mean()

# Adicionar uma nova coluna com o preço médio
dados_totais['PrecoMedio'] = preco_medio

#preco medio  geral
fig_preco_medio_geral = px.bar(dados_totais , 
    x='TipoCombustivel', 
    y='PrecoMedio',  
    title="Preço Médio por Bairro",
    color='TipoCombustivel',
    color_continuous_scale='Viridis')
fig_preco_medio_geral .update_layout(yaxis=dict(range=[0, 10]))



coluna1,coluna2 = st.columns(2)
with coluna1:
    # Criar gráfico de variação mensal da gasolina comum
    fig_variacao_gasolina = px.line(variacao_mensal, 
                                    x='AnoMes', 
                                    y='ValorCombustivel',
                                    title='Variação Mensal da Gasolina Comum',
                                    labels={'AnoMes': 'Mês/Ano', 'ValorCombustivel': 'Preço Médio (R$)'},
                                    markers=True)
    #Valor Minimo por combustivel
    fig_valor_minimo = px.bar(dados_totais, 
                            x='NomePosto', 
                            y='ValorCombustivel', 
                            color='TipoCombustivel', 
                            color_continuous_scale='Viridis',
                            title="Menor Preço de Cada Combustível")
    
    st.plotly_chart(fig_variacao_gasolina, use_container_width = True)
    st.plotly_chart(fig_valor_minimo, use_container_width = True)
    st.plotly_chart(fig_bar_preço_posto, use_container_width = True)
with coluna2:
   
    st.write("Gráfico Interativo de Preços por Tipo de Combustível")
    tipo_combustivel_especifico = 'Gasolina Comum'
    dados_filtrados = dados_totais[dados_totais['TipoCombustivel'] == tipo_combustivel_especifico ]
    # Cria um gráfico de dispersão usando Plotly
    fig = px.scatter(dados_totais, 
                    x='DataColeta', 
                    y='ValorCombustivel', 
                    color='TipoCombustivel',
                    title='Preço do Combustível ao Longo do Tempo',
                    size='ValorCombustivel', hover_data=['TipoCombustivel'])
    st.plotly_chart(fig_cariacao_gasolina_comum , use_container_width = True)
    st.plotly_chart(fig)
    st.plotly_chart(fig_preco_medio_geral)






