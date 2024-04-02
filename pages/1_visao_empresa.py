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

st.set_page_config(page_title='Visão Empresa', page_icon='📊', layout='wide')

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
def order_metric(df):
    """ Esta função tem a responsabilidade gerar um Gráfico Colunas de pedidos por dia 

        1. Selecionar colunas para o dataset de interesse
        2. Selecionar todas as linhas e agrupar pela Data do Pedido
        3. Countar o número de pedidos em cada data
        4. Criar um gráfico de barras com o Número de Pedidos pela Data do Pedido

        Input: Dataframe
        Output: Gráfico de barras
    """
    cols = ['ID', 'Order_Date']
    df_aux = (df.loc[:, cols].groupby('Order_Date')
                             .count()
                             .reset_index())
    fig = px.bar(df_aux, x='Order_Date', y="ID")
    return fig

def traffic_order_share( df ):
    """ Esta função tem a responsabilidade gerar um Gráfico de pizza de distribuição de pedidos por tráfego
    
        1. Selecionar todas as linhas das colunas de interesse
        2. Agrupar por Tipos de Densidade de Tráfego
        3. Contar o número de pedidos realizados em cada situação de densidade de tráfego
        4. Dividir o número de entregas realizadas em cada tipo de densidade de tráfego pela soma total de Pedidos realizados (em todas as condições)
        5. Gerar um gráfico de pizza com a porcentagem de pedidos realizados por tipo de tráfego
        
        Input: Dataframe
        Output: Gráfico de Pizza
    """

    df_aux = (df.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density')
                                                      .count()
                                                      .reset_index())
    df_aux['Entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux, values='Entregas_perc', names='Road_traffic_density')

    return fig

def traffic_order_city( df ):
    """ Esta função tem a responsabilidade gerar um Gráfico de distribuição de pedidos por Cidade e Tráfego
    
        1. Seleciona todas as linhas e as colunas de interesse
        2. Agrupa os dados conforme a cidade e a Densidade de Tráfego
        3. Conta o número o número de entrega em cada um desses grupos
        4. Plota um gráfico de dispersão de bolha conforme o tipo de tráfego e cidade
        
        Input: Dataframe
        Output: Gráfico de Dispersão
    """

    df_aux = (df.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density'])
                                                               .count()
                                                               .reset_index())
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

def order_by_week( df ):
    """ Esta função tem a responsabilidade gerar um Gráfico de linhas da distribuição de pedidos ao longo das semanas
    
        1. Criar uma coluna nova no dataframe chamda 'Week_of_Year', a qual agrupa os dias em semanas
        2. seleciona as linhas e colunas de interesse
        3. Agrupa conforme as semanas
        4. Conta o número de entrega feitas em cada semana
        5. Desenha um gráfico de linhas com o número de pedidos realizado em cada semana do ano
        
        Input: Dataframe
        Output: Gráfico de Linhas
    """
    df['Week_of_Year'] = df['Order_Date'].dt.strftime('%U')
    df_aux = (df.loc[:, ['ID', 'Week_of_Year']].groupby('Week_of_Year')
                                              .count()
                                              .reset_index())
    fig = px.line(df_aux, x='Week_of_Year', y='ID')
    return fig

def avg_order_person_week ( df ):
    """ Esta função tem a responsabilidade gerar um Gráfico de linhas da distribuição do número de pedidos por entregador ao longo das semanas do ano
    
        1. Cria um dataset auxiliar com todas as linhas e as colunas de interesse
        2. Agrupa os dados conforme a semanas
        3. Conta o  número de pedidos realizados em cada semana
        4. Cria um segundo dataset auxiliar com as linhas e as colunas de interesse
        5. Agrupa conforme as semanas
        6. Conta o número de entregadores pelo ID único
        7. Acopla os dois datasets criados, criando um dataset auxliar único
        8. Cria-se uma nova coluna, que calcula o número de pedidos dividio pelo número de entregadores únicos
        9. Desenha um gráfico de linhas
        
        Input: Dataframe
        Output: Gráfico de Linhas
    """

    df_aux01 = (df.loc[:, ['ID', 'Week_of_Year']].groupby(['Week_of_Year'])
                                                .count()
                                                .reset_index())
    df_aux02 = (df.loc[:, ['Week_of_Year', 'Delivery_person_ID']].groupby(['Week_of_Year'])
                                                                .nunique()
                                                                .reset_index())
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['Order_by_DeliveryPerson'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='Week_of_Year', y='Order_by_DeliveryPerson')
    return fig

def country_map( df ):    
    """ Esta função tem a responsabilidade gerar um mapa com a localização central dos tipos de tráfego nas diferentes cidades 
    
        1. Seleciona as linhas e colunas de interesse
        2. Agrupa por cidade e tipo de densidade de trânsito
        3. Calcula a média da longitude e longitude dos pontos de entregas, para cada agrupamento
        4. Cria um mapa
        5. Localiza e plota no mata as informações de Latitude e Longitude de acordo com as categorias
        6. Gera um mapa em comprimento e largura desejadas
        
        Input: Dataframe
        Output: Mapa
    """
    df = (df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_longitude', 'Delivery_location_latitude']].groupby(['City', 'Road_traffic_density'])
                                                                                                                  .median()
                                                                                                                  .reset_index())
    map = folium.Map()
    for index, location_info in df.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                       popup=location_info[['City', 'Road_traffic_density']] ).add_to(map)
    folium_static( map, width=1024, height=600 )
    return None
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
#===================== Visão Empresa ======================
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
    'Até qual data?',
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
linhas_selecionadas = df['Road_traffic_density'].isin( traffic_options)
df = df.loc[linhas_selecionadas,  :]

#==========================================================
#=================== Layout no Streamlit ==================
#==========================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica', ])

#------------------------------------Tab 1----------------------------------------------
with tab1:
    with st.container():
        st.header('Orders by Day')
        fig = order_metric( df )
        st.plotly_chart( fig , use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.header('Order by Traffic')
            fig = traffic_order_share( df )
            st.plotly_chart(fig, use_container_width=True)

        with col2: 
            st.header('Order by City and Traffic')
            fig = traffic_order_city( df )
            st.plotly_chart(fig, use_container_width=True)

#---------------------------------------Tab 2------------------------------------------
with tab2:
    with st.container():
        st.header("Orders by Week")
        fig = order_by_week( df )
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.header("Average Orders per Delivery Person Over the Year")
        fig = avg_order_person_week( df )
        st.plotly_chart( fig, use_container_width=True)

#---------------------------------------Tab 3------------------------------------------
with tab3:
    st.header("Country Map")
    country_map(df)

#------------------------------------------------------------------------ Fim da estrutura lógica do código ------------------------------------------------------------------------
