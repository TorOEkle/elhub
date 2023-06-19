import streamlit as st
import pandas as pd
st.header('Tors el kalkulator')

dict = {'Vaskemaskin': 2.250,
        'Oppvaskmaskin': 2.250,
        'TV': 0.150,
        'Komfyr': 1.250,
        'Kaffetrakter': 1.250,
        'Panelovn': 0.100,
        'Varmepumpe': 0.750,
        'Dusj': 32}
test = pd.DataFrame(dict, index = [0])


apparat = st.selectbox('Velg et apparat', list(dict.keys()))
c1, c2, c3 = st.columns(3)
with c1:
        effekt = st.number_input('Effekt i kw', value = test[f'''{apparat}'''][0] , key ='effekt')
with c2:
        varighet = st.number_input('Brukstid i minutter', value=60 , key ='varighet')
with c3:
        pris = st.number_input('Hva er prisen? nok/kwh ', value=2.5 , key ='pris')
        st.write('Pris kan en finne her https://www.nordpoolgroup.com/en/Market-data1/#/nordic/table. PS: avgifter kommer i tillegg. ca 0.45nok/kwh')

st.header(f'''Pris for bruk: {round(effekt*(varighet/60)*pris,2)} NOK''')
