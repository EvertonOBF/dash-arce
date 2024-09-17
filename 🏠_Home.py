import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards

## ------------------ SIDEBAR --------------------

st.set_page_config(
    page_title="Dash-transporte",
    page_icon="chart_with_upwards_trend",
    layout="wide")

## Página inicial -- Apresentação do dash

st.markdown("### Análise do fluxo de passageiros intermunicipais do Ceará", )
st.divider()
st.markdown(
    '''
    <div style="text-align: justify">
        Dashboard Python para Gestão de Transporte Coletivo: Visualize indicadores chave e otimize decisões 
        em mobilidade urbana. 
    </div>
    ''',
    unsafe_allow_html=True
)

st.write("")

st.markdown(
    '''
        Desenvolvido pelo projeto de Iniciação Científica da Engenharia Civil do 
        [Centro Universitário Christus](https://www.unichristus.edu.br/curso/graduacao-em-engenharia-civil/).
    '''
)

st.write("")
st.write("")

col1, col2 = st.columns(2)

with col1:
    st.image("Logo_Unichristus.png", width=300)

with col2:
    st.image("arce.png", width=300)

