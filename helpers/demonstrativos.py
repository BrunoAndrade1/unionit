import pandas as pd
import streamlit as st

# @st.cache_data
def ordenar_dataframe(df, inicio, fim):
    # Lista de anos únicos no DataFrame
    # anos = list(df["ANO"].unique())

    # Classifique os trimestres de forma personalizada
    trimestres_ordenados = ["4", "3", "2", "1"]
    anos = [str(ano) for ano in range(fim + 1, inicio - 1, -1)]
    trimestres_ordenados = [f"{tri}T{ano}" for ano in anos for tri in trimestres_ordenados]

    # Ordenar colunas por PERIODO
    df.loc[:,'PERIODO'] = pd.Categorical(df.loc[:,'PERIODO'], categories=trimestres_ordenados, ordered=True)
    df = df.sort_values('PERIODO')
    return df 

@st.cache_data
def ler_data():
    # Ler arquivo csv
    # df = load_data("equatorial_final.csv")
    df = st.session_state['data']
    pd.to_numeric(df["VALOR"])   
    pd.to_datetime(df["ANO"]) 
    df = df[(df["DEMONSTRATIVO"] == "Balanço Patrimonial Ativo") | (df["DEMONSTRATIVO"] == "Balanço Patrimonial Passivo")]
    return df

@st.cache_data
def cria_dataframe_trimestral_bp(df, ano_inicio, ano_fim):
    # Filtro ano
    df = df[(df["ANO"] >= ano_inicio) & (df["ANO"] <= ano_fim)]
    
    # Cria a pivot table
    df = df.pivot_table(index=['CONTA', 'DESCRIÇÃO'], columns='PERIODO', values='VALOR').reset_index()

    # Classifique os trimestres de forma personalizada
    trimestres_ordenados = ["4", "3", "2", "1"]
    anos = [str(ano) for ano in range(ano_fim , ano_inicio - 1, -1)]
    trimestres_ordenados = [f"{tri}T{ano}" for ano in anos for tri in trimestres_ordenados]

    # Ordena as colunas de período
    ordered_columns = ['DESCRIÇÃO'] + trimestres_ordenados
    df = df[ordered_columns]

    # Remove o nome da coluna indice
    df.columns.name = None         
    return df   

@st.cache_data
def cria_dataframe_anual_bp(df, ano_inicio, ano_fim):
    # Filtro ano
    df = df[(df["ANO"] >= ano_inicio) & (df["ANO"] <= ano_fim)]

    # Pivot tabela - dataframe
    df = df.pivot_table(index=['CONTA', 'DESCRIÇÃO'], columns='ANO', values='VALOR').reset_index()
    
    # Ordena as colunas de período
    ordered_columns = ['DESCRIÇÃO'] + sorted([col for col in df.columns if col not in ['CONTA', 'DESCRIÇÃO']], reverse=True)
    df = df[ordered_columns]

    # Remove o nome da coluna indice
    df.columns.name = None
    
    # Converte none para "0" e deleta linhas com todos os valores iguais a "0"
    df = converte_zero(df)   
    return df   

@st.cache_data
def cria_dataframe_trimestral_dre(df, ano_inicio, ano_fim):
    # Filtro ano
    df = df[(df["ANO"] >= ano_inicio) & (df["ANO"] <= ano_fim)]
    
    # Cria a pivot table
    df = df.pivot_table(index=['CONTA', 'DESCRIÇÃO'], columns='PERIODO', values='VALOR').reset_index()

    # Classifique os trimestres de forma personalizada
    trimestres_ordenados = ["4", "3", "2", "1"]
    anos = [str(ano) for ano in range(ano_fim , ano_inicio - 1, -1)]
    trimestres_ordenados = [f"{tri}T{ano}" for ano in anos for tri in trimestres_ordenados]

    # Ordena as colunas de período
    ordered_columns = ['DESCRIÇÃO'] + trimestres_ordenados
    df = df[ordered_columns]

    # Remove o nome da coluna indice
    df.columns.name = None         
    return df   

@st.cache_data
def cria_dataframe_anual_dre(df, ano_inicio, ano_fim):
    # Filtro ano
    df = df[(df["ANO"] >= ano_inicio) & (df["ANO"] <= ano_fim)]

    # Pivot tabela - dataframe
    df = df.pivot_table(index=['CONTA', 'DESCRIÇÃO'], columns='ANO', values='VALOR').reset_index()
    
    # Ordena as colunas de período
    ordered_columns = ['DESCRIÇÃO'] + sorted([col for col in df.columns if col not in ['CONTA', 'DESCRIÇÃO']], reverse=True)
    df = df[ordered_columns]

    # Remove o nome da coluna indice
    df.columns.name = None
    
    # Converte none para "0" e deleta linhas com todos os valores iguais a "0"
    df = converte_zero(df)   
    return df   

@st.cache_data
def converte_zero(df):# Converte none para "0" e deleta linhas com todos os valores iguais a "0"
    df = df.fillna(0)
    linha_todos_zeros = (df == 0).all(axis=1)
    df = df.loc[~linha_todos_zeros]
    return df 

