import streamlit as st

import helpers.criarGraficos as graf
import helpers.demonstrativos as demo
import helpers.analises as anls

from helpers.gpt_client import generate_analises_dre
from helpers.gpt_client import generate_analises_dre_agressiva
from helpers.gpt_client import generate_analises_dre_conservadora
from lang import financial_assistant
# Gera a página da guia Demonstrativo de Resultado
def pagina_dre():

    # Verifica se os dados estão no session_state
    if 'data' not in st.session_state:
        st.error("Nenhum dado disponível no session_state.")
        return

    # Recebe o dataframe do session state 
    df = st.session_state['data']

    # Filtra para "Demonstração do Resultado"
    df = df[df["DEMONSTRATIVO"] == "Demonstração do Resultado"]
    periodos_dados = df['PERIODO'].unique()
    
    if df.empty:
        st.error("Nenhum dado disponível para a Demonstração de Resultado.")
        return

    # Lendo os valores da coluna ANO
    periodo = sorted(df["ANO"].unique(), reverse=True)

    # Cria o layout
    with st.container():         
        col1, col2, col3, col4, col5, col6 = st.columns([3,1,1,2,1,1])

    with col1:
        # Ler nome da empresa
        emp = df['EMPRESA'].unique()
        st.write(" ")
        st.write(f"Empresa: {emp[0]}")
        st.markdown("_Protótipo v0.2.0_")

    with col3:    
        filtra_tipo_dados = st.selectbox("Filtros", ["DATA", "AH", "AV"])   
                    
    with col4:   
        # Define "ANUAL" como padrão, se estiver disponível
        if "ANUAL" in periodos_dados:
            index_anual = list(periodos_dados).index("ANUAL")
        else:
            index_anual = 0  # Caso "ANUAL" não esteja disponível, o primeiro item será selecionado

        # Exibe o selectbox com "ANUAL" pré-selecionado, se disponível
        intervalo = st.selectbox("Período", periodos_dados, index=index_anual)
    with col5:
        # Ordena os anos e define o valor padrão para os últimos 4 anos, ou menos, se não houver 4 disponíveis
        anos_disponiveis = sorted(periodo, reverse=True)
        
        if len(anos_disponiveis) >= 4:
            ano_inicio_default = anos_disponiveis[3]  # Pega o quarto ano mais recente
        elif len(anos_disponiveis) >= 3:
            ano_inicio_default = anos_disponiveis[2]
        elif len(anos_disponiveis) >= 2:
            ano_inicio_default = anos_disponiveis[1]
        else:
            ano_inicio_default = anos_disponiveis[0]

        ano_inicio_selecionado = st.selectbox('De:', anos_disponiveis, index=anos_disponiveis.index(ano_inicio_default))

    with col6:
        # Seleciona o ano final como o mais recente disponível
        ano_fim_selecionado = st.selectbox('Até:', anos_disponiveis, index=0)  #
    
    # Exibe a tabela apenas se início for menor que o fim
    if ano_inicio_selecionado > ano_fim_selecionado:
        st.warning("Selecione uma data de início menor que a data de fim.")      
        return

    try:
        if intervalo == "Trimestral": 
            df = df[df["PERIODO"] != "ANUAL"]  # Verifica se os dados não são anuais

            if df.empty:
                st.warning("Não há dados disponíveis para o período trimestral.")
                return

            # Cria dataframes trimestrais
            dre = demo.cria_dataframe_trimestral_dre(df, ano_inicio_selecionado, ano_fim_selecionado)
            df_ah = anls.calcular_analise_horizontal_trimestral(df, ano_inicio_selecionado, ano_fim_selecionado)
            df_av, result_bruto = anls.calcular_analise_vertical_trimestral_resultado(df, ano_inicio_selecionado, ano_fim_selecionado)
        
        elif intervalo == "ANUAL": 
            df = df[df["PERIODO"] == "ANUAL"]

            if df.empty:
                st.warning("Não há dados disponíveis para o período anual.")
                return
            
            # Cria dataframes anuais
            dre = demo.cria_dataframe_anual_dre(df, ano_inicio_selecionado, ano_fim_selecionado)
            df_ah = anls.calcular_analise_horizontal_anual(df, ano_inicio_selecionado, ano_fim_selecionado)
            df_av, result_bruto = anls.calcular_analise_vertical_anual(df, ano_inicio_selecionado, ano_fim_selecionado)

        tab1, tab2 = st.tabs(["📈 Gráfico", "📈 Tabular"])

        # Análise Horizontal
        if filtra_tipo_dados == "AH": 
            with tab1:
                try:
                    if intervalo == "Trimestral":     
                        graf.grafico_analise_horizontal_dre_trimestral(df, ano_inicio_selecionado, ano_fim_selecionado)
                    elif intervalo == "ANUAL":
                        graf.grafico_analise_horizontal_dre_anual(df, ano_inicio_selecionado, ano_fim_selecionado)
                except Exception as e:
                    st.error(f"Ocorreu um erro ao gerar o gráfico de Análise Horizontal: {e}")

            with tab2:
                if df_ah.empty:
                    st.warning("Não há dados disponíveis para a Análise Horizontal.")
                else:
                    st.dataframe(df_ah, use_container_width=True, hide_index=True)

        # Análise Vertical
        elif filtra_tipo_dados == "AV":           
            with tab1:
                try:
                    if intervalo == "Trimestral":
                        if result_bruto is None or result_bruto.empty:
                            st.warning("Não há dados disponíveis para a análise vertical trimestral.")
                        else:
                            graf.grafico_analise_vertical_dre_trimestral(result_bruto)
                    elif intervalo == "ANUAL":
                        if result_bruto is None or result_bruto.empty:
                            st.warning("Não há dados disponíveis para a análise vertical anual.")
                        else:
                            graf.grafico_analise_vertical_dre_anual(result_bruto)
                except Exception as e:
                    st.error(f"Ocorreu um erro ao gerar o gráfico de Análise Vertical: {e}")

            with tab2:
                if df_av.empty:
                    st.warning("Não há dados disponíveis para a Análise Vertical.")
                else:
                    st.dataframe(df_av, use_container_width=True, hide_index=True)

        else:
            with tab1:
                try:
                    if intervalo == "Trimestral":                         
                        graf.grafico_dre_trimestral(df, ano_inicio_selecionado, ano_fim_selecionado)
                    elif intervalo == "ANUAL":
                        graf.grafico_dre_anual(df, ano_inicio_selecionado, ano_fim_selecionado)
                except Exception as e:
                    st.error(f"Ocorreu um erro ao gerar o gráfico do DRE: {e}")

            with tab2:
                if dre.empty:
                    st.warning("Não há dados disponíveis para o DRE.")
                else:
                    st.dataframe(dre, use_container_width=True, hide_index=True, width=700, height=500)

        with st.expander("Para uma nova análise, clique no botão novamente", expanded=True):
            years = list(range(ano_inicio_selecionado, ano_fim_selecionado + 1))

            if st.button('Gerar Análise', key='botao1'):
                with st.spinner('Gerando análise DRE...'):
                    try:
                        if filtra_tipo_dados == "DATA":
                            result_text = generate_analises_dre(dre, "DATA")
                        elif filtra_tipo_dados == "AH":
                            result_text = generate_analises_dre(df_ah, "AH")
                        elif filtra_tipo_dados == "AV":
                            result_text = generate_analises_dre(df_av, "AV")
                        st.success('Análise DRE gerada!')
                        st.write(result_text)
                    except Exception as e:
                        st.error(f"Ocorreu um erro ao gerar a análise: {e}")

            if st.button('Sugestão de Ação Agressiva', key='botao2'):
                with st.spinner('Gerando sugestão de ação agressiva...'):
                    try:
                        if filtra_tipo_dados == "DATA":
                            aggressive_analysis = generate_analises_dre_agressiva(dre, "DATA")
                        elif filtra_tipo_dados == "AH":
                            aggressive_analysis = generate_analises_dre_agressiva(df_ah, "AH")
                        elif filtra_tipo_dados == "AV":
                            aggressive_analysis = generate_analises_dre_agressiva(df_av, "AV")
                        st.success('Sugestão de ação agressiva gerada!')
                        st.write(aggressive_analysis)
                    except Exception as e:
                        st.error(f"Ocorreu um erro ao gerar a sugestão agressiva: {e}")

            if st.button('Sugestão de Ação Conservadora', key='botao3'):
                with st.spinner('Gerando sugestão de ação conservadora...'):
                    try:
                        if filtra_tipo_dados == "DATA":
                            conservative_analysis = generate_analises_dre_conservadora(dre, "DATA")
                        elif filtra_tipo_dados == "AH":
                            conservative_analysis = generate_analises_dre_conservadora(df_ah, "AH")
                        elif filtra_tipo_dados == "AV":
                            conservative_analysis = generate_analises_dre_conservadora(df_av, "AV")
                        st.success('Sugestão de ação conservadora gerada!')
                        st.write(conservative_analysis)
                    except Exception as e:
                        st.error(f"Ocorreu um erro ao gerar a sugestão conservadora: {e}")
                # return filtra_tipo_dados, dre, df_ah, df_av
            user_question = st.text_input("Pergunta:")
            if st.button("Enviar Pergunta"):
                if user_question:
                    with st.spinner('Gerando resposta...'):
                        truncated_question = user_question[:100]  # Ajuste conforme necessário

                        # Verificar qual DataFrame está sendo usado
                        if filtra_tipo_dados == "DATA":
                            teste = dre
                        elif filtra_tipo_dados == "AH":
                            teste = df_ah
                        elif filtra_tipo_dados == "AV":
                            teste = df_av

                        # Reduzir o tamanho do DataFrame para evitar exceder o limite de tokens
                        teste_reduzido = teste  # Manter apenas as primeiras 5 linhas

                        # Chamar a função financial_assistant com o DataFrame de teste reduzido
                        financial_assistant(truncated_question, teste_reduzido)
    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
