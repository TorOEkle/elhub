import pandas as pd
import streamlit as st

st.header('Diskontering')
byggetid = st.number_input('Byggetid (år)', min_value=0, max_value=100, value=3, step=1)
byggekost = st.number_input('Byggekost (MNOK/mw)', min_value=0, max_value=150, value=30, step=1)
kraftpris = st.number_input('Kraftpris (øre/kwh)', min_value=0, max_value=200, value=60, step=1)
levetid = st.number_input('Levetid (år)', min_value=0, max_value=100, value=60, step=1)
diskonteringsrente = st.number_input('Diskonteringsrente (%)', min_value=0.0, max_value=100.0, value=7.0, step=0.1)
kapasitetsfaktor = st.number_input('Kapasitetsfaktor (%)', min_value=0.0, max_value=100.0, value=95.0, step=0.1)
inndekning = kraftpris-22
r = (diskonteringsrente/100)+1
kapasitetsfaktor = kapasitetsfaktor/100
st.write("Antar at investeringskostnader investeres linært over byggetiden og operasjonskostnader på 22øre/kwh")

totalt_n = byggetid+60
byggekost_aarlig = byggekost/byggetid

inndekning = kraftpris-22
produksjon = kapasitetsfaktor*8760
inntekt = produksjon*1000*inndekning/100 #mwh to kwh, øre to kr
inntekt_mill = inntekt/1000000

# make a sequence where byggekost_aarlig *byggetid is first elements and inndekning *60 is last elements
byggekost_aarlig_list = [-byggekost_aarlig for i in range(byggetid)]
inndekning_list = [inntekt_mill for i in range(60)]
cash_flow = byggekost_aarlig_list + inndekning_list

# mage a sequence of total_n * r
r_list = [r for i in range(totalt_n)]
#make a sequence that starts with 1 and goes to total_n
n_list = [i for i in range(totalt_n)]
# make pandas of r_list, n_list and cash_flow
df = pd.DataFrame(list(zip(r_list, n_list, cash_flow)), columns =['r', 'n', 'cash_flow'])
#convert n to float
df['n'] = df['n'].astype(float)

df['diskonteringsfaktor'] = df['r']**df['n']
df['diskontert_verd'] = df['cash_flow']/df['r']**df['n']

#make a column that cumsums the diskontert_verd
df['diskontert_verd_cumsum'] = df['diskontert_verd'].cumsum()

#make a plot of diskontert_verd_cumsum and n on x axis with plotly
import plotly.express as px
fig = px.line(df, x="n", y="diskontert_verd_cumsum", title='Diskontert verdi')
# change title of x axis
fig.update_xaxes(title_text='År')
#change title of y axis
fig.update_yaxes(title_text='Diskontert cashflow (MNOK/MW)')
st.plotly_chart(fig)

st.dataframe(df)
