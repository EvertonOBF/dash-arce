import streamlit as st
import psycopg2
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.stylable_container import stylable_container
import pandas as pd 
import numpy as np
import plotly.express as px
from funcoes_uteis import fluxo_mensal, media_semanal, media_hora, converter_tempo, func_tempo_viagem, format_number, leitura_de_dados, criar_container_estilizado

st.set_page_config(
    layout="wide"
)

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

config = {'displayModeBar': False}
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

leitura_de_dados(empresa_selecionada, cursor)
df_empresa = st.session_state["dados"]
df_empresa = df_empresa.iloc[:,[0, 1, 2, 3, 4, 6]]

# --------------------------- Sidebar para selecionar a linha de ônibus -------------------------

lista_linhas = list(df_empresa.groupby('linha')['subsidio'].count().sort_values(ascending=False).reset_index()['linha'].values)
lista_linhas.insert(0,"Todas")
linha_selecionada = st.sidebar.selectbox("Selecione a linha", lista_linhas)

if linha_selecionada == 'Todas':
    df_linha = df_empresa.copy()
else:
    df_linha = df_empresa[df_empresa['linha'] == linha_selecionada]

# ------------------------- Marcadores -----------------------------------------------------#
st.markdown(f"##### Receita Bruta: Empresa {empresa_selecionada} - Linha - {linha_selecionada}")

col1, col2, col3, col4 = st.columns(4)

#---------------------------------- Card 1 - Total Arrecadado --------------------------------#
with col1:
    total_arrecadado = df_linha['valor_pago'].sum()
    total_subsidio = df_linha['subsidio'].sum()
    total_arrecadado = format_number(float(total_arrecadado))
    total_subsidio = format_number(float(total_subsidio))


    #col1.metric(label="Total Arrecadado", value=f"R$ {total_arrecadado}")
    criar_container_estilizado("Total", total_arrecadado, total_subsidio)

#---------------------------------- Card 2 - Média Mensal ------------------------------------#
with col2:
    media_mes = df_linha.resample("M")['valor_pago'].sum()
    media_mes = format_number(float(media_mes.mean()))

    media_subsidio = df_linha.resample("M")['subsidio'].sum().mean()
    media_subsidio = format_number(float(media_subsidio))
    criar_container_estilizado("Média Mensal", media_mes, media_subsidio)

    #col2.metric(label="Média Mensal", value= f"R$ {format_number(media_mes)}")

#---------------------------------- Card 3 - Média Semanal ------------------------------------#
with col3:
    media_semana = df_linha.resample('W')['valor_pago'].sum()
    media_semana = format_number(media_semana.mean())

    media_semana_subsidio = df_linha.resample('W')['subsidio'].sum()
    media_semana_subsidio = format_number(media_semana_subsidio.mean())

    criar_container_estilizado("Média Semanal", media_semana, media_semana_subsidio)
    #col3.metric(label="Média Semanal", value=f"R$ {media_semana}")

#---------------------------------- Card 4 - Média Diária ------------------------------------#
with col4:

    media_diaria = df_linha.resample('D')['valor_pago'].sum()
    media_diaria = format_number(media_diaria.mean())
    media_dia_subsidio = df_linha.resample('D')['subsidio'].sum()
    media_dia_subsidio = format_number(media_dia_subsidio.mean())
    
    criar_container_estilizado("Média Diária", media_diaria, media_dia_subsidio)
    #col4.metric(label="Média Diária", value=f"R$ {media_diaria}")


    style_metric_cards()

# ------------------------------ FIGURAS MOSTRANDO A SÉRIE HISTÓRICA ------------------------- #
# Série histórica (mensal) - Total pago

col1, col2 = st.columns(2, gap='large')
altura = 400 # Altura dos gráficos.
largura=600
largura2=550

with col1:
    st.text("Valor pago (R$)")
    tab1, tab2, tab3, tab4 = st.tabs(["Mensal", "Semanal", "Diário", "Custo da tarifa"])

    with tab1:
        serie_mes = df_linha.resample('M')['valor_pago'].sum().reset_index()
        serie_mes.rename(columns={'data_hora':'Data', 'valor_pago':'Valor pago'}, inplace=True)
        
        subsidio_serie = df_linha.resample('M')['subsidio'].sum().reset_index()
        subsidio_serie.rename(columns={'data_hora':'Data', 'subsidio':'Subsídio (R$)'}, inplace=True)
        

        fig = px.line()

        fig.add_scatter(x=serie_mes['Data'], y=serie_mes['Valor pago'], name='Valor pago', line=dict(color='#3366CC'))
        fig.add_scatter(x=subsidio_serie['Data'], y=subsidio_serie['Subsídio (R$)'], name='Subsídio')
        
        fig.update_layout({'margin':{'l':0, 'r':10 , 't':10, 'b':0}}, height=altura, width=largura)
        fig.update_xaxes(title='', linewidth=1, linecolor='black')
        fig.update_yaxes(title='Valor (R$)', linewidth=1, linecolor='black')
        fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
        
        st.plotly_chart(fig, config=config)

        # """ 
        # fig_serie_mes = px.line(serie_mes, x = 'Data', y = 'Valor pago')
        # fig_serie_mes.update_layout({'margin':{'l':0, 'r':10 , 't':10, 'b':0}}, height=altura, width=largura)
        # fig_serie_mes.update_xaxes(title='', linewidth=1, linecolor='black')
        # fig_serie_mes.update_yaxes(title='Valor Pago (R$)', linewidth=1, linecolor='black')
        # fig_serie_mes.update_traces(mode='lines+markers', marker=dict(size=8, symbol='circle'))
        # st.plotly_chart(fig_serie_mes, config=config)
        # """
    
    with tab2:
        serie_semana = df_linha.groupby('dia').resample('W')[['valor_pago', 'subsidio']].sum().reset_index(names=['dia_i', 'data_h']).groupby('dia_i').mean()['valor_pago']
        nomes_dias = {0:'Seg', 1:'Ter', 2:'Qua', 3:'Qui', 4:'Sex', 5:'Sab', 6: 'Dom'}
        serie_semana.index = serie_semana.index.map(nomes_dias)
        serie_semana = serie_semana.reset_index()
        texto = (serie_semana['valor_pago'] / serie_semana['valor_pago'].sum()).values
        serie_semana['Proporção'] = texto*100
        serie_semana['Proporção'] = (serie_semana['Proporção'].astype(float)).round(2)
        serie_semana.rename(columns={'valor_pago':'Valor Pago', 'dia_i':'Dia'}, inplace=True)
        fig_serie_semana = px.bar(serie_semana, x = 'Dia', y = 'Valor Pago',  text='Proporção')
        fig_serie_semana.update_layout({'margin':{'l':0, 'r':10 , 't':10, 'b':0}}, height=altura, width=largura)
        fig_serie_semana.update_xaxes(title='', linewidth=1, linecolor='black')
        fig_serie_semana.update_yaxes(title='Valor Pago (R$)', linewidth=1, linecolor='black')
        fig_serie_semana.update_traces(texttemplate='%{text:.2f}%', textposition='outside')

        st.plotly_chart(fig_serie_semana, config=config)
    
    with tab3:
        serie_dia = df_linha.resample('D')['valor_pago'].sum().reset_index()
        serie_dia.rename(columns={'data_hora':'Data', 'valor_pago':'Valor pago'}, inplace=True)
        fig_serie_dia = px.line(serie_dia, x = 'Data', y = 'Valor pago')
        fig_serie_dia.update_layout({'margin':{'l':0, 'r':10 , 't':10, 'b':0}}, height=altura, width=largura)
        fig_serie_dia.update_xaxes(title='', linewidth=1, linecolor='black')
        fig_serie_dia.update_yaxes(title='Valor Pago (R$)', linewidth=1, linecolor='black')
        st.plotly_chart(fig_serie_dia, config=config)

    
    with tab4:
        valor_tarifa = df_linha.resample('W')['valor_pago'].max().reset_index()
        valor_tarifa.rename(columns={"data_hora":"Data", "valor_pago":"Valor Pago (R$)"}, inplace=True)
        fig_preco = px.line(valor_tarifa, x = 'Data', y = 'Valor Pago (R$)')
        fig_preco.update_layout({'margin':{'l':0, 'r':10 , 't':10, 'b':0}}, height=altura, width=largura)
        fig_preco.update_xaxes(title='', linewidth=1, linecolor='black')
        fig_preco.update_yaxes(title='Valor Pago (R$)', linewidth=1, linecolor='black')
        fig_preco.update_traces(mode='lines+markers', marker=dict(size=8, symbol='circle'))
        st.plotly_chart(fig_preco, config=config)
        
        
with col2:
    st.text("Valor Subsídio (R$)")
    tab1, tab2, tab3 = st.tabs(["Subsídio x Total de Passageiros",'Ranking',"Composição"])

    with tab1: # Gráfico mostrando relação subsidio x total passageiros
        tota_linha = df_empresa.groupby('linha')['valor_pago'].sum()
        total_sub = df_empresa.groupby('linha')['subsidio'].sum()
        total_pass = df_empresa.groupby('linha')['integracao'].size()

        merged_df = pd.merge(tota_linha, total_sub, left_index=True, right_index=True)
        merged_df = pd.merge(merged_df, total_pass, left_index=True, right_index=True)
        
        merged_df.rename(columns={'integracao':'Total de Passageiros'}, inplace=True)
        
        merged_df['valor_pago'] = merged_df['valor_pago'].astype(float)
        merged_df['subsidio'] = merged_df['subsidio'].astype(float)
        merged_df['hover_info'] = "Linha " + merged_df.index.astype(str)

        fig = px.scatter(merged_df, x="Total de Passageiros", y="valor_pago", hover_name='hover_info', 
                         size="subsidio", log_y=True, log_x=True, size_max=60, color="subsidio", 
                         color_continuous_scale="Viridis", labels={'valor_pago':'Valor Pago (R$) '})
        
        fig_serie_semana.update_traces(textposition='outside')
        fig.update_layout({'margin':{'l':10, 'r':0 , 't':10, 'b':0}}, height=altura, width=largura2)
        st.plotly_chart(fig, config=config)

    with tab2: # Ranking
        top_10 = df_empresa.groupby('linha')['subsidio'].sum().sort_values(ascending=False).reset_index().iloc[:10,:]
        fig = px.bar(top_10, x ='subsidio', y = np.arange(10), text='subsidio', orientation='h', labels={"y":'Linha'})
        
        fig.update_layout({'margin':{'l':80, 'r':0 , 't':50, 'b':0}}, width=largura2, height=altura, 
                            title=dict(text='Ranking - Subsídio por linha', x=0.35, font_size=15, font_family='Arial'),
                            )  
        fig.update_xaxes(title='Subsídio (R$)', linewidth=1, linecolor='black')
        fig.update_yaxes(title='Linha', linewidth=1, linecolor='black', tickvals=np.arange(10), ticktext=top_10['linha'])
        fig.update_traces(texttemplate='%{text:.0f}', textposition='auto')
        st.plotly_chart(fig, config=config)


    with tab3: # Gráfico de pizza (composição)
        total_pago = df_linha['valor_pago'].sum()
        total_subsidio = df_linha['subsidio'].sum()
        renda = [total_pago, total_subsidio]

        fig_nova = px.pie(names=['Valor Pago', 'Subsídio'], values=renda, labels={'values':'R$'})
        fig_nova.update_layout({'margin':{'l':50, 'r':0 , 't':10, 'b':0}}, height=400, width=400)
        st.plotly_chart(fig_nova, config=config)

    # with tab4: # Subsídio po mês
    #     subsidio_serie = df_linha.resample('M')['subsidio'].sum().reset_index()
    #     subsidio_serie.rename(columns={'data_hora':'Data', 'subsidio':'Subsídio (R$)'}, inplace=True)
    #     media_sub = subsidio_serie['Subsídio (R$)'].mean()
    #     fig_subsidio = px.line(subsidio_serie, x = 'Data', y = 'Subsídio (R$)')
    #     fig_subsidio.update_layout({'margin':{'l':10, 'r':0 , 't':10, 'b':0}}, height=altura, width=largura2)
    #     fig_subsidio.update_xaxes(title='', linewidth=1, linecolor='black')
    #     fig_subsidio.update_yaxes(linewidth=1, linecolor='black')
    #     fig_subsidio.update_traces(mode='lines+markers', marker=dict(size=8, symbol='circle'))
        
    #     fig_subsidio.add_annotation(
    #     xref='paper',  # Referência do eixo x
    #     yref='paper',  # Referência do eixo y
    #     x=0.02,  # Posição horizontal da caixa de texto em porcentagem do gráfico
    #     y=0.99,  # Posição vertical da caixa de texto em porcentagem do gráfico
    #     text=f'Média mensal: R$ {format_number(media_sub)}',  # Texto da caixa de texto
    #     font=dict(size=16, color='black'),  # Configurações da fonte do texto
    #     showarrow=False,  # Não mostrar seta
    #     bgcolor='#f0f0f0',  # Cor de fundo da caixa de texto
    #     bordercolor='black',  # Cor da borda da caixa de texto
    #     borderwidth=1,  # Largura da borda da caixa de texto
    #     borderpad=5,  # Espaçamento entre o texto e a borda da caixa de text
    #     )
        
    #     st.plotly_chart(fig_subsidio, config=config)

    
        
    

