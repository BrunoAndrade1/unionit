import pandas as pd
import streamlit as st 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


import helpers.demonstrativos as demo 
import helpers.analises as anls
import helpers.dadoscontabeis as data_contabil


# Função para ordenar o grafico
# @st.cache_data
def ordenar_grafico_linhas_indicadores_trimestral(df, inicio, fim):
    trimestres_ordenados = []
    indices = df["ÍNDICES"].unique()

    for ano in range(inicio, fim + 1):
        for tri in ["1", "2", "3", "4"]:
            for i in indices:
                trimestres_ordenados.append(f"{tri}T{ano}")

    tri_to_int = {tri: idx for idx, tri in enumerate(trimestres_ordenados)}
    # Resetar o índice do DataFrame
    df.reset_index(drop=True, inplace=True)
    
    df['TRIMESTRE'] = df['TRIMESTRE'].map(tri_to_int)
    df = df.drop_duplicates() 
    df = df.sort_values(by='TRIMESTRE')
    # Converte os valores de volta para o formato desejado
    df['TRIMESTRE'] = trimestres_ordenados
    
    return df 

# Função para ordenar o grafico
# @st.cache_data
def ordenar_grafico_chart(df, inicio, fim):
    # Lista de anos únicos no DataFrame
    anos = list(df["ANO"].unique())

    # Classifique os trimestres de forma personalizada - gráficos
    trimestres_ordenados = ["1", "2", "3", "4"]
    anos = [str(ano) for ano in range(inicio, fim + 1)]
    trimestres_ordenados = [f"{tri}T{ano}" for ano in anos for tri in trimestres_ordenados]
    
    # Ordenar colunas por PERIODO - gráficos
    df.loc[:, 'PERIODO'] = pd.Categorical(df['PERIODO'], categories=trimestres_ordenados, ordered=True)

    return df 

# Função para criar o gráfico
# @st.cache_data
def grafico_bp_anual(df, inicio, fim):    
    
    df_ativo, df_ativo_circ, df_ativo_n_circ, df_passivo_circ, df_passivo_n_circ, df_patrimonio_liq, df_passivo = data_contabil.data_bp_anual(df, inicio, fim)

    # Crie subplots com dois eixos y
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Trace 1: Gráfico de Linhas - Ativo
    # Adiciona o gráfico de linhas no eixo primário (y)
    fig.add_trace(
    go.Scatter(
            mode='lines+markers',
            x=df_ativo.iloc[:, 4],
            y=df_ativo.iloc[:, 2],
            name="Ativo",
            marker_color='blue',        
        ),
    )
    # Trace 2: - Passivo
    fig.add_trace(
        go.Scatter(
            mode='lines+markers',
            x=df_passivo.iloc[:,4],
            y=df_passivo.iloc[:,2],
            name="Passivo",
            marker_color='red',          
        )
    )    
    # Trace 3: Gráfico de Barras (Patrimonio líquido)
    fig.add_trace(
        go.Bar(
            x=df_patrimonio_liq.iloc[:, 4],
            y=df_patrimonio_liq.iloc[:, 2],
            name="Patrimonio Líquido",
            marker_color='mediumblue',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=.5
        ),
    ) 
    # Trace 4: Gráfico de Barras (Ativo circulante)
    fig.add_trace(
        go.Bar(                                       
            x=df_ativo_circ.iloc[:, 4],
            y=df_ativo_circ.iloc[:, 2],
            name="Ativo Circulante",
            marker_color='cornflowerblue',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=.7                      
        ),
    )
    # Trace 5: Gráfico de Barras (Ativo não circulante)
    fig.add_trace(
        go.Bar(
            x=df_ativo_n_circ.iloc[:, 4],
            y=df_ativo_n_circ.iloc[:, 2],
            name="Ativo Não Circulantes",
            marker_color='gold',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=.6
        ),
    )
    # Trace 6: Gráfico de Barras (Passivo circulantes)
    fig.add_trace(
        go.Bar(
            x=df_passivo_circ.iloc[:, 4],
            y=df_passivo_circ.iloc[:, 2],
            name="Passivo Circulantes",
            marker_color='green',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=.6
        ),
    )
    # Trace 6: Gráfico de Barras (Passivo não circulantes)
    fig.add_trace(
        go.Bar(
            x=df_passivo_n_circ.iloc[:, 4],
            y=df_passivo_n_circ.iloc[:, 2],
            name="Passivo Não Circulantes",
            marker_color='crimson',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=.8
        ),
    )    
    # Atualize o layout geral
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.8,
        )
    )
    # Exiba o gráfico
    st.plotly_chart(fig, use_container_width=True)

# Função para criar o gráfico
# @st.cache_data
def grafico_bp_trimestral(df, inicio, fim):    
    
    df_grafico_bp, df_passivo = data_contabil.data_bp_trimestral(df, inicio, fim)
    df_grafico_bp = df_grafico_bp.sort_values(by=['ANO', 'MES'])
    # Filtra os dados
    df_ativo = df_grafico_bp.loc[df_grafico_bp['CONTA'] == '1']
    df_ativo_circ = df_grafico_bp.loc[df_grafico_bp['CONTA'] == '1.01']
    df_ativo_n_circ = df_grafico_bp.loc[df_grafico_bp['CONTA'] == '1.02']

    df_passivo_circ = df_grafico_bp.loc[df_grafico_bp['CONTA'] == '2.01'].sort_values(by=["ANO","MES"])
    df_passivo_n_circ = df_grafico_bp.loc[df_grafico_bp['CONTA'] == '2.02']
    df_patrimonio_liq = df_grafico_bp.loc[df_grafico_bp['CONTA'] == '2.03']

    # Crie subplots com dois eixos y
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Trace 1: Gráfico de Linhas - Ativo
    # Adiciona o gráfico de linhas no eixo primário (y)
    fig.add_trace(
    go.Scatter(
            mode='lines+markers',
            x=df_ativo.iloc[:, 3],
            y=df_ativo.iloc[:, 2],
            name="Ativo",
            marker_color='blue',        
        ),
    )
    # Trace 2 -  Passivo
    fig.add_trace(
        go.Scatter(
            mode='lines+markers',
            x=df_passivo.iloc[:,3],
            y=df_passivo.iloc[:,2],
            name="Passivo",
            marker_color='red',          
        )
    )
    # Trace 3: Gráfico de Barras (Patrimonio líquido)
    fig.add_trace(
        go.Bar(
            x=df_patrimonio_liq.iloc[:, 3],
            y=df_patrimonio_liq.iloc[:, 2],
            name="Patrimonio Líquido",
            marker_color='mediumblue',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=.5
        ),
    ) 
    # Trace 4: Gráfico de Barras (Ativo circulante)
    fig.add_trace(
        go.Bar(                            
            
            x=df_ativo_circ.iloc[:, 3],
            y=df_ativo_circ.iloc[:, 2],
            name="Ativo Circulante",
            marker_color='cornflowerblue',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=.7                      
        ),
    )
    # Trace 5: Gráfico de Barras (Ativo não circulante)
    fig.add_trace(
        go.Bar(
            x=df_ativo_n_circ.iloc[:, 3],
            y=df_ativo_n_circ.iloc[:, 2],
            name="Ativo Não Circulantes",
            marker_color='gold',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=.6
        ),
    )
    # Trace 6: Gráfico de Barras (Passivo circulantes)
    fig.add_trace(
        go.Bar(
            x=df_passivo_circ.iloc[:, 3],
            y=df_passivo_circ.iloc[:, 2],
            name="Passivo Circulantes",
            marker_color='green',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=.6
        ),
    )
    # Trace 6: Gráfico de Barras (Passivo não circulantes)
    fig.add_trace(
        go.Bar(
            x=df_passivo_n_circ.iloc[:, 3],
            y=df_passivo_n_circ.iloc[:, 2],
            name="Passivo Não Circulantes",
            marker_color='crimson',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=.8
        ),
    )    
    # Atualize o layout geral
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.8,
        )
    )
    # Exibe o gráfico
    st.plotly_chart(fig, use_container_width=True)

# Função para criar o grafico do demoonstrativo de resultado  trimestral
def grafico_dre_anual(df, inicio, fim):
    
    # Ano anterior para calculo AH
    ano_anterior_calculado = inicio - 1

    # Filtra os valores para periodo selecionado
    df = df[(df["ANO"] >= ano_anterior_calculado) & (df["ANO"] <= fim )]

    # Transforma os dados da receita liquida e custos para o grafico
    df_receita_liquida = data_contabil.data_receita_liquida_custos_anual(df, inicio, fim)
    # Crie subplots com dois eixos y
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Trace 1: Gráfico de Linhas (lucro liquido)
    # Adiciona o gráfico de linhas no eixo primário (y)
    fig.add_trace(
        go.Scatter(
            mode='lines+markers',
            x=df_receita_liquida.iloc[:,0], 
            y=df_receita_liquida.iloc[:,2], 
            name="Lucro Líquido",
            marker_color='red'
        )
    )    
    # Trace 2: Gráfico de Barras (Receitas)
    fig.add_trace(
        go.Bar(
            x=df_receita_liquida.iloc[:,0],
            y=df_receita_liquida.iloc[:,3],
            name="Receita Líquida",
            marker_color='blue',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=0.5
        ),
        secondary_y=True
    )  
    # Trace 3: Gráfico de Barras (Custo)
    fig.add_trace(
        go.Bar(
            x=df_receita_liquida.iloc[:,0],
            y=df_receita_liquida.iloc[:,1],
            name="Custos",
            marker_color='darkblue',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=0.8
        ),
        secondary_y=True
    ) 
    # Configure os eixos y
    fig.update_yaxes(title_text="Lucro Líquido", secondary_y=False)
    fig.update_yaxes(title_text="Custos | Receita Líquida", secondary_y=True)

    # Atualiza o layout para sobrepor os gráficos de barras
    fig.update_layout(barmode='overlay')

    # Atualize o layout geral
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.4,
        )
    )
    # Exiba o gráfico
    st.plotly_chart(fig, use_container_width=True)

# Função para criar o grafico do demoonstrativo de resultado  trimestral
def grafico_dre_trimestral(df, inicio, fim):
    
    # Ano anterior para calculo AH
    ano_anterior_calculado = inicio - 1

    # Filtra os valores para periodo selecionado
    df = df[(df["ANO"] >= ano_anterior_calculado) & (df["ANO"] <= fim )]

    # Transforma os dados da receita liquida e custos para o grafico
    df_receita_liquida = data_contabil.data_receita_liquida_custos_trimestral(df, inicio, fim)

    # Crie subplots com dois eixos y
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Trace 1: Gráfico de Linhas (lucro liquido)
    # Adiciona o gráfico de linhas no eixo primário (y)
    fig.add_trace(
        go.Scatter(
            mode='lines+markers',
            x=df_receita_liquida.iloc[:,0], 
            y=df_receita_liquida.iloc[:,2], 
            name="Lucro Líquido",
            marker_color='red'
        )
    )    
    # Trace 2: Gráfico de Barras (Receitas)
    fig.add_trace(
        go.Bar(
            x=df_receita_liquida.iloc[:,0],
            y=df_receita_liquida.iloc[:,3],
            name="Receita Líquida",
            marker_color='blue',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=0.5
        ),
        secondary_y=True
    )  
    # Trace 3: Gráfico de Barras (Custo)
    fig.add_trace(
        go.Bar(
            x=df_receita_liquida.iloc[:,0],
            y=df_receita_liquida.iloc[:,1],
            name="Custos",
            marker_color='darkblue',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=0.8
        ),
        secondary_y=True
    ) 
    # Configure os eixos y
    fig.update_yaxes(title_text="Lucro Líquido", secondary_y=False)
    fig.update_yaxes(title_text="Custos | Receita Líquida", secondary_y=True)

    # Atualiza o layout para sobrepor os gráficos de barras
    fig.update_layout(barmode='overlay')

    # Atualize o layout geral
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.4,
        )
    )
    # Exiba o gráfico
    st.plotly_chart(fig, use_container_width=True)

# Função para criar o grafico do demoonstrativo de resultado  trimestral
def grafico_dre_trimestral(df, inicio, fim):
    
    # Ano anterior para calculo AH
    ano_anterior_calculado = inicio - 1

    # Filtra os valores para periodo selecionado
    df = df[(df["ANO"] >= ano_anterior_calculado) & (df["ANO"] <= fim )]

    # Transforma os dados da receita liquida e custos para o grafico
    df_receita_liquida = data_contabil.data_receita_liquida_custos_trimestral(df, inicio, fim)

    # Crie subplots com dois eixos y
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Trace 1: Gráfico de Linhas (lucro liquido)
    # Adiciona o gráfico de linhas no eixo primário (y)
    fig.add_trace(
        go.Scatter(
            mode='lines+markers',
            x=df_receita_liquida.iloc[:,0], 
            y=df_receita_liquida.iloc[:,2], 
            name="Lucro Líquido",
            marker_color='red'
        )
    )    
    # Trace 2: Gráfico de Barras (Receitas)
    fig.add_trace(
        go.Bar(
            x=df_receita_liquida.iloc[:,0],
            y=df_receita_liquida.iloc[:,3],
            name="Receita Líquida",
            marker_color='blue',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=0.5
        ),
        secondary_y=True
    )  
    # Trace 3: Gráfico de Barras (Custo)
    fig.add_trace(
        go.Bar(
            x=df_receita_liquida.iloc[:,0],
            y=df_receita_liquida.iloc[:,1],
            name="Custos",
            marker_color='darkblue',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=0.8
        ),
        secondary_y=True
    ) 
    # Configure os eixos y
    fig.update_yaxes(title_text="Lucro Líquido", secondary_y=False)
    fig.update_yaxes(title_text="Custos | Receita Líquida", secondary_y=True)

    # Atualiza o layout para sobrepor os gráficos de barras
    fig.update_layout(barmode='overlay')

    # Atualize o layout geral
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.4,
        )
    )
    # Exiba o gráfico
    st.plotly_chart(fig, use_container_width=True)

# Função para criar o grafico da AH do DRE
# @st.cache_data
def grafico_analise_horizontal_dre_anual(df, inicio, fim):

    # Ano anterior para calculo AH
    ano_anterior_calculado = inicio - 1

    # Filtra os valores para periodo selecionado
    df = df[(df["ANO"] >= ano_anterior_calculado) & (df["ANO"] <= fim )]
    
    # Transforma os dados da receita liquida e custos para o grafico
    df_receita_liquida = data_contabil.data_receita_liquida_custos_anual(df, inicio, fim)
    
    # Calcula a analise horizontal da receita liquida anual
    df_ah_receita_liquida = anls.calcular_analise_horizontal_receita_liquida_anual(df, inicio, fim)

    # Crie subplots com dois eixos y
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Trace 1: Gráfico de Linhas (AH % receita liquida)
    # Adiciona o gráfico de linhas no eixo primário (y)
    fig.add_trace(
        go.Scatter(
            mode='lines+markers',
            x=df_ah_receita_liquida.iloc[:,0], 
            y=df_ah_receita_liquida.iloc[:,1], 
            name="AH % Receita Líquida",
            marker_color='red'
        )
    )    
    # Trace 2: Gráfico de Barras (Receitas)
    fig.add_trace(
        go.Bar(
            x=df_receita_liquida.iloc[:,0],
            y=df_receita_liquida.iloc[:,3],
            name="Receita Líquida",
            marker_color='blue',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=0.5
        ),
        secondary_y=True
    )  
    # Trace 3: Gráfico de Barras (Custo)
    fig.add_trace(
        go.Bar(
            x=df_receita_liquida.iloc[:,0],
            y=df_receita_liquida.iloc[:,1],
            name="Custos",
            marker_color='darkblue',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=0.8
        ),
        secondary_y=True
    ) 
    # Configure os eixos y
    fig.update_yaxes(title_text="AH % Receita Líquida", secondary_y=False)
    fig.update_yaxes(title_text="Custos \ Receita Líquida", secondary_y=True)

    # Atualiza o layout para sobrepor os gráficos de barras
    fig.update_layout(barmode='overlay')

    # Atualize o layout geral
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.4,
        )
    )
    # # Exiba o gráfico
    st.plotly_chart(fig, use_container_width=True)

# Função para criar o grafico da AH do DRE
# @st.cache_data
def grafico_analise_horizontal_dre_trimestral(df, inicio, fim):
    # Ano anterior para calculo AH
    ano_anterior_calculado = inicio - 1

    # Filtra os valores para periodo selecionado
    df = df[(df["ANO"] >= ano_anterior_calculado) & (df["ANO"] <= fim )]

    # Transforma os dados da receita liquida e custos para o grafico
    df_receita_liquida = data_contabil.data_receita_liquida_custos_trimestral(df, inicio, fim)
    df_ah_receita_liquida = anls.calcular_analise_horizontal_receita_liquida_trimestral(df, inicio, fim)    

    # Crie subplots com dois eixos y
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Trace 1: Gráfico de Linhas (AH % receita liquida)
    # Adiciona o gráfico de linhas no eixo primário (y)
    fig.add_trace(
        go.Scatter(
            mode='lines+markers',
            x=df_ah_receita_liquida.iloc[:,0], 
            y=df_ah_receita_liquida.iloc[:,1], 
            name="AH % Receita Líquida",
            marker_color='red'
        )
    )    
    # Trace 2: Gráfico de Barras (Receitas)
    fig.add_trace(
        go.Bar(
            x=df_receita_liquida.iloc[:,0],
            y=df_receita_liquida.iloc[:,3],
            name="Receita Líquida",
            marker_color='blue',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=0.5
        ),
        secondary_y=True
    )  
    # Trace 3: Gráfico de Barras (Custo)
    fig.add_trace(
        go.Bar(
            x=df_receita_liquida.iloc[:,0],
            y=df_receita_liquida.iloc[:,1],
            name="Custos",
            marker_color='darkblue',
            marker_line_width=1.5,
            marker_line_color='rgb(8,48,107)',
            opacity=0.8
        ),
        secondary_y=True
    ) 
    # Configure os eixos y
    fig.update_yaxes(title_text="AH % Receita Líquida", secondary_y=False)
    fig.update_yaxes(title_text="Custos \ Receita Líquida", secondary_y=True)

    # Atualiza o layout para sobrepor os gráficos de barras
    fig.update_layout(barmode='overlay')

    # Atualize o layout geral
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.4,
        )
    )
    # Exiba o gráfico
    st.plotly_chart(fig, use_container_width=True)

# Função para criar o grafico da AV do DRE
# @st.cache_data
def grafico_analise_vertical_dre_anual(df):
    # def plotly_line_av_dre(df):
    # Crie subplots com dois eixos y
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Trace 1: Gráfico de Linhas
    # Adicione o gráfico de linhas no eixo primário (y)
    fig.add_trace(
        go.Scatter(
            mode='lines+markers',
            x=df.iloc[:,0],
            y=df.iloc[:, 1],
            name="AV% Resultado Líquido",
            marker_color='green'
        )
    )
    
    # Trace 2: Gráfico de Barras (Receitas)
    fig.add_trace(
        go.Scatter(
            mode='lines+markers',
            x=df.iloc[:,0],
            y=df.iloc[:, 2],
            name="AV% Resultado Bruto",
            marker_color='blue'
        ),
    )  
    # Configure os eixos y
    fig.update_yaxes(title_text="AV %", secondary_y=False)

    # Atualiza o layout para sobrepor os gráficos de barras
    fig.update_layout(barmode='overlay')

    # Atualize o layout geral
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.4,
        )
    )
    # # Exiba o gráfico
    st.plotly_chart(fig, use_container_width=True)

# Função para criar o grafico da AV do DRE
# @st.cache_data
def grafico_analise_vertical_dre_trimestral(df):
    # Crie subplots com dois eixos y
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Trace 1: Gráfico de Linhas
    # Adicione o gráfico de linhas no eixo primário (y)
    fig.add_trace(
        go.Scatter(
            mode='lines+markers',
            x=df['PERIODO'],
            y=df.iloc[:, 1],
            name="AV% Resultado Líquido",
            marker_color='green'
        )
    )
    
    # Trace 2: Gráfico de Barras (Receitas)
    fig.add_trace(
        go.Scatter(
            mode='lines+markers',
            x=df['PERIODO'],
            y=df.iloc[:, 2],
            name="AV% Resultado Bruto",
            marker_color='blue'
        ),
    )  
    # Configure os eixos y
    fig.update_yaxes(title_text="AV %", secondary_y=False)

    # Atualiza o layout para sobrepor os gráficos de barras
    fig.update_layout(barmode='overlay')

    # Atualize o layout geral
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=0.4,
        )
    )
    # Exiba o gráfico
    st.plotly_chart(fig, use_container_width=True)

# Funlçai para criar o grafico de area das margens no dashboard
@st.cache_data
def grafico_area_margens_dashboard(df):    
    # Recebe os dados calculados
    df_margens = data_contabil.data_grafico_margens_dashboard(df)    
    print(df_margens)
    fig = px.area(df_margens, x="ANO", y="VALOR", color="MARGENS")
    # fig.update_traces(textposition='top center')
    fig.update_layout(legend=dict(
                orientation="h",
                entrywidth=100,
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
                ))
    fig.update_xaxes(title_text=None)
    fig.update_yaxes(title_text=None)
    # fig.update_layout(margin=dict(b=0, l=1, t=0, r=10))

    st.plotly_chart(fig, use_container_width=True) # GRAFICO DE AREA

# Função para criar o grafico de area dos indicadores no dashboard
# @st.cache_data
def grafico_area_indicadores_dashboard(df):
   
    df = data_contabil.calcula_indicadores_grafico_dashboard(df)

    fig = px.area(df, x="ANO", y="VALOR", color="MARGENS")
    # fig.update_traces(textposition='top center')
    fig.update_layout(legend=dict(
                orientation="h",
                entrywidth=100,
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
                ))
    # Remova as etiquetas dos eixos x e y
    fig.update_xaxes(title_text=None)
    fig.update_yaxes(title_text=None)
    
    st.plotly_chart(fig, use_container_width=True)

# Função para criar o grafico de area dos indicadores trimestrais
# @st.cache_data
def grafico_area_margens_anual(df):
    try:
        # Ordena os dados para o grafico
        fig = px.area(df,
                      x='ANO',
                      y='VALOR',
                      color='ÍNDICES',
                      text='VALOR',
                      markers=True)

        fig.update_traces(textposition='top center')
        fig.update_layout(legend=dict(
                    orientation="h",
                    entrywidth=100,
                    yanchor="bottom",
                    y=1.02, 
                    xanchor="right",
                    x=1
                    ))
        # Remova as etiquetas dos eixos x e y
        fig.update_xaxes(title_text=None)
        fig.update_yaxes(title_text=None)

        # Acrescentando mais dois valores para os limites do eixo x
        limite_inferior = df['ANO'].values[0] - 1 
        limite_superior = df['ANO'].values[-1] + 1

        # Configurando os limites do eixo x
        fig.update_xaxes(range=[limite_inferior, limite_superior])

        # Configuração dos marcadores no eixo x para exibir apenas os valores presentes nos dados
        anos_presentes = sorted(df['ANO'].unique())
        fig.update_xaxes(tickvals=anos_presentes)

        # Exibir gráfico no Streamlit
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        # Captura qualquer erro e exibe a mensagem de erro detalhada
        st.error(f"Ocorreu um erro ao gerar o gráfico: {str(e)}", icon="🚨")
        st.write("Detalhes do erro:", e)

# Função para criar o grafico de area dos indicadores trimestrais
# @st.cache_data
def grafico_area_margens_trimestral(df, inicio, fim):
    # Ordena os dados para o grafico
    df = ordenar_grafico_linhas_indicadores_trimestral(df,inicio,fim)
    fig = px.area(df,
                      x='TRIMESTRE',
                      y='VALOR',
                      color='ÍNDICES',
                      text='VALOR',
                      markers=True)

    fig.update_traces(textposition='top center')
    fig.update_layout(legend=dict(
                orientation="h",
                entrywidth=100,
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
                ))
    # Remova as etiquetas dos eixos x e y
    fig.update_xaxes(title_text=None)
    fig.update_yaxes(title_text=None)

    st.plotly_chart(fig, use_container_width=True)

# Função para criar o grafico de area dos indicadores trimestrais
# @st.cache_data
def grafico_linhas_liquidez_anual(df):
    # Gráfico para margens
    fig = px.line(df,
                      x='ANO',
                      y='VALOR',
                      color='ÍNDICES',
                      text='VALOR',
                      markers=True)
    
    fig.update_xaxes(title_text=None)
    fig.update_yaxes(title_text=None)
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig, use_container_width=True)

# Função para criar o grafico de area dos indicadores trimestrais
# @st.cache_data
def grafico_linhas_liquidez_trimestral(df):
    # Gráfico para margens
    fig = px.line(df,
                      x='TRIMESTRE',
                      y='VALOR',
                      color='ÍNDICES',
                      text='VALOR',
                      markers=True)
    
    fig.update_xaxes(title_text=None)
    fig.update_yaxes(title_text=None)
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig, use_container_width=True)