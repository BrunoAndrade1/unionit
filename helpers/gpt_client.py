import openai
import streamlit as st
import pandas as pd
import numpy as np
import re
import os
from dotenv import load_dotenv

import helpers.dadoscontabeis as data_contabil


load_dotenv()

# Inicialização da API 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


nome_arquivo = "./data/EQUATORIAL_ENERGIA.csv"  
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

# # Extraindo o nome da empresa do caminho do arquivo
# nome_empresa = os.path.splitext(os.path.basename(nome_arquivo))[0]
# # Armazenando o nome da empresa no session_state
# st.session_state['nome_empresa'] = nome_empresa


def generate_analysis_dashboard(df):
    # if 'nome_empresa' not in st.session_state:
    #     nome_arquivo = "./data/EQUATORIAL.csv"  # Certifique-se de que este caminho esteja correto
    #     nome_empresa = os.path.splitext(os.path.basename(nome_arquivo))[0]
    #     st.session_state['nome_empresa'] = nome_empresa

    nome_empresa, ramo = obter_nome_empresa_e_ramo(nome_arquivo)
    
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
    
    # Texto de entrada para o modelo
    input_text = (
            f"Com base nos seguintes índices financeiros: {indices}, forneça uma análise explícita, período a período, sobre os índices apresentados e possíveis diagnósticos financeiros. "
            f"Aqui está o que cada sigla significa: \n"
            f"- Liq_corrente: liquidez corrente\n"
            f"- Div_liq_ebit: dívida líquida da empresa dividida pelo EBIT atual\n"
            f"- Div_liq_pl: dívida líquida dividida pelo patrimônio líquido\n"
            f"- PL_ativos: patrimônio líquido dividido pelos ativos\n"
            f"- Passivos_ativos: passivos divididos pelos ativos\n"
            f"- Margem_Bruta: margem bruta\n"
            f"- Div_liq_ebitda: dívida líquida dividida pelo EBITDA\n"
            f"- Ebitda_rec_liq: receita líquida EBITDA\n"
            f"- Ebit_rec_liq: receita líquida EBIT\n"
            f"- ROIC: retorno sobre o capital investido\n"
            f"- GA: giro dos ativos\n"
            f"- CAGR RECEITAS: Taxa composta de crescimento anual das receitas\n"
            f"- CAGR LUCROS: Taxa composta de crescimento anual dos lucros\n"
            f"- Margem_liquida: margem líquida\n"
            f"- ROE: Retorno sobre o patrimônio líquido\n"
            f"- ROA: Retorno sobre os ativos\n"
            f"Não mencione as siglas no texto da análise, apenas seus significados. Os dados apresentados se referem A {nome_empresa}, que atua no setor de {ramo}. "
            f"Faça a análise dos indicadores em relação a dados históricos setoriais, como a Abicalçados e Relatórios de Relações com Investidores (RI) da própria {nome_empresa}."
        )
    # Solicitar uma resposta do modelo gpt-3.5-turbo
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system", 
             "content": "Você é um assistente financeiro que fornece análises detalhadas e explicativas." 
            },
            {
                "role": "user",
                "content": input_text
            }
        ],
        max_tokens=1600
    )
    
    return response.choices[0].message.content


def generate_analysis_dashboard_agressiva(df):
    # if 'nome_empresa' not in st.session_state:
    #     nome_arquivo = "./data/EQUATORIAL.csv"  # Certifique-se de que este caminho esteja correto
    #     nome_empresa = os.path.splitext(os.path.basename(nome_arquivo))[0]
    #     st.session_state['nome_empresa'] = nome_empresa

    nome_empresa, ramo = obter_nome_empresa_e_ramo(nome_arquivo)
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
    
    # Gerar a análise com o gpt-3.5-turbo
    #input_text = f"Com base nos seguintes índices financeiros: {indices}, forneça uma sugestão de ações administrativas agressivas para melhorar o desempenho da empresa. Você pode se basear nos dados apresentados e também em análises da APIMEC (Associação dos Analistas e profissionais de investimento do mercado de capitais) e na IBRI (Instituto Brasileiro de Relação com Investidores). Aqui está o que cada sigla signifca apresentada no dataframe: Liq_corrente = liquidez corrente, Div_liq_ebit = divida liquida da empresa dividido pelo ebit atual, Div_liq_pl = divida liquida dividido pelo patrimônio liquido, PL_ativos = patrimonio liquido dividido pelos ativos, Passivos_ativos = passivos divididos pelos ativos, Margem_Bruta = margem bruta, Margem_liquida = margem líquida, Div_liq_ebitda = divida líquida dividida pelo ebitda, Ebit_rec_liq = receita liquida Ebit, Ebitda_rec_liq = receita liquida Ebitda, ROIC = retorno no capital investido, GA = giros ativos, CAGR RECEITAS = receitas da Taxa composta de crescimento anual, CAGR LUCROS = lucro da Taxa composta de crescimento anual, Margem_liquida = margem líquida, ROE = Retorno sobre patrimônio líquido, ROA = Retorno sobre ativos. Não mencionar as siglas no texto da análise, apenas seus significados. Os dados apresentados se referem ao grupo brasileiro {nome_empresa} que atua no ramo de calçados e roupas. Para a sugestão de ações administrativas agressivas, leve em consideração também os dados históricos setoriais como os dados da Abicalçados e Relatórios de Relações com Investidores (RI) da própria {nome_empresa}."
    input_text = (
        f"Com base nos seguintes índices financeiros: {indices}, forneça uma sugestão de ações administrativas agressivas para melhorar o desempenho da empresa. "
        f"Você pode se basear nos dados apresentados e também em análises da APIMEC (Associação dos Analistas e Profissionais de Investimento do Mercado de Capitais) "
      
        f"Não mencione as siglas no texto da análise, apenas seus significados. Os dados apresentados se referem ao grupo brasileiro {nome_empresa}, que atua no ramo de {ramo}. "
        f"Para a sugestão de ações administrativas agressivas, leve em consideração também os dados históricos setoriais, como os dados da Abicalçados e Relatórios de Relações com Investidores (RI) da própria {nome_empresa}."
    )
    # Solicitar uma resposta do modelo gpt-3.5-turbo
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro que fornece análises detalhadas e explicativas."},
            {"role": "user", "content": input_text}
        ],
        max_tokens=1600
    )
    return response.choices[0].message.content

def generate_analysis_dashboard_conservadora(df):
    nome_empresa, ramo = obter_nome_empresa_e_ramo(nome_arquivo)
    # Extração dos índices
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
    
    # Gerar a análise com o gpt-3.5-turbo
    #input_text = f"Com base nos seguintes índices financeiros: {indices}, forneça uma sugestão de ações administrativas conservadoras para melhorar o desempenho da empresa. Você pode se basear nos dados apresentados e também em análises da APIMEC (Associação dos Analistas e profissionais de investimento do mercado de capitais) e na IBRI (Instituto Brasileiro de Relação com Investidores). Aqui está o que cada sigla signifca apresentada no dataframe: Liq_corrente = liquidez corrente, Div_liq_ebit = divida liquida da empresa dividido pelo ebit atual, Div_liq_pl = divida liquida dividido pelo patrimônio liquido, PL_ativos = patrimonio liquido dividido pelos ativos, Passivos_ativos = passivos divididos pelos ativos, Margem_Bruta = margem bruta, Margem_liquida = margem líquida, Div_liq_ebitda = divida líquida dividida pelo ebitda, Ebit_rec_liq = receita liquida Ebit, Ebitda_rec_liq = receita liquida Ebitda, ROIC = retorno no capital investido, GA = giros ativos, CAGR RECEITAS = receitas da Taxa composta de crescimento anual, CAGR LUCROS = lucro da Taxa composta de crescimento anual, Margem_liquida = margem líquida, ROE = Retorno sobre patrimônio líquido, ROA = Retorno sobre ativos. Não mencionar as siglas no texto da análise, apenas seus significados. Os dados apresentados se referem ao grupo brasileiro Arezzo que atua no ramo de calçados e roupas. Para a sugestão de ações administrativas conservadoras, leve em consideração também os dados históricos setoriais como os dados da Abicalçados e Relatórios de Relações com Investidores (RI) da própria Arezzo."
    input_text = (
    f"Com base nos seguintes índices financeiros: {indices}, forneça sugestões de ações administrativas conservadoras para melhorar o desempenho da empresa. "
    f"Você pode se basear tanto nos dados apresentados quanto em análises da APIMEC (Associação dos Analistas e Profissionais de Investimento do Mercado de Capitais) "
    f"e do IBRI (Instituto Brasileiro de Relação com Investidores). Aqui estão os significados das siglas apresentadas no dataframe: "
    f"Liq_corrente = liquidez corrente, Div_liq_ebit = dívida líquida da empresa dividida pelo EBIT atual, Div_liq_pl = dívida líquida dividida pelo patrimônio líquido, "
    f"PL_ativos = patrimônio líquido dividido pelos ativos, Passivos_ativos = passivos divididos pelos ativos, Margem_Bruta = margem bruta, Margem_liquida = margem líquida, "
    f"Div_liq_ebitda = dívida líquida dividida pelo EBITDA, Ebit_rec_liq = receita líquida EBIT, Ebitda_rec_liq = receita líquida EBITDA, ROIC = retorno sobre o capital investido, "
    f"GA = giros de ativos, CAGR RECEITAS = taxa composta anual de crescimento das receitas, CAGR LUCROS = taxa composta anual de crescimento dos lucros, "
    f"Margem_liquida = margem líquida, ROE = retorno sobre o patrimônio líquido, ROA = retorno sobre os ativos. Não mencione as siglas no texto da análise, apenas seus significados. "
    f"Os dados apresentados referem-se à {nome_empresa}, que atua no ramo de {ramo}. Para as sugestões de ações administrativas conservadoras,"

    
)
    # Solicitar uma resposta do modelo gpt-3.5-turbo
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro que fornece análises detalhadas e explicativas."},
            {"role": "user", "content": input_text}
        ],
        max_tokens=1600
    )    
    return response.choices[0].message.content

def generate_analises_indicadores(df):
    nome_empresa, ramo = obter_nome_empresa_e_ramo(nome_arquivo)
    input_text = (
        f"Por favor, forneça uma análise detalhada baseada nas seguintes métricas: {df}. "
        f"Os dados são referentes {nome_empresa} do {ramo} "
        f"Faça a análise explícita período a período dos indicadores em relação a dados históricos setoriais como a Abicalçados "
        f"e Relatórios de Relações com Investidores (RI) da própria {nome_empresa}."
    )
    # Solicitar uma resposta do modelo gpt-3.5-turbo
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro que fornece análises detalhadas e explicativas."},
            {"role": "user", "content": input_text}
        ],
        max_tokens=1600
    )
    return response.choices[0].message.content

def generate_analises_indicadores_agressiva(df):
    nome_empresa, ramo = obter_nome_empresa_e_ramo(nome_arquivo)
    input_text = (
        f"Por favor, forneça uma análise detalhada baseada nas seguintes métricas: {df}. "
        f"Os dados são referentes ao grupo brasileiro {nome_empresa} que atua no {ramo}. "
        f"Faça a análise explícita período a período dos indicadores em relação a dados históricos setoriais como a Abicalçados "
        f"e Relatórios de Relações com Investidores (RI) da própria {nome_empresa} do `{ramo}."
    )

    # Realizar chamada ao GPT-3
    # Solicitar uma resposta do modelo gpt-3.5-turbo
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro que fornece análises detalhadas e explicativas."},
            {"role": "user", "content": input_text}
        ],
        max_tokens=1600
    )
    return response.choices[0].message.content

def generate_analises_indicadores_conservadora(df):
    nome_empresa, ramo = obter_nome_empresa_e_ramo(nome_arquivo)
    # input_text = (
    #     f"Com base nas seguintes métricas: {df}, forneça uma sugestão de ações administrativas conservadoras para melhorar o desempenho da empresa. Os dados são referentes ao grupo brasileiro Arezzo que atua no ramo de calçados e roupas. Você pode se basear nos dados apresentados neste dataframe e também em análises da APIMEC (Associação dos Analistas e profissionais de investimento do mercado de capitais), na IBRI (Instituto Brasileiro de Relação com Investidores), Abicalçados e Relatórios de Relações com Investidores (RI) da própria Arezzo para a sugestão de ações administrativas conservadoras."
    # )
    input_text = (
        f"Com base nas seguintes métricas: {df}, forneça sugestões de ações administrativas conservadoras para melhorar o desempenho da empresa. "
        f"Os dados referem-se ao grupo brasileiro {nome_empresa}, que atua no ramo de {ramo}. Você pode se basear nas informações apresentadas neste dataframe "
        f"e também em análises da APIMEC (Associação dos Analistas e Profissionais de Investimento do Mercado de Capitais), na IBRI (Instituto Brasileiro de Relação "
        f"com Investidores), na Abicalçados e em Relatórios de Relações com Investidores (RI) da própria {nome_empresa} para formular suas sugestão de ações administrativas conservadoras."
    )

    # Realizar chamada ao GPT-3
    # Solicitar uma resposta do modelo gpt-3.5-turbo
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro que fornece análises detalhadas e explicativas."},
            {"role": "user", "content": input_text}
        ],
        max_tokens=1600
    )
    return response.choices[0].message.content

def generate_analises_dre(df, tipo_analise):
    nome_empresa, ramo = obter_nome_empresa_e_ramo(nome_arquivo)
    analysis_type_description = {
        "AH": "análise horizontal do DRE",
        "AV": "análise vertical do DRE",
        "DATA": "dados básicos do DRE"  
    }.get(tipo_analise, "dados do DRE")  
    
    print(analysis_type_description)

    # input_text = (
    #     f"Por favor, forneça uma análise detalhada baseada nas seguintes métricas para {analysis_type_description} referente ao dataframe:\n"
    #     f"{df}. \n\n"        
    #     "Favor observar os nomes das linhas no texto acima. "
    #     "Estes dados são referentes ao DRE (Demonstração do Resultado de Exercício) do grupo brasileiro Arezzo, "
    #     "que atua no ramo de calçados e roupas. "
    #     "Faça a análise explícita período a período dos dados do DRE em relação a dados históricos setoriais, "
    #     "como os da Abicalçados e Relatórios de Relações com Investidores (RI) da própria Arezzo."
    # )

    input_text = (
        f"Por favor, forneça uma análise detalhada baseada nas seguintes métricas para {analysis_type_description}, conforme o dataframe abaixo:\n"
        f"{df}\n\n"
        f"Observe os nomes das linhas no texto acima. "
        f"Os dados referem-se ao DRE (Demonstração do Resultado de Exercício) do grupo brasileiro {nome_empresa}, "
        f"que atua no ramo de {ramo}. "
        f"Faça uma análise detalhada, período a período, dos dados do DRE em comparação com dados históricos setoriais, "
        f"como os da Abicalçados e Relatórios de Relações com Investidores (RI) da própria {nome_empresa}."
    )

    # Realizar chamada ao GPT (use sua chamada de API conforme sua implementação)
    # Solicitar uma resposta do modelo gpt-3.5-turbo
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro que fornece análises detalhadas e explicativas."},
            {"role": "user", "content": input_text}
        ],
        max_tokens=1600
    )
    return response.choices[0].message.content

def generate_analises_dre_agressiva(df, tipo_analise):   
    nome_empresa, ramo = obter_nome_empresa_e_ramo(nome_arquivo)
    analysis_type_description = {
        "AH": "análise horizontal do DRE",
        "AV": "análise vertical do DRE",
        "DATA": "dados básicos do DRE"  
    }.get(tipo_analise, "dados do DRE")  
    
    #print(analysis_type_description) 

    # input_text = (
    #     f"Por favor, forneça uma sugestão de ações administrativas agressivas para melhorar o desempenho da empresa baseado nas métricas para {analysis_type_description} do dataframe: \n"
    #     f"{df}. \n\n"        
    #     "Favor observar os nomes das linhas no texto acima. "
    #     "Estes dados são referentes ao DRE (Demonstração do Resultado de Exercício) do grupo brasileiro Arezzo, "
    #     "que atua no ramo de calçados e roupas. "
    #     "Forneça uma sugestão de ações administrativas agressivas baseadas nos dados fornecidos do DRE. Você pode se basear nos dados apresentados neste dataframe e também em análises da APIMEC (Associação dos Analistas e profissionais de investimento do mercado de capitais), na IBRI (Instituto Brasileiro de Relação com Investidores), Abicalçados e Relatórios de Relações com Investidores (RI) da própria Arezzo para a sugestão de ações administrativas agressivas."
    #     )
    input_text = (
        f"Por favor, forneça uma sugestão de ações administrativas agressivas para melhorar o desempenho da empresa {nome_empresa}, "
        f"baseado nas métricas para {analysis_type_description} apresentadas no dataframe abaixo:\n"
        f"{df}\n\n"
        "Observe os nomes das linhas no texto acima. "
        "Os dados referem-se ao DRE (Demonstração do Resultado de Exercício) do {nome_empresa}"
        "que atua no {ramo}. "
        "Forneça sugestões de ações administrativas agressivas com base nos dados do DRE. "
        "Você pode considerar também análises da APIMEC (Associação dos Analistas e Profissionais de Investimento do Mercado de Capitais), "
        "da IBRI (Instituto Brasileiro de Relação com Investidores), da Abicalçados e dos Relatórios de Relações com Investidores (RI) da própria {nome_empresa}"
    )



    # Realizar chamada ao GPT (use sua chamada de API conforme sua implementação)
    # Solicitar uma resposta do modelo gpt-3.5-turbo
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro que fornece análises detalhadas e explicativas."},
            {"role": "user", "content": input_text}
        ],
        max_tokens=1600
    )
    return response.choices[0].message.content

def generate_analises_dre_conservadora(df, tipo_analise):
    nome_empresa, ramo = obter_nome_empresa_e_ramo(nome_arquivo)    
    analysis_type_description = {
        "AH": "análise horizontal do DRE",
        "AV": "análise vertical do DRE",
        "DATA": "dados básicos do DRE"  
    }.get(tipo_analise, "dados do DRE")  
    
    #print(analysis_type_description) 
    # input_text = (
    #     f"Por favor, forneça uma sugestão de ações administrativas conservadoras para melhorar o desempenho da empresa baseado nas métricas para {analysis_type_description} do dataframe: \n"
    #     f"{df}. \n\n"        
    #     "Favor observar os nomes das linhas no texto acima. "
    #     "Estes dados são referentes ao DRE (Demonstração do Resultado de Exercício) do grupo brasileiro Arezzo, "
    #     "que atua no ramo de calçados e roupas. "
    #     "Forneça uma sugestão de ações administrativas conservadoras baseadas nos dados fornecidos do DRE. Você pode se basear nos dados apresentados neste dataframe e também em análises da APIMEC (Associação dos Analistas e profissionais de investimento do mercado de capitais), na IBRI (Instituto Brasileiro de Relação com Investidores), Abicalçados e Relatórios de Relações com Investidores (RI) da própria Arezzo para a sugestão de ações administrativas conservadoras."
    # )
    input_text = (
    f"Por favor, forneça uma sugestão de ações administrativas conservadoras para melhorar o desempenho da empresa, "
    f"baseada nas métricas para {analysis_type_description} do dataframe abaixo:\n"
    f"{df}\n\n"
    "Observe os nomes das linhas no texto acima. "
    f"Os dados referem-se ao DRE (Demonstração do Resultado de Exercício) do grupo brasileiro {nome_empresa}, "
    f"que atua no ramo de {ramo}. "
    "Forneça uma sugestão de ações administrativas conservadoras com base nos dados fornecidos do DRE. "
    "Você pode se basear nos dados apresentados neste dataframe, assim como em análises da APIMEC (Associação dos Analistas e Profissionais de Investimento do Mercado de Capitais), "
    "da IBRI (Instituto Brasileiro de Relação com Investidores), Abicalçados e Relatórios de Relações com Investidores (RI) da própria {nome_empresa}."
)
    
    # Realizar chamada ao GPT (use sua chamada de API conforme sua implementação)
    # Solicitar uma resposta do modelo gpt-3.5-turbo
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro que fornece análises detalhadas e explicativas."},
            {"role": "user", "content": input_text}
        ],
        max_tokens=1600
    )
    return response.choices[0].message.content

def generate_analises_bp(df, tipo_analise):
    nome_empresa, ramo = obter_nome_empresa_e_ramo(nome_arquivo)
    analysis_type_description = {
        "AH": "análise horizontal do Balanço Patrimonial",
        "AV": "análise vertical do Balanço Patrimonial",
        "DATA": "dados básicos do Balanço Patrimonial"  
    }.get(tipo_analise, "dados do Balanço Patrimonial")  
    
    # input_text = (
    #     f"Por favor, forneça uma análise detalhada baseada nas seguintes métricas para a {analysis_type_description} referente ao dataframe:\n"
    #     f"{df}.\n\n"
    #     "Favor observar os nomes das linhas no texto acima. "
    #     "Estes dados são referentes ao Balanço Patrimonial do grupo brasileiro Arezzo, "
    #     "que atua no ramo de calçados e roupas. "
    #     "Faça a análise explícita período a período dos dados do Balanço Patrimonial em relação a dados históricos setoriais, "
    #     "como os da Abicalçados e Relatórios de Relações com Investidores (RI) da própria Arezzo. Quando o período selecionado for maior que 5 anos, resumir a análise."
    # )
    input_text = (
    f"Por favor, forneça uma análise detalhada baseada nas seguintes métricas para {analysis_type_description} do dataframe abaixo:\n"
    f"{df}\n\n"
    "Observe os nomes das linhas no texto acima. "
    f"Os dados referem-se ao Balanço Patrimonial do grupo brasileiro {nome_empresa}, "
    f"que atua no ramo de {ramo}. "
    "Faça uma análise explícita período a período dos dados do Balanço Patrimonial em relação a dados históricos setoriais, "
    "como os da Abicalçados e Relatórios de Relações com Investidores (RI) da própria {nome_empresa}. "
    "Se o período analisado for superior a 5 anos, forneça um resumo da análise."
)


    # Solicitar uma resposta do modelo gpt-3.5-turbo
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro que fornece análises detalhadas e explicativas."},
            {"role": "user", "content": input_text}
        ],
        max_tokens=1600
    )
    return response.choices[0].message.content

def generate_analises_bp_agressiva(df, tipo_analise):
    nome_empresa, ramo = obter_nome_empresa_e_ramo(nome_arquivo)
    analysis_type_description = {
        "AH": "análise horizontal do Balanço Patrimonial",
        "AV": "análise vertical do Balanço Patrimonial",
        "DATA": "dados básicos do Balanço Patrimonial"  
    }.get(tipo_analise, "dados do Balanço Patrimonial")  
        
    # input_text = (
    #     f"Por favor, forneça uma sugestão de ações administrativas agressivas para melhorar o desempenho da empresa baseado em {analysis_type_description} referente ao dataframe:\n"
    #     f"{df}.\n\n"
    #     "Favor observar os nomes das linhas no texto acima. "
    #     "Estes dados são referentes ao Balanço Patrimonial do grupo brasileiro Arezzo, "
    #     "que atua no ramo de calçados e roupas. "
    #     "Forneça uma sugestão de ações administrativas agressivas baseadas nos dados fornecidos do Balanço Patrimonial. "
    #     "Você pode se basear nos dados apresentados neste dataframe e também em análises da APIMEC (Associação dos Analistas e profissionais de investimento do mercado de capitais), na IBRI (Instituto Brasileiro de Relação com Investidores), Abicalçados e Relatórios de Relações com Investidores (RI) da própria Arezzo para a sugestão de ações administrativas agressivas."
    # )
    input_text = (
    f"Por favor, forneça uma sugestão de ações administrativas agressivas para melhorar o desempenho da empresa com base em {analysis_type_description} referente ao dataframe abaixo:\n"
    f"{df}\n\n"
    "Observe os nomes das linhas no texto acima. "
    f"Os dados referem-se ao Balanço Patrimonial do grupo brasileiro {nome_empresa}, "
    f"que atua no ramo de {ramo}. "
    "Forneça uma sugestão de ações administrativas agressivas com base nos dados fornecidos do Balanço Patrimonial. "
    "Você pode se basear nos dados apresentados neste dataframe e também em análises da APIMEC (Associação dos Analistas e Profissionais de Investimento do Mercado de Capitais), "
    "na IBRI (Instituto Brasileiro de Relação com Investidores), Abicalçados e Relatórios de Relações com Investidores (RI) da própria {nome_empresa} para a sugestão de ações administrativas agressivas."
)

    # Solicitar uma resposta do modelo gpt-3.5-turbo
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro que fornece análises detalhadas e explicativas."},
            {"role": "user", "content": input_text}
        ],
        max_tokens=1600
    )
    return response.choices[0].message.content

def generate_analises_bp_conservadora(df, tipo_analise):
    nome_empresa, ramo = obter_nome_empresa_e_ramo(nome_arquivo)
    analysis_type_description = {
        "AH": "análise horizontal do Balanço Patrimonial",
        "AV": "análise vertical do Balanço Patrimonial",
        "DATA": "dados básicos do Balanço Patrimonial"  
    }.get(tipo_analise, "dados do Balanço Patrimonial")  
        
    # input_text = (
    #     f"Por favor, forneça uma sugestão de ações administrativas conservadoras para melhorar o desempenho da empresa baseado em {analysis_type_description} referente ao dataframe:\n"
    #     f"{df}.\n\n"
    #     "Favor observar os nomes das linhas no texto acima. "
    #     "Estes dados são referentes ao Balanço Patrimonial do grupo brasileiro Arezzo, "
    #     "que atua no ramo de calçados e roupas. "
    #     "Forneça uma sugestão de ações administrativas conservadoras baseadas nos dados fornecidos do Balanço Patrimonial. "
    #     "Você pode se basear nos dados apresentados neste {df} e
    #  também em análises da APIMEC (Associação dos Analistas e profissionais
    #  de investimento do mercado de capitais), na IBRI (Instituto Brasileiro de Relação com Investidores), 
    # Abicalçados e Relatórios de Relações com Investidores (RI) da própria {nome_empresa} para a sugestão de ações administrativas conservadoras."
    # )

    input_text = (
    f"Por favor, forneça uma sugestão de ações administrativas conservadoras para melhorar o desempenho da empresa com base em {analysis_type_description} referente ao dataframe abaixo:\n"
    f"{df}\n\n"
    "Observe os nomes das linhas no texto acima. "
    f"Os dados referem-se ao Balanço Patrimonial do grupo brasileiro {nome_empresa}, "
    f"que atua no ramo de {ramo}. "
    "Forneça sugestões de ações administrativas conservadoras com base nos dados fornecidos do Balanço Patrimonial. "
    "Você pode se basear também em análises da APIMEC (Associação dos Analistas e Profissionais de Investimento do Mercado de Capitais), "
    "na IBRI (Instituto Brasileiro de Relação com Investidores), Abicalçados e Relatórios de Relações com Investidores (RI) da própria {nome_empresa} para a sugestão de ações administrativas conservadoras."
)



    # Solicitar uma resposta do modelo gpt-3.5-turbo
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro que fornece análises detalhadas e explicativas."},
            {"role": "user", "content": input_text}
        ],
        max_tokens=1600
    )
    return response.choices[0].message.content
