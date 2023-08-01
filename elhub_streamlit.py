import streamlit as st
st.set_page_config(layout="wide", page_title= 'Elhub visualized', page_icon= "lightning")
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
from PIL import Image
import re

## import styling
with open('style.css')as f:
 st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html = True)

image = Image.open('elhub_logo.png')

col1, col2 = st.columns([1,1])
with col1:
    st.image(image, width= 300)
with col2:
    st.title("Plot of Elhub data")
    st.subheader('Source: https://elhub.no/statistikk/')
#with col3:
#    st.title(" ")
#    st.subheader(' ')
#Cache data so it does not load for every time different regions is chosen
@st.cache_data(ttl= 86400)
def load_data1():
    data1 = pd.read_excel('https://elhub.no/app/uploads/2023/06/Daglig-produksjon-pr-type-og-prisomrade-MWh-1.xlsx')
    return data1

@st.cache_data
def load_data2(ttl= 86400):
    data2 = pd.read_excel('https://elhub.no/app/uploads/2023/06/Daglig-nettap-pr-prisomrade-MWh-1.xlsx')
    return data2

@st.cache_data
def load_data3(ttl= 86400):
    data3 = pd.read_excel('https://elhub.no/app/uploads/2023/06/Daglig-forbruk-pr-gruppe-og-prisomrade-MWh-1.xlsx')
    return data3

df_produksjon = load_data1()
#df_loss = load_data2()
df_group = load_data3()

#Wrangle production data
df_produksjon.rename(columns={
    'Bruksdøgn':'dato',
    'Produksjonstype':'produksjonstype',
    'Prisområde':'region',
    'Volum (MWh)': 'volum'
}, inplace = True)
df_produksjon = df_produksjon.astype({'volum':'int64',
                'region':'category',
                'produksjonstype': 'category',
                'dato': 'datetime64[ns]'})

## Wrangle transmission loss data
#df_loss.rename(columns={
    'Bruksdøgn':'dato',
    'Prisområde':'region',
    'Fysisk Nettap':'fysisk_tap',
    'Administrativt Nettap': 'admin_tap'
}, inplace = True)
#df_loss = df_loss.astype({'region':'category',
                'admin_tap':'int64',
                'fysisk_tap': 'int64',
                'dato': 'datetime64[ns]'})
##Wranlge consumption data
df_group.rename(columns={
    'STARTDATE':'dato',
    'MBA':'region',
    'GROUPDESCRIPTION':'gruppe',
    'VOLMWH': 'volum',
    'ANTMP': 'antall_konsumenter'
}, inplace = True)
df_group = df_group.astype({'region':'category',
                'volum':'int64',
                'dato': 'datetime64[ns]',
                'gruppe':'category'})

##Correct for outlier in NO3 21. july 2021
median_termal = df_produksjon.loc[(df_produksjon['region'] == 'NO3') & (df_produksjon['produksjonstype'] == 'Termisk kraft')].volum.median()
df_produksjon.loc[(df_produksjon['region'] == 'NO3') & (df_produksjon['produksjonstype'] == 'Termisk kraft')& (df_produksjon['dato'] == '2020-07-21'), 'volum'] = median_termal
median_gruppe = df_group.loc[(df_group['region'] == 'NO3') & (df_group['gruppe'] == 'Elektrisitets-, gass-, damp- og varmtvannsforsyning')].volum.median()
df_group.loc[(df_group['region'] == 'NO3') & (df_group['dato'] == '2020-07-21') & (df_group['gruppe'] == 'Elektrisitets-, gass-, damp- og varmtvannsforsyning'), 'volum'] = median_gruppe

options = st.multiselect(
    'Which region do you want to look at? Map where different regions is https://www.nordpoolgroup.com/en/maps/#/nordic',
    ['NO1', 'NO2', 'NO3', 'NO4', 'NO5'],['NO1', 'NO2', 'NO3', 'NO4', 'NO5'], help= 'If more than one region is choosen, data is aggregated over these regions')

## Add transmission loss as percentage of consumption
df_prod_volum = df_produksjon.groupby(['dato', 'region'])[['volum']].sum().reset_index()
#df_loss = pd.merge(df_loss, df_prod_volum, how='left', left_on=['dato','region'], right_on=['dato','region'])
#df_loss.rename(columns= {'volum': 'prod_volum'}, inplace= True)

length = len(options)
if length == 0:
    st.warning('Choose at least one region')
    st.stop()
elif length == 1:
    df_produksjon_filter = df_produksjon[df_produksjon['region'] == options[0]]
    #df_loss_filter = df_loss[df_loss['region'] == options[0]]
    #df_loss_filter['fysisk_tap_andel'] = df_loss_filter['fysisk_tap']/df_loss_filter['prod_volum']
    df_group_filter = df_group[df_group['region'] == options[0]]
else:
    df_produksjon_filter = df_produksjon[df_produksjon['region'].isin(options)] # Filter for choosen regions
    df_produksjon_filter =df_produksjon_filter.groupby(['dato', 'produksjonstype'])[['volum']].sum().reset_index() # Aggregate data
    #df_loss_filter = df_loss[df_loss['region'].isin(options)] 
    #df_loss_filter = df_loss_filter.groupby(['dato'])[['fysisk_tap','admin_tap','prod_volum']].sum().reset_index() 
    #df_loss_filter['fysisk_tap_andel'] = df_loss_filter['fysisk_tap']/df_loss_filter['prod_volum']
    df_group_filter = df_group[df_group['region'].isin(options)] 
    df_group_filter = df_group_filter.groupby(['dato','gruppe'])[['volum','antall_konsumenter']].sum().reset_index() 
 


#st.subheader(f'''Plots for  {options}''')
#Prepare plots
#fig_loss= make_subplots(specs=[[{"secondary_y": True}]])
#fig1 = px.line(df_loss_filter, x = 'dato', y= ['fysisk_tap','admin_tap'], template= 'plotly_white')
#fig2 = px.line(df_loss_filter, x = 'dato', y= ['fysisk_tap_andel'], template= 'plotly_white')
#fig2.update_traces(yaxis="y2",line_color='#DC3912')
#fig_loss.update_layout({
#'plot_bgcolor': 'rgba(0, 0, 0, 0)',
#'paper_bgcolor': 'rgba(0, 0, 0, 0)',
#}, showlegend=False, title_text = 'Transmisjonstap <br><sup>Rød linje er andel av produksjon, akse til høyre</sup>')
#fig_loss.add_traces(fig1.data + fig2.data)

fig_group = px.line(df_group_filter, x = 'dato', y= ['volum'], color= 'gruppe', template= 'plotly_white', title= 'Consumption by group' )
fig_group.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
}, showlegend=False, yaxis_title="Volume [Mwh]")

fig_prod = px.line(df_produksjon_filter,x = 'dato', y = 'volum', color= 'produksjonstype',template="plotly_white",title="Production by source")
fig_prod.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
}, showlegend=False, yaxis_title="Volume [Mwh]")

#KPI for metrics
date_prod = df_produksjon_filter.groupby(['dato'])[['volum']].sum().reset_index().sort_values(by='volum', ascending=False).head(1).iloc[0]['dato'].strftime('%d. %B %Y')
max_prod = df_produksjon_filter.groupby(['dato'])[['volum']].sum().reset_index().sort_values(by='volum', ascending=False).head(1).iloc[0]['volum']
date_consumption = df_group_filter.groupby(['dato'])[['volum']].sum().reset_index().sort_values(by='volum', ascending=False).head(1).iloc[0]['dato'].strftime('%d. %B %Y') 
max_consumption = df_group_filter.groupby(['dato'])[['volum']].sum().reset_index().sort_values(by='volum', ascending=False).head(1).iloc[0]['volum']
consumption_last_days = df_group_filter.groupby(['dato'])[['volum']].sum().reset_index().tail(2)['volum']




st.markdown('<hr/>', unsafe_allow_html = True)
col4, col5, col6 = st.columns(3)
with col4:
    st.metric(label=f'Date for max production {date_prod}', value= re.sub(',', ' ', f'{max_prod:,} [MWh]'))
with col5:
    st.metric(label=f'Date for max consumption {date_consumption}', value= re.sub(',', ' ', f'{max_consumption:,} [MWh]'))
with col6:
    st.metric(label="Consumption last day", value= re.sub(',', ' ', f'{consumption_last_days.iloc[1]:,} [MWh]'), delta= consumption_last_days.diff().iloc[1])
st.markdown('<hr/>', unsafe_allow_html = True)




st.plotly_chart(fig_prod, use_container_width=True)
st.plotly_chart(fig_group, use_container_width=True)
#st.plotly_chart(fig_loss, use_container_width=True)

# run from terminal: py -m streamlit run elhub_streamlit.py
# How to style metrics https://medium.com/pythoneers/how-to-style-streamlit-metrics-in-custom-css-9a0f02b150da

