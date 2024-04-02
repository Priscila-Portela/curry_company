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


st.set_page_config(page_title='Visão Restaurante', page_icon='🍴', layout='wide')
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

def distance(df):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df_aux = df.loc[:, cols]
    df_aux['Distance'] = (df.loc[:, cols].apply( lambda x: 
                                               haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                          (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
    avg_distance = np.round(df_aux['Distance'].mean(), 2)
    return avg_distance
            
def avg_std_time_delivery(df, op, col_number, number_title, festival):
    """"
    Esta função calcula o tempo médio e o desvio padrão do tempo de enterega. 
    Parâmetros:
        Input:
            - df: Dataframe com os dados necesssários para o cálculo
            - op: Tipo de operação que precisa ser calculado
                'avg_time': Calcula o tempo médio
                'std_time': Calcula o desvio padrão do tempo.   
            - col_number: Objeto onde os resultados serão exibidos 
                 col3, col4, etc.
            - festival: Parâmetro define período durante o Festival
                'Yes': Durante o festival 
                'No': Durante período que não ocorre o festival
        Output:
            - df: Dataframe com 2 colunas e 1 linha.

    """
    df_aux = (df.loc[:, ['Time_taken(min)', 'Festival']]
            .groupby('Festival')
            .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)
    col_number.metric(number_title, df_aux)
    return df_aux

#------------------------------------Fim função de Gráficos--------------------------------

#---------------------------------------------------------------------- Início da estrutura lógica do código ---------------------------------------------------------------------

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
st.title('Visão Restaurantes')

    
#==========================================================
#=================== Layout no Streamlit ==================
#==========================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)


        with col1:
            delivery_unique = len(df.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores', delivery_unique)

        with col2:
            avg_distance = distance(df)
            col2.metric('Distância média', avg_distance)

        with col3:
            df_aux = avg_std_time_delivery (df, 'avg_time', col3, 'Tempo médio de entrega no Festival', 'Yes')

        with col4:
            df_aux = avg_std_time_delivery (df, 'std_time', col4, 'STD do tempo de entrega no Festival', 'Yes')
            
        with col5:
            df_aux = avg_std_time_delivery (df, 'avg_time', col5, 'Tempo médio de entrega sem Festival', 'No')

        with col6:
            df_aux = avg_std_time_delivery (df, 'std_time', col6, 'STD do tempo de entrega sem Festival', 'No')

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
    ############Gráfico de linhas
            

            st.markdown('### Tempo médio de entrega por cidade')
            df_aux = df.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = go.Figure()
            fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
            fig.update_layout(barmode='group')
            st.plotly_chart( fig, use_container_width=True )

    ############Tabela de distribuição da distância        
        with col2:
            st.markdown('### Distribuição da Distância')
            df_aux = (df.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']]
                    .groupby(['City', 'Type_of_order'])
                    .agg({'Time_taken(min)': ['mean', 'std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux, use_container_width=True)            

    with st.container():
        st.title('Distribuição do Tempo')
        col1, col2 = st.columns(2)

        with col1:
           ###Gráfico de pizza
           cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
           df['Distance'] = df.loc[:, cols].apply(lambda x:
                                                haversine(   (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                             (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            
           avg_distance = df.loc[:, ['City', 'Distance']].groupby('City').mean().reset_index()
           fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['Distance'], pull=[0, 0.1, 0])])
           st.plotly_chart( fig , use_container_width=True)

        with col2:
            ###Gráfico sunburst
            df_aux = (df.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                    .groupby(['City', 'Road_traffic_density'])
                    .agg({'Time_taken(min)': ['mean', 'std']}))

            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = (px.sunburst(df_aux, path=['City', 'Road_traffic_density'], 
                                      values='avg_time', color='std_time', color_continuous_scale='RdBu', 
                                      color_continuous_midpoint=np.average(df_aux['std_time'])))

            st.plotly_chart( fig , use_container_width=True)