import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Plot av Elhub data")
st.subheader('Kilde: https://elhub.no/statistikk/')

data_load_state = st.text('Loading data on production')

@st.cache
def load_data1():
    data1 = pd.read_excel('https://elhub.no/app/uploads/2022/10/Daglig-produksjon-pr-gruppe-og-prisomrade-MWh.xlsx')
    return data1

df_produksjon = load_data1()


data_load_state.text('Do some data wrangling')

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

data_load_state.text('Data wrangling...done!, Plotting next')

st.subheader('Plot electricity production by method in NO2')
df = df_produksjon
fig = px.line(df,x = df[df['region']=='NO2']['dato'], y = df[df['region']=='NO2']['volum'], color= df[df['region']=='NO2']['produksjonstype'],template="simple_white")
st.plotly_chart(fig, use_container_width=True)

# Multiple plots in one figure https://plotly.com/python/subplots/

# glpat-UzoeUjepMSi-eKnRWKDM

