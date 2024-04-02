#Importar bibliotecas

import pandas as pd
from haversine import haversine
import plotly.express as px 
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
import numpy as np
import plotly.graph_objects as go


st.set_page_config(page_title='Visão Entregadores', page_icon='🚚', layout='wide')
#==========================================================
# Funções
#==========================================================

#--------------------------------Início da função de Limpeza-----------------------------
def clean_code(df):
    """Esta função tem a responsabilidade de limpar o dataframe
    
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Formatação da coluna de data
        4. Remoção dos espaços das variáveis
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )

        Input: Dataframe
        Output: Dataframe        
    """

    #1. Limpando os NaN
    
    linhas_selecionadas = (df['Delivery_person_Age'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()

    df = df.loc[(df['multiple_deliveries']  != 'NaN '), :].copy()
    df = df.loc[(df['Road_traffic_density'] != 'NaN ')]
    df = df.loc[df['Road_traffic_density']  != 'NaN ']
    df = df.loc[(df['City']                 != 'NaN ')]
    df = df.loc[df['City']                  != 'NaN ']
    df = df.loc[(df['Festival']             != 'NaN ')]
    df = df.loc[df['Festival']              != 'NaN ']
    df = df.loc[df['City']                  != 'NaN ', :]
    df = df.loc[df['Road_traffic_density']  != 'NaN ', :]

    #2. Mudando os tipos das colunas

    df['Delivery_person_Age']     = df['Delivery_person_Age']    .astype(int)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    df['multiple_deliveries']     = df['multiple_deliveries']    .astype(int)

    #3. Formatação da coluna de data

    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format = '%d-%m-%Y' )

    #4.Limpando os espaços depois das strings:

    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_order']        = df.loc[:, 'Type_of_order']       .str.strip()
    df.loc[:, 'Type_of_vehicle']      = df.loc[:, 'Type_of_vehicle']     .str.strip()
    df.loc[:, 'City']                 = df.loc[:, 'City']                .str.strip()
    df.loc[:, 'Festival']             = df.loc[:, 'Festival']            .str.strip()
    df.loc[:, 'ID']                   = df.loc[:, 'ID']                  .str.strip()


    # 5. Limpando a coluna de time taken

    df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    return df
#----------------------------------Fim da função de Limpeza-------------------------------

#----------------------------------Início função de Gráficos------------------------------
def top_delivers(df, top_asc):
    cols = ['Time_taken(min)', 'Delivery_person_ID', 'City']
    df_aux = df.loc[:, cols].groupby(['City', 'Delivery_person_ID']).mean()
    df_aux = df_aux.sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index()
    df_aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    df_aux03 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)
    df_aux = pd.concat( [df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return df_aux 



#------------------------------------Fim função de Gráficos--------------------------------

#------------------------------------------------------------------------ Início da estrutura lógica do código ------------------------------------------------------------------------

#==========================================================
# ==================== Importar dataset ===================
#==========================================================

#Importar dataset

df_raw = pd.read_csv('train.csv')

#==========================================================
# =================== Limpeza dos dados ===================
#==========================================================

df = clean_code( df_raw )

#==========================================================
#=================== Visão Entregadores ===================
#==========================================================

#==========================================================
#=============== Barra Lateral no Streamlit ===============
#==========================================================
st.header('Marketplace - Visão Cliente')

#image_path = 'E:\\Priscila\\repos\\ftc_programacao_python\\ciclo_05\\imagem_logo.png'
image = Image.open('imagem_logo.png' )
st.sidebar.image( image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Faster Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('# Selecione uma data limite:')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime( 2022, 4, 13 ),
    min_value=datetime( 2022, 2, 11) ,
    max_value=datetime( 2022, 4, 6 ),
    format='DD-MM-YYYY' )

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default='Low' )

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Priscila Portela')
### Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas,  :]
### filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin( traffic_options )
df = df.loc[linhas_selecionadas,  :]

#==========================================================
#=================== Layout no Streamlit ==================
#==========================================================

tab1, tab2, tab3 = st.tabs( ['Visão Geral', '_', '_'] )

#------------------------------------Tab 1----------------------------------------------
with tab1:
    with st.container():
        st.title('Overall Metrics')

    col1, col2, col3, col4 = st.columns(4, gap='large')
    with col1:
        #Maior idade dos entrgadores
        maior_idade = df.loc[:, 'Delivery_person_Age'].max()
        col1.metric('Maior idade', maior_idade)

    with col2:
        #Menor idade dos entrgadores
        menor_idade = df.loc[:, 'Delivery_person_Age'].min()
        col2.metric('Menor idade', menor_idade)

    with col3:
        #Melhor condiçãoo de veículos
        melhor_condicao = df.loc[:, 'Vehicle_condition'].max()
        col3.metric('Melhor condição de veículo', melhor_condicao)


    with col4:
        #Pior condição de veículos
        pior_condicao = df.loc[:, 'Vehicle_condition'].min()
        col4.metric('Pior condição de veículo', pior_condicao)
    
    with st.container():
        st.markdown('---')
        st.title('Avaliações')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliações médias por Entregador')
            avg_rating_id = ( df.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                            .groupby('Delivery_person_ID')
                            .mean()
                            .reset_index() )
            st.dataframe(avg_rating_id)
        
        with col2:
            st.markdown('##### Avaliação média por transito')
            df_avg_std_traffic = ( df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                        .groupby('Road_traffic_density')
                                        .agg({'Delivery_person_Ratings': ['mean', 'std']}) )
            df_avg_std_traffic.columns = ['delivery_mean', 'delivery_std']
            df_avg_std_traffic = df_avg_std_traffic.reset_index()
            st.dataframe(df_avg_std_traffic)

            st.markdown( '##### Avaliação média por clima')
            cols = ['Delivery_person_Ratings', 'Weatherconditions']
            df_avg_std_weather = (df.loc[:, cols].groupby('Weatherconditions')
                                                .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            df_avg_std_weather.columns = ['Weather_mean', 'Weather_std']
            df_avg_std_weather = df_avg_std_weather.reset_index()
            st.dataframe(df_avg_std_weather)

    with st.container():
        st.markdown('---')
        st.title('Velocidade de entrga')

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Top entregadores mais rápidos')

            df_aux = top_delivers(df, top_asc=True)
            st.dataframe(df_aux)

        with col2:
            st.markdown('##### Top entregadores mais lentos')
           
            df_aux = top_delivers(df, top_asc=False)
            st.dataframe(df_aux)