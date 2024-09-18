import pyodbc
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
def carregar_dados():
    conexao = conectar_bd()
    consulta_sql = """
    SELECT *
    FROM Tabela_Coleta

    """
    dados = pd.read_sql(consulta_sql, conexao)
    conexao.close()
    return dados

dados_coleta = carregar_dados()

def carregar_dados2():
    conexao = conectar_bd()
    consulta_sql = """
    SELECT
        IdColeta,
        NomePosto,
        CidadePosto,
        BairroPosto,
        RuaPosto,
        NumeroPosto,
        TipoCombustivel,
        DataColeta,
        ValorCombustivel,
	    COUNT(*) OVER (PARTITION BY NomePosto, TipoCombustivel) AS QuantidadeAmostras
    FROM 
        Tabela_Coleta
    INNER JOIN
        Tabela_Posto ON FkPosto = IdPosto
    INNER JOIN
        Tabela_Combustivel ON FkCombustivel = IdCombustivel

    """
    dados = pd.read_sql(consulta_sql, conexao)
    conexao.close()
    return dados

dados_totais = carregar_dados2()

# Agrupar por TipoCombustivel e DataColeta e calcular o preço médio
df_agrupado = dados_totais.groupby(['TipoCombustivel', 'DataColeta'])['ValorCombustivel'].min().reset_index()
#Procedure valor minimo por: 
def get_data(bairro, tipo_combustivel):
    conn_str = (
         'DRIVER={ODBC Driver 17 for SQL Server};'
         'SERVER=DESKTOP-SUCSSF7\SQLEXPRESS;'
         'DATABASE=AOP_Banco_de_dados;'
         'Trusted_Connection=yes;'
    )

    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute("EXEC ValorMinimoCombustivel @BairroPosto=?, @TipoCombustivel=?", bairro, tipo_combustivel)
        rows = cursor.fetchall()
        df = pd.DataFrame.from_records(rows, columns=[desc[0] for desc in cursor.description])
    return df

#Procedure preço medio
def get_preco_medio(data_inicial=None, data_final=None):
    conexao = conectar_bd()
    cursor = conexao.cursor()

    # Montando a consulta SQL com base nos parâmetros fornecidos
    if data_inicial and data_final:  # Se ambos os parâmetros forem fornecidos
        query = """
        EXEC PrecoMedio @DataInicial=?, @DataFinal=?
        """
        cursor.execute(query, (data_inicial, data_final))
    elif data_inicial:  # Se apenas o parâmetro data_inicial for fornecido
        query = """
        EXEC PrecoMedio @DataInicial=?, @DataFinal=NULL
        """
        cursor.execute(query, (data_inicial,))
    elif data_final:  # Se apenas o parâmetro data_final for fornecido
        query = """
        EXEC PrecoMedio @DataInicial=NULL, @DataFinal=?
        """
        cursor.execute(query, (data_final,))
    else:  # Se nenhum parâmetro for fornecido
        query = """
        EXEC PrecoMedio @DataInicial=NULL, @DataFinal=NULL
        """
        cursor.execute(query)
    
    # Fetching the results and creating a DataFrame
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame.from_records(rows, columns=columns)
    
    conexao.close()
    return df

# Função para carregar dados com filtros opcionais
def get_listagem_preco_medio(data_inicial=None, data_final=None):
    conexao = conectar_bd()
    cursor = conexao.cursor()

    # Montando a consulta SQL com base nos parâmetros fornecidos
    if data_inicial and data_final:  # Se ambos os parâmetros forem fornecidos
        query = """
        EXEC ListagemPrecoMedio @DataInicial=?, @DataFinal=?
        """
        cursor.execute(query, (data_inicial, data_final))
    else:  # Se os parâmetros não forem fornecidos
        query = """
        EXEC ListagemPrecoMedio @DataInicial=NULL, @DataFinal=NULL
        """
        cursor.execute(query)
    
    # Fetching the results and creating a DataFrame
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame.from_records(rows, columns=columns)
    
    conexao.close()
    return df

# Interface Streamlit       
aba1, aba2, aba3 = st.tabs(['Menor Valor de Combustível ', 'Preço Médio Geral',  'Listagem Preço Médio c/ Amostras'])

with aba1:
    #Interface procedure valor minimo
    st.title("Menor Valor de Combustível")
    bairro = st.text_input("Bairro")
    tipo_combustivel = st.text_input("Tipo de Combustível")
    if st.button("Buscar"):
        df = get_data(bairro, tipo_combustivel)
        fig = px.bar(df, x='Posto', y='ValorMinimo', color='TipoCombustivel', title='Menor Valor por Posto')
        st.dataframe(df)
        
    ## Gráfico de menor valor do combustivel por data e tipo:
    fig_variacao_combustivel = px.line(df_agrupado, 
                x = 'DataColeta',
                y = 'ValorCombustivel',
                markers = True, 
                range_y = (0,df_agrupado.max()), 
                color = 'TipoCombustivel', 
                line_dash = 'TipoCombustivel',
                title = 'Variação do valor')

    fig_variacao_combustivel.update_layout(yaxis_title='Variação combustivel')
    st.plotly_chart(fig_variacao_combustivel)
with aba2:
    st.title("Preço Médio de Combustível")

    data_inicial = st.date_input("Data Inicial")
    data_final = st.date_input("Data Final")

    if st.button("Buscar preço"):
        # Chama a função com ou sem parâmetros
        df = get_preco_medio(data_inicial if data_inicial else None, data_final if data_final else None)
    else:
        # Se não clicar, exibe todos os dados sem filtro
        df = get_preco_medio()

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
        df = get_listagem_preco_medio(data_inicial if data_inicial else None, data_final if data_final else None)
    else:
        # Se não clicar, exibe todos os dados sem filtro
        df = get_listagem_preco_medio()

    # Exibir dataframe
    st.dataframe(df)

    # Exibir gráfico se dados foram carregados
    if not df.empty:
        fig = px.bar(df, x='Posto', y='PrecoMedio', color='TipoCombustivel', title='Preço Médio por Posto e Tipo de Combustível')
        st.plotly_chart(fig)
       


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

#Preço Médio por combustivel
fig_preco_medio= px.bar(dados_totais, 
       x='NomePosto', 
       y='QuantidadeAmostras', 
       color='TipoCombustivel', 
       title="Quantidade de Amostras por Posto")
st.plotly_chart(fig_preco_medio)



fig_scatter  =  px . scatter ( dados_totais ,  
                              y = "NomePosto" ,  
                              x = "ValorCombustivel" ,  
                              color = "TipoCombustivel" ,  
                              symbol = "TipoCombustivel" ) 
fig . update_traces (marker_size=10 ) 
st.plotly_chart(fig_scatter)