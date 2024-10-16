import streamlit as st
from streamlit_extras.grid import grid
from streamlit_option_menu import option_menu

import helpers.criarGraficos as grf
import helpers.dadoscontabeis as data_contabil
from paginas.configuracao_de import pagina_configuracao
from helpers.gpt_client import generate_analysis_dashboard
from helpers.gpt_client import generate_analysis_dashboard_agressiva
from helpers.gpt_client import generate_analysis_dashboard_conservadora
from lang import financial_assistant

def dashboard():
   
    # Recebe o dataframe do session state 
    df = st.session_state['data']
    
    # Recebe os dados calculados
    df_data_dash = data_contabil.data_dashboard(df)
    
    # Cria layout
    my_grid = grid(4,3, vertical_align="bottom")

    # Armazena o nome da empresa
    empresa = df['EMPRESA'].unique()

    # Armazena as informações sobre cada indicador
    div_pl_help = "Indica quanto de dívida uma empresa está usando para financiar os seus ativos em relação ao patrimònio dos acionistas."
    cagr_lucro_help = "O CAGR (Compound Annual Growth Rate), ou taxa de crescimento anual composta, é a taxa de retorno necessária para um investimento crescer de seu saldo inicial para o seu saldo final."
    cagr_receita_help = "O CAGR (Compound Annual Growth Rate), ou taxa de crescimento anual composta, é a taxa de retorno necessária para um investimento crescer de seu saldo inicial para o seu saldo final."
    help_div_liq_ebitda = "Indica quanto tempo seria necessário para pagar a dívida líquida da empresa considerando o EBITDA atual. Indica também o grau de endividamento da companhia."
    help_div_liq_ebit = "Indica quanto tempo seria necessário para pagar a dívida líquida da empresa considerando o EBIT atual. Indica também o grau de endividamento da companhia."
    help_pl_ativos = "Este indicador é para mostrar a relação dos ativos no patrimônio da empresa."
    help_passivos_ativos = "Cálculo para saber a relação entre os ativos (circulantes e não circulantes) e os passivos de uma empresa."
    help_liq_corrente = "Indica a capacidade de pagamento da empresa no curto prazo."
    help_margem_bruta = "Mede de maneira objetiva o quanto a empresa ganha com a venda de seus produtos."
    help_margem_ebitda = "É a proporção do lucro operacional em relação à receita líquida da empresa."
    help_margem_ebit = "Mede a lucratividade da empresa sem considerar o efeito de juros e impostos."
    help_margem_liquida = "Representa a porcentagem de lucro em relação às receitas de uma empresa."
    help_roe = "Mede a capacidade de uma empresa de agregar valor a partir de seus próprios recursos."
    help_roa = "Return on assets - indica quanto do valor que a empresa investiu na operação voltou para o negócio sob a forma de lucro."
    help_roic = "Mede a capacidade da empresa de gerar retorno com base no capital total investido, incluíndo aportes por meio de dívidas."
    help_giro_ativos = "Mede como a empresa esta utilizando o seu ativo para produzir riqueza, através da venda de seus produtos/serviços."

    # Filtros
    Liq_corrente = df_data_dash.loc[df_data_dash["ÍNDICES"] == "Liq_corrente", "VALOR"].values[0]
    Div_liq_ebit = df_data_dash.loc[df_data_dash["ÍNDICES"] == "Div_liq_ebit", "VALOR"].values[0]
    div_liq = df_data_dash.loc[df_data_dash["ÍNDICES"] == "Div_liq_pl", "VALOR"].values[0]
    pl_ativos = df_data_dash.loc[df_data_dash["ÍNDICES"] == "PL_ativos", "VALOR"].values[0]
    passivo_ativos = df_data_dash.loc[df_data_dash["ÍNDICES"] == "Passivos_ativos", "VALOR"].values[0]
    Margem_Bruta = df_data_dash.loc[df_data_dash["ÍNDICES"] == "Margem_Bruta", "VALOR"].values[0]
    Div_liq_ebitda = df_data_dash.loc[df_data_dash["ÍNDICES"] == "Div_liq_ebitda", "VALOR"].values[0]
    Ebitda_rec_liq = df_data_dash.loc[df_data_dash["ÍNDICES"] == "Ebitda_rec_liq", "VALOR"].values[0]
    Ebit_rec_liq = df_data_dash.loc[df_data_dash["ÍNDICES"] == "Ebit_rec_liq", "VALOR"].values[0]
    roic = df_data_dash.loc[df_data_dash["ÍNDICES"] == "ROIC", "VALOR"].values[0]
    giro_ativo = df_data_dash.loc[df_data_dash["ÍNDICES"] == "GA", "VALOR"].values[0]
    cagr_receita = df_data_dash.loc[df_data_dash["ÍNDICES"] == "CAGR RECEITAS", "VALOR"].values[0]
    cagr_lucro = df_data_dash.loc[df_data_dash["ÍNDICES"] == "CAGR LUCROS", "VALOR"].values[0]
    Margem_liquida = df_data_dash.loc[df_data_dash["ÍNDICES"] == "Margem_liquida", "VALOR"].values[0]
    roe = df_data_dash.loc[df_data_dash["ÍNDICES"] == "ROE", "VALOR"].values[0]
    roa = df_data_dash.loc[df_data_dash["ÍNDICES"] == "ROA", "VALOR"].values[0]

    # Row 1:
    my_grid.markdown(f"Empresa: {empresa[0]}")
    my_grid.markdown("Indicadores")
    my_grid.empty()

    # Row 2:
    my_grid.markdown(f"{empresa[0]}")
    my_grid.empty()
    my_grid.markdown("Indicadores")
    my_grid.empty()

    # Row 3:
    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12 = st.columns(12)    

    col1.markdown("_Protótipo v0.2.0_")
    col7.metric(label=":blue[DÍV LÍQ/PL]", value=div_liq, delta="0.0%", help=div_pl_help)
    col8.metric(label=":blue[DÍV. LÍQ/EBITDA]", value=Div_liq_ebitda, delta="0.0 %", help=help_div_liq_ebitda)    
    col9.metric(label=":blue[DÍV. LÍQ/EBIT]", value=Div_liq_ebit, delta="0.0 %", help=help_div_liq_ebit)
    col10.metric(label=":blue[PL/ATIVOS]", value=pl_ativos, delta="0.0  %", help=help_pl_ativos)
    col11.metric(label=":blue[PASSIVOS/ATIVOS]", value=passivo_ativos, delta="0.0 %", help=help_passivos_ativos)
    col12.metric(label=":blue[LÍQ. CORRENTE]", value=Liq_corrente, delta="0.0 %", help=help_liq_corrente)
    
    # Row 3:
    m_grid = grid([3,3,2], vertical_align="bottom")
    
    m_grid.markdown("Indicadores de Crescimento - 5 ANOS")
    m_grid.markdown("Indicadores de Eficiência")
    m_grid.markdown("Indicadores de Rentabilidade")
    
    # Row 3:
    colu1, colu2, colu3, colu4, colu5, colu6, colu7, colu8, colu9, colu10, colu11, colu12  = st.columns(12)

    colu1.metric(label=":blue[CAGR RECEITAS]", value=f"{cagr_receita}%", delta="0.0 %", help=cagr_receita_help)
    colu2.metric(label=":blue[CAGR LUCROS]", value=f"{cagr_lucro}%", delta="0.0 %", help=cagr_lucro_help)
    colu4.metric(label=":blue[M. BRUTA %]", value=f"{Margem_Bruta} %", delta="0.0%", help=help_margem_bruta)
    colu5.metric(label=":blue[M. EBITDA]", value=f"{Ebitda_rec_liq} %", delta="0.0%", help=help_margem_ebitda)
    colu6.metric(label=":blue[M. EBIT]", value=f"{Ebit_rec_liq} %", delta="0.0%", help=help_margem_ebit)
    colu7.metric(label=":blue[M. LÍQUIDA]", value=f"{Margem_liquida}%", delta="0.0%", help=help_margem_liquida)
    colu9.metric(label=":blue[ROE]", value=roe, delta="0.0%", help=help_roe)
    colu10.metric(label=":blue[ROA]", value=roa, delta="0.0%", help=help_roa)
    colu11.metric(label=":blue[ROIC]", value=roic, delta="0.0%", help=help_roic)
    colu12.metric(label=":blue[GIRO ATIVOS]", value=giro_ativo, delta="0.0%", help=help_giro_ativos)

    cl1, cl2 = st.columns(2)
    with cl1:        
        grf.grafico_area_margens_dashboard(df)
        ...

    with cl2:
        grf.grafico_area_indicadores_dashboard(df)
        ...

    with st.expander("Para uma nova análise, clique no botão novamente", expanded=True):
        
        # Primeiro botão: 'Gerar Análise'
        if st.button('Gerar Análise', key='botao1'):
            with st.spinner('Gerando análise...'):
                analysis = generate_analysis_dashboard(df_data_dash)
        
            st.success('Análise gerada!')
            st.write(analysis) 

        # Segundo botão: 'Sugestão de Ação Agressiva'
        if st.button('Sugestão de Ação Agressiva', key='botao2'):
            with st.spinner('Gerando sugestão de ação agressiva...'):
                aggressive_analysis = generate_analysis_dashboard_agressiva(df_data_dash)
                
            st.success('Sugestão de ação agressiva gerada!')
            st.write(aggressive_analysis)

        # Terceiro botão: 'Sugestão de Ação Conservadora'
        if st.button('Sugestão de Ação Conservadora', key='botao3'):
            with st.spinner('Gerando sugestão de ação conservadora...'):
                conservative_analysis = generate_analysis_dashboard_conservadora(df_data_dash)
                
            st.success('Sugestão de ação conservadora gerada!')
            st.write(conservative_analysis)
        ############
        user_question = st.text_input("Pergunta:")            
        if st.button("Enviar Pergunta"):
            if user_question:
                with st.spinner('Gerando resposta...'):
                    financial_assistant(user_question, df_data_dash)