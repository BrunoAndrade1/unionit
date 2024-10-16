import streamlit as st
import pandas as pd
import plotly.express as px

import helpers.criarGraficos as graf
import helpers.dadoscontabeis as data_contabil
from helpers.gpt_client import generate_analises_indicadores
from helpers.gpt_client import generate_analises_indicadores_agressiva
from helpers.gpt_client import generate_analises_indicadores_conservadora
from lang import financial_assistant

# Gera a página da guia indicadores
def pagina_indicadores():        
    # Verifica se os dados estão no session_state
    if 'data' not in st.session_state:
        st.error("Nenhum dado disponível no session_state.")
        return

    # Recebe o dataframe do session state 
    df = st.session_state['data']

    # Verifica se o dataframe não está vazio
    if df.empty:
        st.error("Nenhum dado disponível para a empresa selecionada.")
        return

    # Lendo os valores da coluna ANO
    periodo = sorted(df["ANO"].unique(), reverse=True)
    
    # Obtém os períodos disponíveis (Trimestral ou Anual)
    periodos_dados = df['PERIODO'].unique()
    
    # Inicializa as variáveis dos dataframes que serão utilizados posteriormente
    df_margens, df_liquidez, df_indicadores, df_indicadores_ia = None, None, None, None

    # Cria o layout
    with st.container():         
        col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 2, 1, 1])

    with col1:
        # Lê e exibe o nome da empresa
        emp = df['EMPRESA'].unique()
        st.write(" ")
        st.write(f"Empresa: {emp[0]}")
        st.markdown("_Protótipo v0.2.0_")
    
    with col4:   
        # Seleciona o período (Trimestral ou Anual)
        intervalo = st.selectbox(
            "Período", 
            periodos_dados,
            index=periodos_dados.tolist().index("ANUAL") if "ANUAL" in periodos_dados else 0
        )

    with col5:
        # Ordena os anos disponíveis
        anos_disponiveis = sorted(periodo, reverse=True)
        
        # Define o ano de início padrão: o quarto ano mais recente, ou menos se houver menos de 4 anos disponíveis
        if len(anos_disponiveis) >= 4:
            ano_inicio_default = anos_disponiveis[3]
        elif len(anos_disponiveis) >= 3:
            ano_inicio_default = anos_disponiveis[2]
        elif len(anos_disponiveis) >= 2:
            ano_inicio_default = anos_disponiveis[1]
        else:
            ano_inicio_default = anos_disponiveis[0]

        # Caixa de seleção para o ano de início
        ano_inicio_selecionado = st.selectbox(
            'De:',
            anos_disponiveis,
            index=anos_disponiveis.index(ano_inicio_default)
        )

    with col6:
        # Define o ano de fim padrão como o ano mais recente disponível
        ano_fim_default = anos_disponiveis[0]

        # Caixa de seleção para o ano de fim
        ano_fim_selecionado = st.selectbox(
            'Até:',
            anos_disponiveis,
            index=anos_disponiveis.index(ano_fim_default)
        )

    # Valida se o ano de início é menor ou igual ao ano de fim
    if ano_inicio_selecionado > ano_fim_selecionado:
        st.warning("Selecione outra data: o ano de início não pode ser maior que o ano de fim.")
    else:
        st.success(f"Período selecionado: de {ano_inicio_selecionado} até {ano_fim_selecionado}")
        
        # Filtra os dados com base no período selecionado (Trimestral ou Anual)
        if intervalo == "Trimestral": 
            df = df[df["PERIODO"] != "ANUAL"]
            if df.empty:
                st.warning("Não há dados trimestrais disponíveis para o intervalo selecionado.")
                return
            # Recebe dados para os gráficos trimestrais
            df_margens, df_liquidez, df_indicadores, df_indicadores_ia = data_contabil.data_margens_trimestral(df, ano_inicio_selecionado, ano_fim_selecionado)  

        elif intervalo == "ANUAL": 
            df = df[df["PERIODO"] == "ANUAL"]
            if df.empty:
                st.warning("Não há dados anuais disponíveis para o intervalo selecionado.")
                return
            # Recebe dados para os gráficos anuais
            df_margens, df_liquidez, df_indicadores, df_indicadores_ia = data_contabil.data_margens_anual(df, ano_inicio_selecionado, ano_fim_selecionado)  
      
        # Verifica se os dados foram retornados corretamente
        if df_margens is not None:
            tab1, tab2, tab3 = st.tabs(["📈 Margens", "📈 Líquidez", "📈 Tabular"])
            
            with tab1:  # Aba das margens                         
                # Cria o gráfico de margens
                if intervalo == "Trimestral":     
                    graf.grafico_area_margens_trimestral(df_margens, ano_inicio_selecionado, ano_fim_selecionado)
                else:
                    graf.grafico_area_margens_anual(df_margens)

            with tab2:  # Aba da liquidez
                # Cria o gráfico de liquidez
                if intervalo == "Trimestral":     
                    graf.grafico_linhas_liquidez_trimestral(df_liquidez)
                else:
                    graf.grafico_linhas_liquidez_anual(df_liquidez)
                
            with tab3:  # Aba tabular
                st.dataframe(df_indicadores, hide_index=True, use_container_width=True)  

        else:
            st.error("Erro: Não foram encontrados dados para o intervalo selecionado.")
    
        # Expansor para novas análises
        with st.expander("Para uma nova análise, clique no botão novamente", expanded=True):
            # Cria a lista a partir do intervalo do período
            years = list(range(ano_inicio_selecionado, ano_fim_selecionado + 1)) 
            
            # Primeiro botão: 'Gerar Análise'
            if st.button('Gerar Análise', key='botao1'):

                # Se o intervalo de anos selecionado for superior a 5 anos, a análise será anual
                if len(years) >= 5:
                    _, _, _, df_indicadores_ia = data_contabil.data_margens_anual(df, ano_inicio_selecionado, ano_fim_selecionado)  

                with st.spinner('Gerando análise dos indicadores...'):
                    analysis = generate_analises_indicadores(df_indicadores_ia)
                    
                st.success('Análise dos indicadores gerada!')
                st.write(analysis)     

            # Segundo botão: 'Sugestão de Ação Agressiva'
            if st.button('Sugestão de Ação Agressiva', key='botao2'):
        
                # Se o intervalo de anos selecionado for superior a 5 anos, a análise será anual
                if len(years) >= 5:
                    _, _, _, df_indicadores_ia = data_contabil.data_margens_anual(df, ano_inicio_selecionado, ano_fim_selecionado)  

                with st.spinner('Gerando análise agressiva dos indicadores...'):
                    aggressive_analysis = generate_analises_indicadores_agressiva(df_indicadores_ia)
                    
                st.success('Análise agressiva dos indicadores gerada!')
                st.write(aggressive_analysis)

            # Terceiro botão: 'Sugestão de Ação Conservadora'
            if st.button('Sugestão de Ação Conservadora', key='botao3'):

                # Se o intervalo de anos selecionado for superior a 5 anos, a análise será anual
                if len(years) >= 5:
                    _, _, _, df_indicadores_ia = data_contabil.data_margens_anual(df, ano_inicio_selecionado, ano_fim_selecionado)  

                with st.spinner('Gerando análise conservadora dos indicadores...'):
                    conservative_analysis = generate_analises_indicadores_conservadora(df_indicadores_ia)
                
                st.success('Análise conservadora dos indicadores gerada!')
                st.write(conservative_analysis)
############################################
            user_question = st.text_input("Pergunta:")
            if st.button("Enviar Pergunta"):
                if user_question:
                    with st.spinner('Gerando resposta...'):
                        financial_assistant(user_question, df_indicadores_ia)