import streamlit as st
import psycopg2
from streamlit_folium import st_folium
import folium
from streamlit_extras.metric_cards import style_metric_cards
import pandas as pd 
import numpy as np
import plotly.express as px
from funcoes_uteis import fluxo_mensal, media_semanal, media_hora, converter_tempo, func_tempo_viagem, format_number, leitura_de_dados

st.set_page_config(
    layout="wide"
)

config = {'displayModeBar': False}
# -------------------------- Removendo o recuo do texto superior -------------------------------
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 2rem;
                    padding-right: 2rem;
                }
        </style>
        """, unsafe_allow_html=True)

# ------------------------ Regulando o tamanho do sidebar ---------------------------------------
st.markdown(f'''
    <style>
        section[data-testid="stSidebar"] .css-ng1t4o {{width: 14rem;}}
        section[data-testid="stSidebar"] .css-1d391kg {{width: 14rem;}}
    </style>
''',unsafe_allow_html=True)
# ----------------------------------- conectando postgrees ------------------------------------

conexao = psycopg2.connect(database = "sindionibus",
                           host = "localhost",
                           user = "postgres",
                           password = "everton1310",
                           port = "5432",
)

cursor = conexao.cursor()

# ---------------------------  Sidebar para selecionar a empresa --------------------------------

#cursor.execute('SELECT DISTINCT empresa_codigo FROM dados_passageiros')
#lista_empresas = [row[0] for row in cursor.fetchall()]
lista_empresas = [2, 12, 14, 19, 20, 21, 26, 30, 35, 36, 42, 55, 56, 57, 60, 64, 67, 72, 74, 76, 79, 80, 84, 86]
empresa_selecionada = st.sidebar.selectbox("Selecione a empresa", lista_empresas)

df_empresa, chave_unica = leitura_de_dados(empresa_selecionada, cursor)
df_empresa = df_empresa.iloc[:,[0, 3, 4, 5, 6, 7, 8, 9]]

# --------------------------- Sidebar para selecionar a linha de ônibus -------------------------

lista_linhas = list(df_empresa.groupby('linha')['subsidio'].count().sort_values(ascending=False).reset_index()['linha'].values)
lista_linhas.insert(0,"Todas")
linha_selecionada = st.sidebar.selectbox("Selecione a linha", lista_linhas)

if linha_selecionada == 'Todas':
    df_linha = df_empresa.copy()
else:
    df_linha = df_empresa[df_empresa['linha'] == linha_selecionada]

df_linha['tempo_viagem'] = df_linha['tempo_viagem'].astype('timedelta64[ns]')

st.markdown(f"##### Indicadores - Empresa {empresa_selecionada}")

# ------------------------ Indicadores - Cards --------------------------
col1, col2, col3, col4, col5, col6 = st.columns(6)

# --------------------------- Total de passageiros por empresa -------------------- #
df_empr = df_empresa[['linha', 'empresa_codigo', 'subsidio']].groupby(['linha', 'empresa_codigo']).count().reset_index()
df_empr.rename(columns=({'subsidio':'total'}), inplace=True)

passageiros_empresa = df_empr[df_empr['empresa_codigo'] == empresa_selecionada]['total'].sum()
col1.metric(label="Total Transportado", value=format_number(passageiros_empresa))

# --------------------------- Média mensal da empresa ------------------------------ #
med_mes = fluxo_mensal(df_empresa)['N° de passageiros'].mean().round()
col2.metric(label="Média Mensal", value=format_number(med_mes))

# --------------------------- Média semanal da empresa ------------------------------ #
media_semana = med_mes/4.5
col3.metric(label="Média Semanal", value=format_number(media_semana))

# --------------------------- Média semanal da empresa ------------------------------ #
media_dia = med_mes/30
col4.metric(label="Média Diária", value=format_number(media_dia))

# --------------------------- Número de linhas ------------------------------ #
col5.metric(label='Número de linhas', value=len(lista_linhas))

# --------------------------- Média semanal da empresa ------------------------------ #
col6.metric(label='Tamanho da frota', value=10)

style_metric_cards()

# ---------------- Dados para serem apresentados nos gráficos -------------

df_mensal = fluxo_mensal(df_linha)
df_semanal = media_semanal(df_linha)
df_media_hora = media_hora(df_linha)
tempo_viagem = func_tempo_viagem(df_linha)

# ----------------- Criando os cards para os gráficos ----------------------
#st.markdown(f"###### Indicadores - Linha {linha_selecionada}")
st.markdown(
    f"<h6 style='position:absolute; left:35%; top:50%; transform: translate(-50%, -25%);'>Indicadores - Linha {linha_selecionada}</h6>",
    unsafe_allow_html=True
)

col1, col2 = st.columns([3,2], gap='large')
altura = 400 # Altura dos gráficos.

with col1:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Mensal", "Semanal médio", "Horário médio", "Tempo de viagem", "Rota"])
    
    with tab1: # Apresenta o gráfico do total de passageiros transportados por mês
        fig_fluxo_mes = px.line(df_mensal, x='Período', y='N° de passageiros', labels={'Período': ''})
        fig_fluxo_mes.update_layout({'margin':{'l':0, 'r':0 , 't':10, 'b':0}}, height=altura)
        fig_fluxo_mes.update_xaxes(linewidth=1, linecolor='black')
        fig_fluxo_mes.update_yaxes(linewidth=1, linecolor='black')
        fig_fluxo_mes.update_traces(mode='lines+markers', marker=dict(size=8, symbol='circle'))
        media_mes_pass = df_mensal['N° de passageiros'].mean()
        fig_fluxo_mes.add_annotation(
        xref='paper',  # Referência do eixo x
        yref='paper',  # Referência do eixo y
        x=0.05,  # Posição horizontal da caixa de texto em porcentagem do gráfico
        y=0.95,  # Posição vertical da caixa de texto em porcentagem do gráfico
        text=f'Média mensal: {format_number(media_mes_pass)}',  # Texto da caixa de texto
        font=dict(size=16, color='black'),  # Configurações da fonte do texto
        showarrow=False,  # Não mostrar seta
        bgcolor='#f0f0f0',  # Cor de fundo da caixa de texto
        bordercolor='black',  # Cor da borda da caixa de texto
        borderwidth=1,  # Largura da borda da caixa de texto
        borderpad=5,  # Espaçamento entre o texto e a borda da caixa de text
        )

        st.plotly_chart(fig_fluxo_mes, config=config)

    with tab2: # Apresenta o gráfico do número de passageiros transportados por dia da semana
        fig_fluxo_semana = px.bar(df_semanal, x='Dia', y='Total de passageiros', text='Proporção')
        fig_fluxo_semana.update_layout({'margin':{'l':0, 'r':0 , 't':10, 'b':0}}, height=altura)
        fig_fluxo_semana.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_fluxo_semana.update_xaxes(linewidth=1, linecolor='black')
        fig_fluxo_semana.update_yaxes(linewidth=1, linecolor='black')
        st.plotly_chart(fig_fluxo_semana, config=config)

    with tab3: # Apresenta o grárfico do total de passageiros transportados por hora do dia
        fig_fluxo_hora = px.line(df_media_hora, x='Hora', y='N° de passageiros', text='Proporção')
        fig_fluxo_hora.update_layout({'margin':{'l':0, 'r':0 , 't':10, 'b':0}}, height=altura)
        fig_fluxo_hora.update_traces(mode='lines+markers', marker=dict(size=8, symbol='circle'), fill='tonexty', fillcolor='rgba(173, 216, 230, 0.5)')
        fig_fluxo_hora.update_xaxes(linewidth=1, linecolor='black')
        fig_fluxo_hora.update_yaxes(linewidth=1, linecolor='black')
        st.plotly_chart(fig_fluxo_hora, config=config)
    
    with tab4: # Gráfico do tempo médio de viagem
        fig_tempo_viagem = px.line(tempo_viagem, x = 'data', y = 'tempo (h)')
    
        tempo_medio = tempo_viagem['tempo (h)'].mean().round(2)
        tempo_medio = converter_tempo(tempo_medio)
        
        fig_tempo_viagem.add_annotation(
        xref='paper',  # Referência do eixo x
        yref='paper',  # Referência do eixo y
        x=0.05,  # Posição horizontal da caixa de texto em porcentagem do gráfico
        y=0.95,  # Posição vertical da caixa de texto em porcentagem do gráfico
        text=f'Tempo médio: {tempo_medio}',  # Texto da caixa de texto
        font=dict(size=16, color='black'),  # Configurações da fonte do texto
        showarrow=False,  # Não mostrar seta
        bgcolor='#f0f0f0',  # Cor de fundo da caixa de texto
        bordercolor='black',  # Cor da borda da caixa de texto
        borderwidth=1,  # Largura da borda da caixa de texto
        borderpad=5,  # Espaçamento entre o texto e a borda da caixa de text
        )

        from math import ceil, floor
        maior = ceil(tempo_viagem['tempo (h)'].max())
        menor = floor(tempo_viagem['tempo (h)'].min())

        fig_tempo_viagem.update_layout(
            height=altura,
            margin = dict(l=0, r=0 , t=10, b=0),
            xaxis = dict(title=None, linewidth=1, linecolor='black'),
            yaxis = dict(title='Tempo médio (h)', linewidth=1, linecolor='black', range=[menor,maior]),
        ) #tickvals = np.arange(menor, maior+1, 0.5)

        fig_tempo_viagem.update_traces(mode='lines+markers', marker=dict(size=5)) 
        st.plotly_chart(fig_tempo_viagem, config=config)

    #with tab5: # Rota do ônibus
    #    m = folium.Map(location=[-4.025097073812614, -38.4846955141984], zoom_start=9, tiles="Cartodb Positron")
    #    st_data = st_folium(m, width=725, height=360)

with col2: # Apresenta o Ranking das 10 linhas que mais transportam passageiros da empresa selecionanda

    df_top_linha = df_empresa.groupby('linha')['subsidio'].count()
    df_top_linha = df_top_linha.sort_values(ascending=False)[:10].reset_index().rename(columns={'subsidio':'Total'})
    fig = px.bar(df_top_linha, x='Total', text='Total', labels={'Total':'Nº de passageiros', 'index':'Linha'})
    
    fig.update_layout({'margin':{'l':0, 'r':0 , 't':50, 'b':0}}, width=400, 
                        title=dict(text='Top 10 - Total de passageiros por linha', x=0.25, font_size=15, font_family='Arial'),
                        )  
    fig.update_xaxes(linewidth=1, linecolor='black')
    fig.update_yaxes(title='Linha', linewidth=1, linecolor='black', tickvals=np.arange(10), ticktext=df_top_linha['linha'])
    fig.update_traces(texttemplate='%{text:.0f}', textposition='auto')
    fig.update_yaxes(categoryorder='total ascending')
    st.plotly_chart(fig, config=config)