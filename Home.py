import streamlit as st
from PIL import Image

st.set_page_config( 
    page_title="Home",
    page_icon='🎲'
)

#==========================================================
#=============== Barra Lateral no Streamlit ===============
#==========================================================
st.header('Marketplace - Visão Cliente')

#image_path = 'E:\\Priscila\\repos\\ftc_programacao_python\\ciclo_05\\imagem_logo.png'
image = Image.open( 'imagem_logo.png' )
st.sidebar.image( image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Faster Delivery in Town')
st.sidebar.markdown("""---""")


st.write("# Curry Company Growth Dashboard")
st.markdown( """ 
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão da Empresa:
        - Visão Gerencial: Métricas gerais de comportamento
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    -Visão Entregador:
        - Acompnhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes

    ### Ask for Help
        ✉️ E-mail de contato: priscila.rportela@gmail.com       
    """)