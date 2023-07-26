import streamlit as st
import pandas as pd
import plotly.express as px


st.header("Carregar o conjunto de dados")
data_file = st.file_uploader("Carregue o arquivo .xlsx com o IDEX aqui", type=['xlsx'])

if data_file is not None:
    df = pd.read_excel(data_file)
    df['Spread ponderado'] = df['Spread de compra (%)'] * df['Peso no índice (%)']
    df['Spread médio ponderado'] = df.groupby(['Data', 'Segmento'])['Spread ponderado'].transform('sum') / df.groupby(['Data', 'Segmento'])['Peso no índice (%)'].transform('sum')
    
    st.header("Escolha o gráfico")
    graph_options = ["Evolução dos Spreads Médios Ponderados", "Peso por Segmento", "Duration Média Ponderada", "Peso por Segmento ao Longo do Tempo"]

    selected_graph = st.radio("Selecione um gráfico", graph_options)

    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Intervalo de datas")
        start_date = st.date_input("Data inicial", df['Data'].min())
        end_date = st.date_input("Data final", df['Data'].max())
        if start_date > end_date:
            st.error('Erro: A data final deve ser depois da data inicial.')

        df = df[(df['Data'] >= pd.to_datetime(start_date)) & (df['Data'] <= pd.to_datetime(end_date))]

    if selected_graph == "Evolução dos Spreads Médios Ponderados":
        with col2:
            st.header("Segmentos")
            segments = st.multiselect("Escolha os segmentos", df['Segmento'].unique())

            remove_outliers = st.radio("Remover outliers?", ['Sim', 'Não'])
            if remove_outliers == 'Sim':
                outlier_threshold = st.number_input("Digite o valor acima do qual um ponto é considerado um outlier", value=70.0, step=0.1)
                df = df[df['Spread médio ponderado'] < outlier_threshold / 100] 

        df['Spread médio ponderado'] *= 100 
        if segments:
            df = df[df['Segmento'].isin(segments)]
            fig = px.line(df, x='Data', y='Spread médio ponderado', color='Segmento')
            fig.update_layout(title='Evolução dos Spreads Médios Ponderados', yaxis_title='Spread Médio Ponderado (%)')
            st.plotly_chart(fig)
        else:
            fig = px.line(df, x='Data', y='Spread médio ponderado')
            fig.update_layout(title='Evolução dos Spreads Médios Ponderados', yaxis_title='Spread Médio Ponderado (%)')
            st.plotly_chart(fig)
    elif selected_graph == "Peso por Segmento":
        weights = df.groupby('Segmento')['Peso no índice (%)'].sum()
        fig = px.pie(values=weights, names=weights.index)
        st.plotly_chart(fig)
    elif selected_graph == "Duration Média Ponderada":
        df['Duration ponderada'] = df['Duration'] * df['Peso no índice (%)']
        df['Duration média ponderada'] = df.groupby(['Data', 'Segmento'])['Duration ponderada'].transform('sum') / df.groupby(['Data', 'Segmento'])['Peso no índice (%)'].transform('sum')
        with col2:
            st.header("Selecione os segmentos")
            segments = st.multiselect("Escolha os segmentos", df['Segmento'].unique())
        if segments:
            df = df[df['Segmento'].isin(segments)]
            fig = px.line(df, x='Data', y='Duration média ponderada', color='Segmento')
            st.plotly_chart(fig)
        else:
            fig = px.line(df, x='Data', y='Duration média ponderada')
            st.plotly_chart(fig)
    elif selected_graph == "Peso por Segmento ao Longo do Tempo":
        df_grouped = df.groupby(['Data', 'Segmento'])['Peso no índice (%)'].sum().reset_index()
        fig = px.bar(df_grouped, x='Data', y='Peso no índice (%)', color='Segmento', title='Evolução do Peso por Segmento ao Longo do Tempo')
        fig.update_layout(yaxis_title='Peso no Índice (%)')
        st.plotly_chart(fig)

    col3, col4 = st.columns(2)

    with col3:
        st.header("Empresas com maior peso Médio")
        df_grouped = df.groupby('Emissor')['Peso no índice (%)'].mean().reset_index()
        top_emitters = df_grouped.nlargest(10, 'Peso no índice (%)')
        st.dataframe(top_emitters)

    with col4:
        st.header("Frequência de Segmentos")
        segment_freq = df['Segmento'].value_counts()
        segment_freq.columns = ['Segmento', 'Frequência']
        st.dataframe(segment_freq)