import pandas as pd
import streamlit as st 
import helpers.demonstrativos as demo 
import helpers.criarGraficos as graf
import numpy as np


def cria_coluna_mes_ano(df, ordem=True):
    # Separa a coluna periodo
    df[['TRIMESTRE','ANO']] = df['PERIODO'].str.split("T", expand = True)
    df['TRIMESTRE'] = df['TRIMESTRE'].str.strip()
    df['ANO'] = df['ANO'].str.strip()
    df = df.sort_values(by=["ANO", "TRIMESTRE"], ascending=ordem )

    return df


# @st.cache_data
def calcular_analise_vertical_trimestral_patrimonio(df, ano_inicio, ano_fim):
    # Filtra os valores para o período selecionado
    df = df.loc[(df["ANO"] >= ano_inicio) & (df["ANO"] <= ano_fim)]    
    
    # Altera a estrutura dos dados
    df_pivot = df.pivot_table(index=['CONTA', 'DESCRIÇÃO'], columns='PERIODO', values='VALOR', observed=False).reset_index()

    # Classifique os trimestres de forma personalizada
    trimestres_ordenados = ["4", "3", "2", "1"]
    anos = [str(ano) for ano in range(ano_fim, ano_inicio - 1, -1)]
    trimestres_ordenados = [f"{tri}T{ano}" for ano in anos for tri in trimestres_ordenados]

    # Ordena as colunas de período
    ordered_columns = ['CONTA', 'DESCRIÇÃO'] + trimestres_ordenados
    df_pivot = df_pivot[ordered_columns]

    # Remove o nome da coluna índice
    df_pivot.columns.name = None

    # Colunas a serem calculadas
    colunas = df_pivot.columns[2:]

    # DataFrame para armazenar os resultados da AV
    df_av = pd.DataFrame()
    df_graf_av = pd.DataFrame()

    # Calcula os valores da análise vertical
    for coluna in colunas:
        # Preencher valores nulos com zero
        df_pivot[coluna] = df_pivot[coluna].fillna(0)
        
        # Adiciona a coluna original
        df_av[f"{coluna}"] = df_pivot[coluna]

        # Calcula o AV evitando divisão por zero
        if df_pivot[coluna][0] != 0:
            av_calculado = round((df_pivot[coluna] / df_pivot[coluna][0]) * 100, 2)
        else:
            av_calculado = [0] * len(df_pivot[coluna])

        # Adiciona a coluna calculada
        df_av[f"{coluna} %"] = av_calculado
        df_graf_av[f"{coluna} %"] = av_calculado

    # Adiciona a coluna DESCRIÇÃO de volta ao DataFrame
    df_av['DESCRIÇÃO'] = df_pivot['DESCRIÇÃO']
    df_graf_av['DESCRIÇÃO'] = df_pivot['DESCRIÇÃO']

    # Reorganiza as colunas
    colunas_ordenadas = ['DESCRIÇÃO'] + list(df_av.columns[:-1])
    df_av = df_av[colunas_ordenadas]
    
    # Converte valores nulos para zero
    df_av = demo.converte_zero(df_av)

    return df_av
# @st.cache_data
def calcular_analise_vertical_trimestral_resultado(df, ano_inicio, ano_fim):
    # Filtra os valores para o período selecionado
    df = df.loc[(df["ANO"] >= ano_inicio) & (df["ANO"] <= ano_fim)]
      
    # Altera a estrutura dos dados
    df = df.pivot_table(index=['CONTA', 'DESCRIÇÃO'], columns='PERIODO', values='VALOR', observed=False).reset_index()

    # Classifique os trimestres de forma personalizada
    trimestres_ordenados = ["4", "3", "2", "1"]
    anos = [str(ano) for ano in range(ano_fim, ano_inicio - 1, -1)]
    trimestres_ordenados = [f"{tri}T{ano}" for ano in anos for tri in trimestres_ordenados]

    # Ordena as colunas de período
    ordered_columns = ['CONTA', 'DESCRIÇÃO'] + trimestres_ordenados
    df = df[ordered_columns]

    # Remove o nome da coluna índice
    df.columns.name = None

    # Colunas a serem calculadas
    colunas = df.columns[2:]

    # DataFrame para armazenar os resultados da AV
    df_av = pd.DataFrame()
    df_graf_av = pd.DataFrame()

    # Calcula os valores da análise vertical
    for coluna in colunas:
        # Preencher valores nulos com zero
        df[coluna] = df[coluna].fillna(0)

        # Adiciona a coluna original
        df_av[f"{coluna}"] = df[coluna]

        # Calcula o AV evitando divisão por zero
        if df[coluna][0] != 0:
            av_calculado = round((df[coluna] / df[coluna][0]) * 100, 2)
        else:
            av_calculado = [0] * len(df[coluna])

        # Adiciona a coluna calculada
        df_av[f"{coluna} %"] = av_calculado
        df_graf_av[f"{coluna} %"] = av_calculado

    # Adiciona a coluna DESCRIÇÃO de volta ao DataFrame
    df_av['DESCRIÇÃO'] = df['DESCRIÇÃO']
    df_graf_av['DESCRIÇÃO'] = df['DESCRIÇÃO']

    # Reorganiza as colunas
    colunas_ordenadas = ['DESCRIÇÃO'] + list(df_av.columns[:-1])
    df_av = df_av[colunas_ordenadas]

    df_graf_av = df_graf_av.melt(id_vars='DESCRIÇÃO', var_name='PERIODO', value_name='VALORES')
    
    df_resul_bruto = df_graf_av[
        (df_graf_av["DESCRIÇÃO"] == "Resultado Bruto") |
        (df_graf_av["DESCRIÇÃO"] == "Resultado Antes do Resultado Financeiro e dos Tributos")]
    
    df_resul_bruto = df_resul_bruto.pivot_table(index='PERIODO',
                                                columns='DESCRIÇÃO',
                                                values='VALORES').reset_index()
    
    df_resul_bruto = cria_coluna_mes_ano(df_resul_bruto)
    return df_av, df_resul_bruto

# @st.cache_data
def calcular_analise_vertical_anual(df, ano_inicio, ano_fim):

    # Filtra os valores para o período selecionado
    df = df.loc[(df["ANO"] >= ano_inicio) & (df["ANO"] <= ano_fim)]
    
    # Executa a função de ordenar os dados
    df = demo.ordenar_dataframe(df, ano_inicio, ano_fim)
    df.reset_index(inplace=True)

    df_pivot = df.pivot_table(index=['CONTA', 'DESCRIÇÃO'], columns='ANO', values='VALOR', observed=False).reset_index()

    # Remove o nome da coluna índice
    df_pivot.columns.name = None

    # Colunas a serem calculadas
    colunas = list(df_pivot.columns[2:])    

    # DataFrame para armazenar os resultados da AV
    df_av = pd.DataFrame()
    df_graf_av = pd.DataFrame()

    for coluna in colunas[::-1]:
        # Verifica se a coluna tem valores válidos e substitui valores nulos por zero
        df_pivot[coluna] = df_pivot[coluna].fillna(0)

        # Adicione a coluna original
        df_av[f"{coluna}"] = df_pivot[coluna]

        # Verifica se o valor base (primeira linha) não é zero para evitar divisão por zero
        if df_pivot[coluna][0] != 0:
            av_calculado = round((df_pivot[coluna] / df_pivot[coluna][0]) * 100, 2)
        else:
            # Se o valor base for zero, define o AV como zero
            av_calculado = [0] * len(df_pivot[coluna])

        # Adicione a coluna calculada
        df_av[f"{coluna} %"] = av_calculado
        
        # Cria DataFrame apenas com colunas calculadas
        df_graf_av[f"{coluna} %"] = av_calculado
        
    # Adicione a coluna 'DESCRIÇÃO' de volta ao DataFrame
    df_av['DESCRIÇÃO'] = df['DESCRIÇÃO']
    df_graf_av['DESCRIÇÃO'] = df_pivot['DESCRIÇÃO']

    # Reorganize as colunas
    colunas_ordenadas = ['DESCRIÇÃO'] + list(df_av.columns[:-1])
    df_av = df_av[colunas_ordenadas]  

    df_graf_av = df_graf_av.melt(id_vars='DESCRIÇÃO', var_name='PERIODO', value_name='VALORES')
    
    resul_bruto = df_graf_av[
        (df_graf_av["DESCRIÇÃO"] == "Resultado Bruto") |
        (df_graf_av["DESCRIÇÃO"] == "Resultado Antes do Resultado Financeiro e dos Tributos")]
    
    resul_bruto = resul_bruto.pivot_table(index='PERIODO',
                                          columns='DESCRIÇÃO',
                                          values='VALORES').reset_index()

    # Converte valores nulos para zero antes de retornar o DataFrame final
    df_av = demo.converte_zero(df_av) 

    return df_av, resul_bruto

# @st.cache_data
def calcular_analise_horizontal_trimestral(df, ano_inicio, ano_fim):

    # Ano anterior para cálculo AH
    ano_anterior_calculado = ano_inicio - 1   
    
    # Filtra os valores para o período selecionado
    df = df.loc[(df["ANO"] >= ano_anterior_calculado) & (df["ANO"] <= ano_fim)]

    # Pivot tabela - dataframe
    df = df.pivot_table(index=['CONTA', 'DESCRIÇÃO'], columns='PERIODO', values='VALOR', observed=False).reset_index()

    # Classifique os trimestres de forma personalizada
    trimestres_ordenados = ["4", "3", "2", "1"]
    anos = [str(ano) for ano in range(ano_fim, ano_anterior_calculado - 1, -1)]
    trimestres_ordenados = [f"{tri}T{ano}" for ano in anos for tri in trimestres_ordenados]

    # Ordena as colunas de período
    ordered_columns = ['CONTA', 'DESCRIÇÃO'] + trimestres_ordenados
    df = df[ordered_columns]

    # Filtra as colunas para criar novo DataFrame   
    colunas = df.columns[2:]  # Especifica as colunas a serem consideradas 

    # DataFrame para armazenar os resultados da AH
    df_ah = pd.DataFrame()

    # Calcula os valores da análise horizontal
    for i in range(1, len(colunas)):
        coluna_atual = colunas[i]
        coluna_anterior = colunas[i - 1]

        # Preencher valores nulos com zero
        df[coluna_atual] = df[coluna_atual].fillna(0)
        df[coluna_anterior] = df[coluna_anterior].fillna(0)

        # Adiciona a coluna original apenas uma vez
        if f"{coluna_anterior}" not in df_ah.columns:
            df_ah[f"{coluna_anterior}"] = df[coluna_anterior]

        # Calcula o AH evitando divisão por zero
        with np.errstate(divide='ignore', invalid='ignore'):
            ah_calculado = np.where(df[coluna_atual] != 0,
                                    round(((df[coluna_anterior] / df[coluna_atual]) - 1) * 100, 2),
                                    0)
        df_ah[f'{coluna_anterior} %'] = ah_calculado

    # Adiciona a coluna DESCRIÇÃO de volta ao DataFrame
    df_ah['DESCRIÇÃO'] = df['DESCRIÇÃO']

    # Reorganiza as colunas
    colunas_ordenadas = ['DESCRIÇÃO'] + list(df_ah.columns[:-2])
    df_ah = df_ah[colunas_ordenadas]

    # Converte os valores ausentes para zero
    df_ah = demo.converte_zero(df_ah)

    # Filtra de colunas exibidas AH - DataFrame
    df_ah = df_ah.iloc[:, :-6] 
    
    return df_ah

# @st.cache_data
def calcular_analise_horizontal_anual(df, ano_inicio, ano_fim):
    # Ano anterior para cálculo AH
    ano_anterior_calculado = ano_inicio - 1   

    # Filtra os valores para o período selecionado
    df = df.loc[(df["ANO"] >= ano_anterior_calculado) & (df["ANO"] <= ano_fim)]

    # Executa a função de ordenar os dados
    df = demo.ordenar_dataframe(df, ano_anterior_calculado, ano_fim)

    # Pivot tabela - DataFrame
    df = df.pivot_table(index=['CONTA', 'DESCRIÇÃO'], columns='ANO', values='VALOR', observed=False)
    df.reset_index(inplace=True)

    # Filtra as colunas para criar novo DataFrame
    colunas = df.columns[2:].sort_values(ascending=False)

    # DataFrame para armazenar os resultados da AH
    df_ah = pd.DataFrame()

    # Calcula os valores da análise horizontal
    for i in range(1, len(colunas)):
        coluna_atual = colunas[i]
        coluna_anterior = colunas[i - 1]

        # Adiciona a coluna original apenas uma vez
        if f"{coluna_anterior}" not in df_ah.columns:
            df_ah[f"{coluna_anterior}"] = df[coluna_anterior]

        # Calcula o AH
        df_ah[f'{coluna_anterior} %'] = round(((df[coluna_anterior] / df[coluna_atual]) - 1) * 100, 2)

    # Adiciona a coluna DESCRIÇÃO de volta ao DataFrame
    df_ah['DESCRIÇÃO'] = df['DESCRIÇÃO']
    df_ah['CONTA'] = df['CONTA']

    # Reorganiza as colunas
    colunas_ordenadas = ['CONTA'] + ['DESCRIÇÃO'] + list(df_ah.columns[:-2])

    # Ordena as colunas
    df_ah = df_ah[colunas_ordenadas]

    # Converte os valores ausentes para zero
    df_ah = demo.converte_zero(df_ah)

    # Deleta as linhas com valores iguais a zero
    df_ah = df_ah.drop(columns=['CONTA'])

    return df_ah

# @st.cache_data
def calcular_analise_horizontal_receita_liquida_trimestral(df, ano_inicio, ano_fim):
# Ano anterior para calculo AH
    ano_anterior_calculado = ano_inicio - 1   
    
    # Filtra os valores para periodo selecionado
    df = df.loc[(df["ANO"] >= ano_anterior_calculado) & (df["ANO"] <= ano_fim )]
 
    # Pivot tabela - dataframe
    df = df.pivot_table(index=['CONTA', 'DESCRIÇÃO'], columns='PERIODO', values='VALOR', observed=False).reset_index()

    # Classifique os trimestres de forma personalizada
    trimestres_ordenados = ["4", "3", "2", "1"]
    anos = [str(ano) for ano in range(ano_fim , ano_anterior_calculado - 1, -1)]
    trimestres_ordenados = [f"{tri}T{ano}" for ano in anos for tri in trimestres_ordenados]

    # Ordena as colunas de período
    ordered_columns = ['CONTA','DESCRIÇÃO'] + trimestres_ordenados
    df = df[ordered_columns]

    # Filtra as colunas para criar novo dataframe   
    colunas = df.columns[2:] # Especifica as colunas a serem consideradas 

    # DataFrame para armazenar os resultados da AH
    df_ah = pd.DataFrame()

     # Calcula os valores da analise horizontal
    for i in range(1, len(colunas)):
        coluna_atual = colunas[i]
        coluna_anterior = colunas[i - 1]

        # Adicione a coluna original apenas uma vez
        if f"{coluna_anterior}" not in df_ah.columns:
            df_ah[f"{coluna_anterior}"] = df[coluna_anterior]      

        df_ah[f'{coluna_anterior}'] = round(((df[coluna_anterior] / df[coluna_atual]) - 1) * 100, 2)

    
    # Reorganize as colunas
    colunas_ordenadas =   ['DESCRIÇÃO']  + df_ah.columns[:-3][::-1].tolist()

    # Adicione a coluna DESCRIÇÃO de volta ao DataFrame
    df_ah['DESCRIÇÃO'] = df['DESCRIÇÃO']

    # Ordena as colunas
    df_ah = df_ah[colunas_ordenadas]

    # Converte os valores ausentes para zero
    # df_ah = demo.converte_zero(df_ah)        

    # # Filtra valor do resultado operacional
    res_operacional = df_ah.head(1)
    # Altera a estrutura dos dados
    df_transposed = res_operacional.set_index('DESCRIÇÃO').T
    df_transposed.reset_index(inplace=True)
    
    # Remove o nome da coluna indice
    df_transposed.columns.name = None 

    # Altera o nome das colunas
    df_transposed.columns = ['PERIODO', 'AH %  Receita Líquida']
    return df_transposed

# @st.cache_data
def calcular_analise_horizontal_receita_liquida_anual(df,ano_inicio, ano_fim):    

    # Filtra os valores para periodo selecionado
    # df = df.loc[(df["ANO"] >= ano_anterior_calculado) & (df["ANO"] <= ano_fim )]

    # Executa a função de ordenar os dados
    df = demo.ordenar_dataframe(df,ano_inicio, ano_fim)

    # Altera a estrutura dos dados
    df = df.pivot_table(index=['CONTA', 'DESCRIÇÃO'], columns='ANO', values='VALOR', observed=False).reset_index()
    # Filtra as colunas que serão usadas para o calculo de AH 
    colunas = df.columns[2:].sort_values(ascending=False) # Especifica as colunas a serem consideradas 

    # Cria um dataFrame para armazenar os resultados da AV
    df_ah = pd.DataFrame()

    # Realiza o calculo de AH
    for i in range(1, len(colunas)):
        coluna_atual = colunas[i]
        coluna_anterior = colunas[i - 1]
        # Calcula o AH para a coluna atual e anterior
        df_ah[f'{coluna_anterior}'] = round(((df[coluna_anterior] / df[coluna_atual]) - 1) * 100, 2)

    # Adicione a coluna CONTA de volta ao DataFrame
    df_ah['DESCRIÇÃO'] = df['DESCRIÇÃO'] 
    df_ah['CONTA'] = df['CONTA'] 

    # Reorganize as colunas
    colunas_ordenadas =  ['CONTA'] + ['DESCRIÇÃO']  + list(df_ah.columns[:-2])
    df_ah = df_ah.loc[:, colunas_ordenadas]

    # Deleta a coluna conta
    df_ah = df_ah.drop(columns=['CONTA'])             

    # Filtra valor do resultado operacional
    resultado_operacional = df_ah.head(1)

    # MELT - mudando a estrutura dos dados para gráfico de linhas
    resultado_operacional = resultado_operacional.melt(id_vars='DESCRIÇÃO', 
                                                       var_name='ANO',
                                                       value_name='VALORES')

    # Altera a estrutura do dataframe para o gráfico
    resultado_operacional = resultado_operacional.pivot_table(index='ANO', 
                                                              columns='DESCRIÇÃO',
                                                              values='VALORES').reset_index()  
  
    # Remove o nome da coluna indice
    resultado_operacional.columns.name = None

    # # Altera o nome das colunas
    resultado_operacional.columns = ['PERIODO', 'AH %  Receita Líquida']
    return resultado_operacional

