import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate)
from langchain.memory import ConversationBufferMemory
import pandas as pd
import helpers.dadoscontabeis as data_contabil

# Initialize session state for 'data' if it does not exist
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame()  # or load your initial data here

df = st.session_state['data']

# Verificar o conteúdo do DataFrame
st.write("Conteúdo do DataFrame (as primeiras linhas):")
st.write(df.head())
nome_arquivo = "./data/EQUATORIAL_ENERGIA.csv"  # Exemplo de caminho

def obter_nome_empresa_e_ramo(nome_arquivo):
    if 'nome_empresa' not in st.session_state or 'ramo' not in st.session_state:
        nome_arquivo_sem_extensao = os.path.splitext(os.path.basename(nome_arquivo))[0]
        partes = nome_arquivo_sem_extensao.split('_')
        
        if len(partes) >= 2:
            nome_empresa = partes[0]
            ramo = '_'.join(partes[1:])
        else:
            nome_empresa = partes[0]
            ramo = ""
        
        st.session_state['nome_empresa'] = nome_empresa
        st.session_state['ramo'] = ramo
    else:
        nome_empresa = st.session_state['nome_empresa']
        ramo = st.session_state['ramo']
    
    return nome_empresa, ramo

indices = {}
if not df.empty:
    df_data_dash = data_contabil.data_dashboard(df)
    indices = {
        "Liq_corrente": df.loc[df["ÍNDICES"] == "Liq_corrente", "VALOR"].values[0],
        "Div_liq_ebit": df.loc[df["ÍNDICES"] == "Div_liq_ebit", "VALOR"].values[0],
        "Div_liq_pl": df.loc[df["ÍNDICES"] == "Div_liq_pl", "VALOR"].values[0],
        "PL_ativos": df.loc[df["ÍNDICES"] == "PL_ativos", "VALOR"].values[0],
        "Passivos_ativos": df.loc[df["ÍNDICES"] == "Passivos_ativos", "VALOR"].values[0],
        "Margem_Bruta": df.loc[df["ÍNDICES"] == "Margem_Bruta", "VALOR"].values[0],
        "Div_liq_ebitda": df.loc[df["ÍNDICES"] == "Div_liq_ebitda", "VALOR"].values[0],
        "Ebitda_rec_liq": df.loc[df["ÍNDICES"] == "Ebitda_rec_liq", "VALOR"].values[0],
        "Ebit_rec_liq": df.loc[df["ÍNDICES"] == "Ebit_rec_liq", "VALOR"].values[0],
        "ROIC": df.loc[df["ÍNDICES"] == "ROIC", "VALOR"].values[0],
        "GA": df.loc[df["ÍNDICES"] == "GA", "VALOR"].values[0],
        "CAGR RECEITAS": df.loc[df["ÍNDICES"] == "CAGR RECEITAS", "VALOR"].values[0],
        "CAGR LUCROS": df.loc[df["ÍNDICES"] == "CAGR LUCROS", "VALOR"].values[0],
        "Margem_liquida": df.loc[df["ÍNDICES"] == "Margem_liquida", "VALOR"].values[0],
        "ROE": df.loc[df["ÍNDICES"] == "ROE", "VALOR"].values[0],
        "ROA": df.loc[df["ÍNDICES"] == "ROA", "VALOR"].values[0]
    }

def initialize_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

def financial_assistant(user_question, df=None, indices=None):
    nome_empresa, ramo = obter_nome_empresa_e_ramo(nome_arquivo)
    # Inicializar chat_history se não existir
    initialize_chat_history()

    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    if not OPENAI_API_KEY:
        st.error("API Key for OpenAI is missing. Please check your .env file.")
        return

    # Definir a memória da conversa
    memory = ConversationBufferMemory(return_messages=True)

    if indices is None:
        indices = {}

    indices_str = "\n".join([f"{key}: {value}" for key, value in indices.items()])

    # Adicionar informações do DataFrame ao contexto, se fornecido
    df_context = ""
    if df is not None and not df.empty:
        df_context = df # Mostrar as duas primeiras linhas do DataFrame para verificação

    
    system_template = f"""
    Você é um assistente financeiro. Utilize as seguintes informações de contexto para responder às perguntas dos usuários. 
    Se você não souber a resposta, forneça a melhor resposta possível baseada nas informações disponíveis e sugira ao usuário onde ele pode encontrar mais detalhes.

    **Contexto da Empresa**:
    A empresa que você vai analisar é {nome_empresa}, atuando no ramo de {ramo}.

    **Informações de Contexto Geral**:
    1. O mercado de ações é um componente essencial da economia global.
    2. A diversificação é uma estratégia fundamental para reduzir riscos em investimentos.
    3. As taxas de juros influenciam diretamente os preços dos títulos e ações.
    4. O planejamento financeiro inclui a gestão de receitas, despesas, investimentos e aposentadoria.
    5. A análise fundamentalista e técnica são métodos comuns para avaliar ações.
    6. A poupança de emergência deve cobrir pelo menos seis meses de despesas essenciais.
    7. Os impostos sobre investimentos variam dependendo do país e do tipo de investimento.
    8. O risco de crédito é a possibilidade de um tomador de empréstimo não cumprir suas obrigações de pagamento.
    9. A inflação corrói o poder de compra do dinheiro ao longo do tempo.
    10. A liquidez de um ativo refere-se à facilidade com que ele pode ser convertido em dinheiro sem perda significativa de valor.
    11. A alavancagem financeira pode aumentar os retornos, mas também os riscos de um investimento.
    12. Investimentos em moedas estrangeiras e riscos cambiais.
    13. Investimento socialmente responsável (ESG).

    **Fontes de Informação**:
    - ANEEL: https://www.aneel.gov.br/
    - O Setor Elétrico: https://www.osetoreletrico.com.br/
    - Investing.com: https://www.investing.com/
    - Trading Economics: https://tradingeconomics.com/
    - Relatórios financeiros das Empresas de {ramo}.

    **Indicadores Específicos**:
    - Olhe os indicadores DEC e FEC caso seja perguntado. DEC (Duração Equivalente de Interrupção por Unidade Consumidora) e FEC (Frequência Equivalente de Interrupção por Unidade Consumidora) são usados para medir a qualidade do serviço de distribuição de energia elétrica, conforme definido pela ANEEL.
    - O balanço patrimonial fornece uma visão geral da saúde financeira de uma empresa, incluindo ativos, passivos e patrimônio líquido.
    - Indicadores financeiros como margem de lucro, retorno sobre o investimento (ROI) e liquidez corrente são cruciais para avaliar a performance de uma empresa.
    - Resultados financeiros trimestrais e anuais são essenciais para monitorar o desempenho e a sustentabilidade de uma empresa.
    - Dívidas elevadas podem impactar a capacidade de uma empresa de investir em infraestrutura e manutenção, resultando em um desempenho pior nos indicadores DEC e FEC. É importante comparar esses indicadores entre distribuidoras para avaliar a eficiência e a qualidade do serviço prestado.
    - Indicadores de energia, como eficiência energética, perdas na transmissão e distribuição, e o consumo de energia por setor, são importantes para analisar o desempenho das empresas do setor elétrico.

    **Informações do DataFrame**:
    Aqui estão alguns índices financeiros da empresa:
    {indices_str}

    Informações adicionais do DataFrame:
    {df_context}

    Agora, responda à pergunta do usuário da melhor maneira possível.
    """
    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{question}"),
    ]
    prompt = ChatPromptTemplate.from_messages(messages)

    # Use um modelo ChatOpenAI
    llm = ChatOpenAI(model_name='gpt-4', max_tokens=4000, temperature=0, openai_api_key=OPENAI_API_KEY)

    # Gerar a mensagem completa a ser enviada para o modelo
    formatted_messages = prompt.format_messages(question=user_question)

    # Obter a resposta do modelo
    response = llm(formatted_messages)

    # Atualizar a memória com a resposta do modelo
    memory.save_context({"input": user_question}, {"response": response.content})

    # Exibir a resposta ao usuário
    st.write(f"**Resposta do Assistente:** {response.content}")

# Testando a função no Streamlit
user_question = st.text_input("Pergunta:")

if st.button("Enviar Pergunta"):
    if user_question:
        with st.spinner('Gerando resposta...'):
            financial_assistant(user_question, df_data_dash, indices)
