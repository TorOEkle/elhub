import streamlit as st
st.set_page_config(layout="wide", page_title= 'Elhub visualized', page_icon= "lightning")
import pandas as pd
from plotly.subplots import make_subplots
import numpy as np
import plotly.express as px
#from PIL import Image

#image = Image.open('elhub_logo.png')
#col1, col2, col3 = st.columns([1.5,2,3])
#with col1:
#    st.image(image, width= 300)
#with col2:
#    st.title("Plot of Elhub data")
#    st.subheader('Source: https://elhub.no/statistikk/')
#with col3:
#    st.write("")
st.title("Visualisering av Elhub data")
st.subheader('Kilde: https://elhub.no/statistikk/')

#Cache data so it does not load for every time different regions is chosen
@st.cache(ttl= 86400)
def load_data1():
    data1 = pd.read_excel('https://elhub.no/app/uploads/2022/10/Daglig-produksjon-pr-gruppe-og-prisomrade-MWh.xlsx')
    return data1

@st.cache(ttl= 86400)
def load_data2():
    data2 = pd.read_excel('https://elhub.no/app/uploads/2022/10/Daglig-nettap-pr-prisomrade-MWh.xlsx')
    return data2

@st.cache(ttl= 86400)
def load_data3():
    data3 = pd.read_excel('https://elhub.no/app/uploads/2022/10/Daglig-forbruk-pr-gruppe-og-prisomrade-MWh.xlsx')
    return data3

df_produksjon = load_data1()
df_loss = load_data2()
df_group = load_data3()

# Wrangle production data   
df_produksjon = df_produksjon.rename(columns=df_produksjon.iloc[0]).drop(df_produksjon.index[0])
df_produksjon.rename(columns={
    'Bruksdøgn':'dato',
    'Produksjonstype':'produksjonstype',
    'Prisområde':'region',
    'Volum (MWh)': 'volum'
}, inplace = True)

df_produksjon = df_produksjon.astype({'volum':'int64',
                'region':'category',
                'produksjonstype': 'category',
                'dato': 'datetime64'})

# Wrangle transmission loss data
df_loss = df_loss.rename(columns=df_loss.iloc[0]).drop(df_loss.index[0])
df_loss.rename(columns={
    'Bruksdøgn':'dato',
    'Prisområde':'region',
    'Fysisk nettap':'fysisk_tap',
    'Administrativt nettap': 'admin_tap'
}, inplace = True)
df_loss = df_loss.astype({'region':'category',
                'admin_tap':'int64',
                'fysisk_tap': 'int64',
                'dato': 'datetime64'})
#Wranlge consumption data
df_group = df_group.rename(columns=df_group.iloc[0]).drop(df_group.index[0])
df_group.rename(columns={
    'Bruksdøgn':'dato',
    'Prisområde':'region',
    'Gruppe':'gruppe',
    'Volum (MWh)': 'volum',
    'Antall målepunkter': 'antall_konsumenter'
}, inplace = True)
df_group = df_group.astype({'region':'category',
                'volum':'int64',
                'antall_konsumenter': 'int64',
                'dato': 'datetime64',
                'gruppe':'category'})'

## Add prod volume to transmission loss df
df_prod_volum = df_produksjon.groupby(['dato', 'region'])[['volum']].sum().reset_index()
df_loss = pd.merge(df_loss, df_prod_volum, how='left', left_on=['dato','region'], right_on=['dato','region'])
df_loss.rename(columns= {'volum': 'prod_volum'}, inplace= True)

st.write('Kart over hvor de ulike regionene er https://www.nordpoolgroup.com/en/maps/#/nordic')
options = st.multiselect(
    'Hvilke region(er) vil du se på?',
    ['NO1', 'NO2', 'NO3', 'NO4', 'NO5'],['NO1', 'NO2', 'NO3', 'NO4', 'NO5'], help= 'Data blir aggregert for de valgte regionene, velg alle = Norge')

length = len(options)
if length == 0:
    st.warning('Velg minst en region')
    st.stop()
elif length == 1:
    df_produksjon_filter = df_produksjon[df_produksjon['region'] == options[0]]
    df_loss_filter = df_loss[df_loss['region'] == options[0]]
    df_group_filter = df_group[df_group['region'] == options[0]]
else:
    df_produksjon_filter = df_produksjon[df_produksjon['region'].isin(options)] # Filter for choosen regions
    df_produksjon_filter =df_produksjon_filter.groupby(['dato', 'produksjonstype'])[['volum']].sum().reset_index() # Aggregate data
    df_loss_filter = df_loss[df_loss['region'].isin(options)] 
    df_loss_filter = df_loss_filter.groupby(['dato'])[['fysisk_tap','admin_tap','prod_volum']].sum().reset_index() 
    df_loss_filter['fysisk_tap_andel'] = df_loss_filter['fysisk_tap']/df_loss_filter['prod_volum']
    df_group_filter = df_group[df_group['region'].isin(options)] 
    df_group_filter = df_group_filter.groupby(['dato','gruppe'])[['volum','antall_konsumenter']].sum().reset_index()
 


st.subheader(f'''Grafer for  {options}''')
#Prepare plots
fig_loss= make_subplots(specs=[[{"secondary_y": True}]])
fig1 = px.line(df_loss_filter, x = 'dato', y= ['fysisk_tap','admin_tap'], template= 'plotly_white')
fig2 = px.line(df_loss_filter, x = 'dato', y= ['fysisk_tap_andel'], template= 'plotly_white')
fig2.update_traces(yaxis="y2",line_color='#DC3912')
fig_loss.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
}, showlegend=False, title_text = 'Transmisjonstap <br><sup>Rød linje er andel av produksjon, akse til høyre</sup>')
fig_loss.add_traces(fig1.data + fig2.data)

fig_group = px.line(df_group_filter, x = 'dato', y= ['volum'], color= 'gruppe', template= 'plotly_white', title= 'Forbruk per gruppe' )
fig_group.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
}, showlegend=False, yaxis_title="Volum [MWh]")

fig_prod = px.line(df_produksjon_filter,x = 'dato', y = 'volum', color= 'produksjonstype',template="plotly_white",title="Produksjon per type")
fig_prod.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
}, showlegend=False, yaxis_title="Volum [MWh]")

st.plotly_chart(fig_prod, use_container_width=True)
st.plotly_chart(fig_group, use_container_width=True)
st.plotly_chart(fig_loss, use_container_width=True)

# run from terminal: py -m streamlit run elhub_streamlit.py

