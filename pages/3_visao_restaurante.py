import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
from datetime import datetime
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import folium
import numpy as np

st.set_page_config(page_title='Visão Restaurante', page_icon='📊',layout='wide')

#______________________
#Funções
#______________________

def avg_std_time_on_traffic(df1):
    df_aux=df1.loc[:,['City','Time_taken(min)','Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
    df_aux.columns=['avg_time','std_time']
    df_aux=df_aux.reset_index()
    fig=px.sunburst(df_aux,path=['City', 'Road_traffic_density'],values='avg_time',
            color='std_time',color_continuous_scale='RdBu',
            color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

def avg_std_time_graph(df1):            
    df_aux=df1.loc[:,['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']})
    df_aux.columns=['avg_time','std_time']
    df_aux=df_aux.reset_index()
    fig=go.Figure()
    fig.add_trace(go.Bar(name='Control',
                x=df_aux['City'],
                y=df_aux['avg_time'],
                error_y=dict(type='data',array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def avg_std_delivery_time(df1,festival,op):
    #esta função cacula o tempo médio e o desvio padrão do tempo de entrega
        #Parametros:
            #Input:
                #-df: Dataframe com os dados necessarios para o calculo
                #-op: Tipo de operação que precisa ser calculado 
                    #avg_time: Calcula o tempo médio
                    #std_time: Calcula o desvio padrão do tempo 
            #Output:
                #df: Dataframe com 2 colunas e 1 linha 
                
    df_aux=df1.loc[:,['Time_taken(min)','Festival']].groupby(['Festival']).agg({'Time_taken(min)':['mean','std']})
    df_aux.columns=['avg_time','std_time']
    df_aux=df_aux.reset_index()
    df_aux=np.round(df_aux.loc[df_aux["Festival"]==festival,op],2)
    return df_aux

def distance(df1,fig):
    if fig==False:
        cols=['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
        df1['Distance']=df1.loc[:,cols].apply( lambda x:haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis=1 )
        avg_distance=np.round(df1['Distance'].mean(),2)
        return avg_distance
    
    else:
        cols=['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
        df1['Distance']=df1.loc[:,cols].apply( lambda x:haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis=1 )
        avg_distance=df1.loc[:,['City','Distance']].groupby('City').mean().reset_index()
        fig=go.Figure(data=[go.Pie(labels=avg_distance['City'],values=avg_distance['Distance'],pull=[0,0.1,0])])
        return fig
            
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

#buscando o arquivo train.csv e imagem
df = pd.read_csv('train.csv')
image=Image.open('logo.jpeg')
st.sidebar.image(image, width=120)

#----------------------
#limpando os dados
#----------------------

df1=clean_code(df)

#===================
# Barra Lateral
#===================

st.header('Marketplace-Visão Restaurantes')
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

#==============
#Layout
#==============

tab1,tab2,tab3=st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overal Metrics')
        col1,col2,col3,col4,col5,col6=st.columns(6)

        with col1:
            du=len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', du)

        with col2:
            avg_distance=distance(df1, fig=False)
            col2.metric('Distância média das entregas', avg_distance)

        with col3:
            df_aux=avg_std_delivery_time(df1,'Yes', 'avg_time')
            col3.metric('tempo médio de entrega no festival', df_aux)

        with col4:
            df_aux=avg_std_delivery_time(df1,'Yes','std_time')
            col4.metric('desvio padrão no tempo de entrega no festival', df_aux)         

        with col5:
            df_aux=avg_std_delivery_time(df1,'No', 'avg_time')
            col5.metric('tempo médio de entrega no festival', df_aux)
            
        with col6:
            df_aux=avg_std_delivery_time(df1,'No','std_time')
            col6.metric('desvio padrão no tempo de entrega no festival', df_aux)
        
    with st.container():
        st.markdown("""___""")
        st.title('tempo médio de entrega por cidade')
        col1,col2=st.columns(2)
        with col1:
            fig=avg_std_time_graph(df1)
            st.plotly_chart(fig,use_container_width=True)
        
        with col2:
            df_aux=df1.loc[:,['City','Time_taken(min)','Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)':['mean','std']})

            df_aux.columns=['avg_time','std_time']
            df_aux=df_aux.reset_index()
            st.dataframe(df_aux)

    
    with st.container():
        st.markdown("""___""")
        st.title('Distribuição por tempo')
        col1,col2 =st.columns(2)
        with col1:
            fig=distance(df1,fig=True)
            st.plotly_chart(fig,use_container_width=True)


        with col2:
            fig= avg_std_time_on_traffic(df1)
            st.plotly_chart(fig,use_container_width=True)




        




