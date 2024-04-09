#bibliotecas

import pandas as pd
import plotly.graph_objects as go
from haversine import haversine
from datetime import datetime
import streamlit as st
from PIL import Image

st.set_page_config(page_title='Visão Entregadores', page_icon='📊',layout='wide')

#______________________
#Funções
#______________________

def top_delivers(df1,top_asc):
    df2=(df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
            .groupby(['Delivery_person_ID','City'])
            .max()
            .sort_values(['City','Time_taken(min)'],ascending=top_asc).reset_index())
    aux01=df2.loc[df2['City']=='Metropolitian ',:].head(10)
    aux02=df2.loc[df2['City']=='Urban ',:].head(10)
    aux03=df2.loc[df2['City']=='Semi-Urban ',:].head(10)
    lentos=pd.concat([aux01,aux02,aux03]).reset_index(drop=True)       
    return lentos

def clean_code(df1):
    #esta função tem a responsabilidade de limpar o dataframe
    #1- Remoção dos dados NaN
    #2- Mudança do tipo da coluna de dados
    #3- Remoção de espaços nas variavéis de texto
    #4- Formatação da coluna de datas 
    #5- Limpeza da coluna de tempo (remoção do texto da varivél numérica)
    
    #Input: Dataframe
    #Output: Dataframe

    
    linhas_selecionadas=df1['Delivery_person_Age'] != 'NaN '
    df1=df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas=df1['Road_traffic_density'] != 'NaN '
    df1=df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas=df1['City'] != 'NaN '
    df1=df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas=df1['Festival'] != 'NaN '
    df1=df1.loc[linhas_selecionadas,:].copy()

    df1['Delivery_person_Age']=df1['Delivery_person_Age'].astype(int)

    df1['Delivery_person_Ratings']=df1['Delivery_person_Ratings'].astype(float)

    df1['Order_Date']=pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')


    linhas_selecionadas=df1['multiple_deliveries'] != 'NaN '
    df1=df1.loc[linhas_selecionadas,:].copy()
    df1['multiple_deliveries']=df1['multiple_deliveries'].astype(int)

    df1.loc[:,'ID']=df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Festival']=df1.loc[:,'Festival'].str.strip()


    #limpando coluna Time_taken(min)

    df1['Time_taken(min)']=df1['Time_taken(min)'].apply(lambda x: x.split( '(min)')[1])
    df1['Time_taken(min)']=df1['Time_taken(min)'].astype(int)

    #criando coluna distancia
    cols=['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']

    df1['Distance']=df1.loc[:,cols].apply( lambda x:haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis=1 )

    return df1

#----------------------------------------------------------- Inicio da estrutura Lógica do código ----------------------------------
#------------------------------
#Importando Dataset e Imagem para o streamlit
#------------------------------
df = pd.read_csv('train.csv')
#image_path = r"C:\Users\55149\OneDrive - Fatec Centro Paula Souza\Documents\repos\logo.jpeg"
image=Image.open('logo.jpeg')
st.sidebar.image(image, width=120)
#----------------------
#limpando os dados
#----------------------

df1=clean_code(df)

#usando o streamlit 

#===================
# Barra Lateral
#===================
st.header('Marketplace-Visão Entregadores')
st.sidebar.markdown("### Curry company")
st.sidebar.markdown("## fastest delivery in town")
st.sidebar.markdown("""___""")

st.sidebar.markdown("## Selecione uma data limite")

date_slider=st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022,4,13),
    min_value=datetime(2022,2,11),
    max_value=datetime(2022,4,6),
    format='DD-MM-YYYY')

#obs: o nome das linhas contem um espaço fazio que eu não ajustei
traffic_options=st.sidebar.multiselect(
    'Quais são as condições do trânsito?',
    ['Low ','Medium ','High ','Jam '],
    default=['Low ','Medium ','High ','Jam '])

st.sidebar.markdown("""___""")
st.sidebar.markdown('## powered by Lucas Leal')


#filtro de data
ls=df1['Order_Date']<date_slider
df1=df1.loc[ls,:]

#filtro de transito
ls=df1['Road_traffic_density'].isin(traffic_options)
df1=df1.loc[ls,:]

#==================
#layout
#==================

tab1,tab2,tab3=st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():

        st.title('overall metrics')
        col1,col2,col3,col4=st.columns(4,gap='large')
        
        with col1:

            maior_idade=df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('maior idade',maior_idade)

        with col2:

            menor_idade=df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('menor idade',menor_idade)

        with col3:

            melhor_cond=df1.loc[:,'Vehicle_condition'].max()
            col3.metric('melhor condição',melhor_cond)

        with col4:

            pior_cond=df1.loc[:,'Vehicle_condition'].min()
            col4.metric('pior condição',pior_cond)

    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')

        col1,col2=st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por entregador')
            aval_media_entre=df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(aval_media_entre)

        with col2:

            st.markdown('##### Avaliação média por trânsito')
            media=df1.loc[:,['Delivery_person_Ratings','Road_traffic_density']].groupby('Road_traffic_density').mean().reset_index()
            st.dataframe(media)

            st.markdown('##### Avaliação média por clima')
            media_por_clima=df1.loc[:,['Delivery_person_Ratings','Weatherconditions']].groupby('Weatherconditions').mean().reset_index()
            st.dataframe(media_por_clima)

    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de entrega')

        col1,col2=st.columns(2)
        with col1:
            st.subheader('top entregadores mais rápidos')
            lentos=top_delivers(df1,top_asc=True)
            st.dataframe(lentos)

        with col2:
            st.subheader('top entregadores mais lentos')
            lentos=top_delivers(df1,top_asc=False)
            st.dataframe(lentos)



