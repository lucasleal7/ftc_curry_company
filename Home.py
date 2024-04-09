import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='📊',
    layout='wide'
    
)


#image_path = r"C:\Users\55149\OneDrive - Fatec Centro Paula Souza\Documents\repos\logo.jpeg"
image= Image.open("logo.jpeg")
st.sidebar.image(image,width=120)

st.sidebar.markdown("### Curry company")
st.sidebar.markdown("## fastest delivery in town")
st.sidebar.markdown("""___""")

st.write('# Curry Company dashboard')

st.markdown(
    """
    Growth Dashboard foi construido para acompanhar as métricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar esse dashboard growth dashboard?

    -Visão Empresa:

        -Visão Gerencial: Métricas gerais de comportamento.

        -Visão tática: indicadores semanais de crescimento.

        -Visão Geográfica: Insights de geocalização.

    -Visão entregador:

        -Acompanhamento dos indicadores semanais de crescimento

    -Visão Restaurante:

        -Indicadores semanais de crescimento dos restaurantes

    ### Ask for help
    - Time de Data science no discord 
        -@leal       
""")