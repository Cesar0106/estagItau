import streamlit as st
import pandas as pd
import plotly.express as px

# Function to load and process the data
def process_data(file):
    df = pd.read_excel(file)
    df['Spread ponderado'] = df['Spread de compra (%)'] * df['Peso no índice (%)']
    df['Spread médio ponderado'] = df.groupby(['Data', 'Segmento'])['Spread ponderado'].transform('sum') / df.groupby(['Data', 'Segmento'])['Peso no índice (%)'].transform('sum')
    return df

# Upload the dataset
st.header("Carregar o conjunto de dados")
data_file = st.file_uploader("Carregue o arquivo .xlsx com o IDEX aqui", type=['xlsx'])

if data_file is not None:
    df = process_data(data_file)
    
    st.header("Escolha o gráfico")
    graph_options = ["Evolução dos Spreads Médios Ponderados", "Peso por Segmento"]
    selected_graph = st.selectbox("Selecione um gráfico", graph_options)

    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Selecione o intervalo de datas")
        start_date = st.date_input("Data inicial", df['Data'].min())
        end_date = st.date_input("Data final", df['Data'].max())
        if start_date > end_date:
            st.error('Erro: A data final deve ser depois da data inicial.')

        # Filter the data by date
        df = df[(df['Data'] >= pd.to_datetime(start_date)) & (df['Data'] <= pd.to_datetime(end_date))]

    with col2:
        st.header("Selecione os segmentos")
        segments = st.multiselect("Escolha os segmentos", df['Segmento'].unique())

    # If any segment is selected, filter the data by segment
    if segments:
        df = df[df['Segmento'].isin(segments)]

    if selected_graph == "Evolução dos Spreads Médios Ponderados":
        fig = px.line(df, x='Data', y='Spread médio ponderado', color='Segmento')
        st.plotly_chart(fig)
    elif selected_graph == "Peso por Segmento":
        weights = df.groupby('Segmento')['Peso no índice (%)'].sum()
        fig = px.pie(values=weights, names=weights.index)
        st.plotly_chart(fig)
