import pandas as pd
import numpy as np
import streamlit as st
import psycopg2
from streamlit_extras.stylable_container import stylable_container

def criar_container_estilizado(texto, valor_arrecadado, valor_subsidio):
    # Conteúdo do container com múltiplas linhas
    conteudo_container = f"""
    <div style="font-size: 1.1em; line-height: 1.2;">
        <span style="font-size: 1.05em; font-weight: bold; margin-bottom: 0.5em; display: block;">{texto}</span>
        <span style="font-size: 0.9em;">Valor Pago: R$ {valor_arrecadado}</span><br>
        <span style="font-size: 0.9em;">Subsídio: R$ {valor_subsidio}</span>
    </div>
    """

    # Exibir o container estilizado com borda e texto em múltiplas linhas
    with stylable_container(
        key="container_with_border",
        css_styles="""
        {
            border-top: 1px solid rgba(49, 51, 63, 0.2);
            border-right: 1px solid rgba(49, 51, 63, 0.2);
            border-bottom: 1px solid rgba(49, 51, 63, 0.2);
            border-left: 10px solid #ADD8E6; /* Largura e cor da borda esquerda */
            border-radius: 0.5rem;
            padding: calc(1em - 1px);
            padding-bottom: 2em; /* Aumenta o espaço interno na parte inferior */
        }
        """,
    ):
        return st.write(conteudo_container, unsafe_allow_html=True)

def fluxo_mensal(df):
  df_mensal = df.resample('M').count()
  df_mensal['mes'] = df_mensal.index.month
  df_mensal['Período'] = df_mensal.index.strftime('%b %Y')
  df_mensal = df_mensal.reset_index(drop=True).iloc[:,[0,-1]].rename(columns={'linha':'N° de passageiros'})
  return df_mensal

def media_semanal(df):

  nomes_dias = {0:'Seg', 1:'Ter', 2:'Qua', 3:'Qui', 4:'Sex', 5:'Sab', 6: 'Dom'}
  media_dia = df.groupby('dia').resample('W').count().reset_index(names=['dia_i', 'data_h']).groupby('dia_i').mean()['linha']

  media_dia.index = media_dia.index.map(nomes_dias)

  media_dia = media_dia.round(2)
  texto = ((media_dia / media_dia.sum()) * 100).round(2).values
  df_semanal = pd.DataFrame({'Total de passageiros':media_dia, 'Proporção':texto}).reset_index(names=['Dia'])

  return df_semanal

def media_hora(df):
    total_dia = df.resample('D').count()['hora']
    df_horario_dia = df.resample('H').count()
    df_horario_dia['proporcao'] = df_horario_dia['hora'] / total_dia[df_horario_dia.index.date].values
    
    prop = (df_horario_dia['proporcao'].groupby(df_horario_dia.index.hour).mean() * 100).round(2)
    qtd = df_horario_dia['linha'].groupby(df_horario_dia.index.hour).mean().round()
    
    df_media_hora = pd.DataFrame({'N° de passageiros':qtd, 'Proporção':prop}).reset_index(names=['Hora'])

    return df_media_hora

def converter_tempo(horas_float):
    # Extrair a parte inteira das horas (parte dos minutos)
    horas_int = int(horas_float)
    
    # Calcular os minutos restantes
    minutos_rest = int((horas_float - horas_int) * 60)

    if horas_int == 0:
        return f"{minutos_rest} min"
    
    else:
        # Retornar o tempo formatado como horas e minutos
        return f"{horas_int}h {minutos_rest} min"

def func_tempo_viagem(df):
  tempo_viagem = (df['tempo_viagem'].dt.total_seconds()/3600).resample("D").mean()
  tempo_viagem = tempo_viagem.reset_index()
  tempo_viagem.rename(columns={'tempo_viagem': 'tempo (h)', 'data_hora':'data'}, inplace=True)
  tempo_viagem['tempo (h)'] = tempo_viagem['tempo (h)'].round(2)
  return tempo_viagem

def format_number(number):
    if abs(number) >= 1e6:
        return '{:.2f}M'.format(number / 1e6)
    elif abs(number) >= 1e3:
        return '{:.2f}k'.format(number / 1e3)
    else:
        return str(round(number))

def leitura_de_dados(empresa_selecionada, cursor):
    chave_unica = f"{empresa_selecionada}"
    
    if not 'dados' in st.session_state or st.session_state.get('chave_unica') != chave_unica:

      cursor.execute(f'SELECT * FROM dados_passageiros WHERE empresa_codigo = {empresa_selecionada}')
      conj_dados = cursor.fetchall()
      colunas = []

      for col in cursor.description:
          colunas.append(col[0])

      df_empresa = pd.DataFrame(data=conj_dados, columns=colunas)
      df_empresa.set_index('data_hora', inplace=True)
  
      st.session_state['dados'] = df_empresa
      st.session_state['chave_unica'] = chave_unica

    else:
        # Se os dados já estiverem na sessão, reutilizá-los
        df_empresa = st.session_state['dados']

    return df_empresa, chave_unica