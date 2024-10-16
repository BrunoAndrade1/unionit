import streamlit as st

import helpers.criarGraficos as graf
import helpers.demonstrativos as demo
import helpers.analises as anls

from helpers.gpt_client import generate_analises_bp
from helpers.gpt_client import generate_analises_bp_agressiva
from helpers.gpt_client import generate_analises_bp_conservadora
from lang import financial_assistant
# Gera a página da guia Balanço Patrimonial
def pagina_bp():        
    # Recebe o dataframe do session state 
    df = st.session_state['data']

    # Filtra as contas de BP Ativo e Passivo
    df = df[(df["DEMONSTRATIVO"] == "Balanço Patrimonial Ativo") | (df["DEMONSTRATIVO"] == "Balanço Patrimonial Passivo")]

    # Lendo os valores da coluna ANO 
    periodo = sorted(df["ANO"].unique(), reverse=True)

    periodos_dados = df['PERIODO'].unique()

    # Cria o layout
    with st.container():         
        col_bp1, col_bp2, col_bp3, col_bp4, col_bp5, col_bp6 = st.columns([3, 1, 1, 2, 1, 1])

    with col_bp1:
        # Ler e exibe o nome da empresa
        emp = df['EMPRESA'].unique()
        st.write(" ")
        st.write(f"Empresa: {emp[0]}")
        st.markdown("_Protótipo v0.2.0_")

    with col_bp3:    
        filtra_tipo_dados = st.selectbox(
            "Filtros", ["DATA", "AH", "AV"]
        )  
                    
    with col_bp4:   
        # Seleciona o período (Trimestral ou Anual), predefinindo "ANUAL" como padrão, se disponível
        intervalo = st.selectbox(
            "Período", 
            periodos_dados,
            index=periodos_dados.tolist().index("ANUAL") if "ANUAL" in periodos_dados else 0
        )

    with col_bp5:
        # Ordena os anos disponíveis
        anos_disponiveis = sorted(periodo, reverse=True)

        # Define o ano de início padrão: o quarto ano mais recente ou menos, se houver menos de 4 anos
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

    with col_bp6:
        # Define o ano de fim padrão como o ano mais recente disponível
        ano_fim_default = anos_disponiveis[0]

        # Caixa de seleção para o ano de fim
        ano_fim_selecionado = st.selectbox(
            'Até:',
            anos_disponiveis,
            index=anos_disponiveis.index(ano_fim_default)
        )

    # Exibe um aviso se o ano de início for maior que o ano de fim
    if ano_inicio_selecionado > ano_fim_selecionado:
        st.warning("Selecione outra data: o ano de início não pode ser maior que o ano de fim.")
    else:
        st.success(f"Período selecionado: de {ano_inicio_selecionado} até {ano_fim_selecionado}")

        # Filtra os dados com base no período selecionado (Trimestral ou Anual)
        if intervalo == "Trimestral": 
            df = df[df["PERIODO"] != "ANUAL"]
            
            # Verifica se há dados trimestrais disponíveis
            if df.empty:
                st.warning("Não há dados trimestrais disponíveis para o intervalo selecionado.")
                return
            
            # Cria dataframes trimestrais
            bpa = demo.cria_dataframe_trimestral_bp(df, ano_inicio_selecionado, ano_fim_selecionado)
            df_ah = anls.calcular_analise_horizontal_trimestral(df, ano_inicio_selecionado, ano_fim_selecionado)
            df_av = anls.calcular_analise_vertical_trimestral_patrimonio(df, ano_inicio_selecionado, ano_fim_selecionado)

        elif intervalo == "ANUAL": 
            df = df[df["PERIODO"] == "ANUAL"]

            # Verifica se há dados anuais disponíveis
            if df.empty:
                st.warning("Não há dados anuais disponíveis para o intervalo selecionado.")
                return
            
            # Cria dataframes anuais
            bpa = demo.cria_dataframe_anual_bp(df, ano_inicio_selecionado, ano_fim_selecionado)
            df_ah = anls.calcular_analise_horizontal_anual(df, ano_inicio_selecionado, ano_fim_selecionado)
            df_av, _ = anls.calcular_analise_vertical_anual(df, ano_inicio_selecionado, ano_fim_selecionado)

        # Instancia das abas
        tab1, tab2 = st.tabs(["📈 Gráfico", "📈 Tabular"])

        # Seleciona a análise horizontal
        if filtra_tipo_dados == "AH":
            with tab1: 
                # Cria o gráfico de BP trimestral ou anual
                if intervalo == "Trimestral":     
                    graf.grafico_bp_trimestral(df, ano_inicio_selecionado, ano_fim_selecionado)
                else:
                    graf.grafico_bp_anual(df, ano_inicio_selecionado, ano_fim_selecionado)

            with tab2: 
                # Exibe o DataFrame da análise horizontal
                st.dataframe(df_ah, use_container_width=True, hide_index=True)

        # Seleciona a análise vertical
        elif filtra_tipo_dados == 'AV':
            with tab1: 
                if intervalo == "Trimestral":     
                    graf.grafico_bp_trimestral(df, ano_inicio_selecionado, ano_fim_selecionado)
                else:
                    graf.grafico_bp_anual(df, ano_inicio_selecionado, ano_fim_selecionado)

            with tab2: 
                # Exibe a tabela da análise vertical
                st.dataframe(df_av, use_container_width=True, hide_index=True)

        # Seleciona os dados do BP
        else:                    
            with tab1:
                if intervalo == "Trimestral":     
                    graf.grafico_bp_trimestral(df, ano_inicio_selecionado, ano_fim_selecionado)
                else:
                    graf.grafico_bp_anual(df, ano_inicio_selecionado, ano_fim_selecionado)
                    
            with tab2:
                # Exibe o DataFrame dos dados do BP
                st.dataframe(bpa, use_container_width=True, hide_index=True, width=700, height=500)

        # Expansor para novas análises
        with st.expander("Para uma nova análise, clique no botão novamente", expanded=True):
            # Cria a lista a partir do intervalo do período
            years = list(range(ano_inicio_selecionado, ano_fim_selecionado + 1))

            if st.button('Gerar Análise', key='botao1'):
                # Executa a análise com base nos dados disponíveis, independentemente de quantos anos estejam presentes
                bpa = demo.cria_dataframe_anual_bp(df, ano_inicio_selecionado, ano_fim_selecionado)
                df_ah = anls.calcular_analise_horizontal_anual(df, ano_inicio_selecionado, ano_fim_selecionado)
                df_av, _ = anls.calcular_analise_vertical_anual(df, ano_inicio_selecionado, ano_fim_selecionado)

                with st.spinner('Gerando análise de BP...'):
                    if filtra_tipo_dados == "DATA":
                        result_text = generate_analises_bp(bpa, "DATA")
                    elif filtra_tipo_dados == "AH":
                        result_text = generate_analises_bp(df_ah, "AH")
                    elif filtra_tipo_dados == "AV":
                        result_text = generate_analises_bp(df_av, "AV")

                st.success('Análise de BP gerada!')
                st.write(result_text)

            # Sugestão de Ação Agressiva
            if st.button('Sugestão de Ação Agressiva', key='botao2'):
                # Executa a sugestão de ação agressiva com base nos dados disponíveis, independentemente do número de anos
                bpa = demo.cria_dataframe_anual_bp(df, ano_inicio_selecionado, ano_fim_selecionado)
                df_ah = anls.calcular_analise_horizontal_anual(df, ano_inicio_selecionado, ano_fim_selecionado)
                df_av, _ = anls.calcular_analise_vertical_anual(df, ano_inicio_selecionado, ano_fim_selecionado)

                with st.spinner('Gerando sugestão de ação agressiva para BP...'):
                    if filtra_tipo_dados == "DATA":
                        aggressive_analysis = generate_analises_bp_agressiva(bpa, "DATA")
                    elif filtra_tipo_dados == "AH":
                        aggressive_analysis = generate_analises_bp_agressiva(df_ah, "AH")
                    elif filtra_tipo_dados == "AV":
                        aggressive_analysis = generate_analises_bp_agressiva(df_av, "AV")

                st.success('Sugestão de ação agressiva para BP gerada!')
                st.write(aggressive_analysis)

            # Sugestão de Ação Conservadora
            if st.button('Sugestão de Ação Conservadora', key='botao3'):
                # Executa a sugestão de ação conservadora com base nos dados disponíveis, independentemente do número de anos
                bpa = demo.cria_dataframe_anual_bp(df, ano_inicio_selecionado, ano_fim_selecionado)
                df_ah = anls.calcular_analise_horizontal_anual(df, ano_inicio_selecionado, ano_fim_selecionado)
                df_av, _ = anls.calcular_analise_vertical_anual(df, ano_inicio_selecionado, ano_fim_selecionado)

                with st.spinner('Gerando sugestão de ação conservadora para BP...'):
                    if filtra_tipo_dados == "DATA":
                        conservative_analysis = generate_analises_bp_conservadora(bpa, "DATA")
                    elif filtra_tipo_dados == "AH":
                        conservative_analysis = generate_analises_bp_conservadora(df_ah, "AH")
                    elif filtra_tipo_dados == "AV":
                        conservative_analysis = generate_analises_bp_conservadora(df_av, "AV")

                st.success('Sugestão de ação conservadora para BP gerada!')
                st.write(conservative_analysis)
##########################################################################################
            user_question = st.text_input("Pergunta:")
            if st.button("Enviar Pergunta"):
                if user_question:
                    with st.spinner('Gerando resposta...'):
                        truncated_question = user_question[:100]  # Ajuste conforme necessário

                        # Verificar qual DataFrame está sendo usado
                        if filtra_tipo_dados == "DATA":
                            teste = bpa
                        elif filtra_tipo_dados == "AH":
                            teste = df_ah
                        elif filtra_tipo_dados == "AV":
                            teste = df_av

                        # Reduzir o tamanho do DataFrame para evitar exceder o limite de tokens
                        teste_reduzido = teste.head(5)  # Manter apenas as primeiras 5 linhas

                        # Chamar a função financial_assistant com o DataFrame de teste reduzido
                        financial_assistant(truncated_question, teste_reduzido)