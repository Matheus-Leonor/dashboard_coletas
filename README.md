# Dashboard de Coleta de Preços de Combustíveis

Este projeto consiste em um **Dashboard Interativo de Coleta de Preços de Combustíveis**, desenvolvido utilizando **Streamlit, Pandas** e **Plotly**. A aplicação permite a visualização e análise de dados de preços de combustíveis coletados em diferentes postos, abrangendo o período de **01 de dezembro de 2023 a 01 de setembro de 2024**.

## 🛠 Tecnologias Utilizadas
- **Python**: Linguagem principal para manipulação de dados e desenvolvimento do dashboard.
- **Streamlit**: Framework para a construção da interface web do dashboard.
- **Pandas**: Biblioteca para tratamento e análise dos dados.
- **Plotly**: Utilizado para visualização gráfica dos dados.

## 📊 Funcionalidades

O dashboard oferece as seguintes funcionalidades:

1. **Visualização do Menor Preço por Bairro e Tipo de Combustível:**
   - O usuário pode selecionar o bairro e o tipo de combustível para visualizar o menor valor disponível em cada posto.

2. **Cálculo do Preço Médio por Posto e Combustível:**
   - Filtragem por datas e bairros para exibir o preço médio de cada combustível em diversos postos.

3. **Listagem de Preço Médio com Amostras:**
   - Apresenta o número de coletas realizadas em cada posto, assim como o preço médio dos combustíveis.

## 🗃 Estrutura de Dados

Os dados são armazenados em três tabelas principais:

- **Tabela de Postos**: Informações dos postos de combustível.
- **Tabela de Combustíveis**: Tipos de combustíveis disponíveis.
- **Tabela de Coletas**: Preços coletados ao longo do período.

Essas tabelas foram unidas utilizando **Pandas** para gerar um DataFrame completo com todas as informações necessárias para as análises.

## 💡 Processo de Desenvolvimento

Inicialmente, o projeto utilizava a biblioteca **pyodbc** para conectar-se ao banco de dados SQL Server e executar procedures diretamente do SQL. No entanto, para maior flexibilidade e otimização do processo, os dados foram exportados para **arquivos CSV**, e o tratamento e filtragem dos dados passaram a ser feitos diretamente no Python, utilizando Pandas.

### Fluxo de Trabalho:
1. **Coleta de Dados**: Os dados de preços foram coletados em diferentes datas e armazenados em arquivos CSV.
2. **Tratamento dos Dados**: Utilizando Pandas, realizamos a limpeza e integração das tabelas de postos, combustíveis e coletas.
3. **Visualização no Dashboard**: A interface construída com Streamlit permite a interação do usuário com os dados, filtrando por tipo de combustível, bairro e período de tempo.

## 🚀 Visualize o projeto: https://dashboardcoletas-hwv2b8zxdennnrkytndbng.streamlit.app/
