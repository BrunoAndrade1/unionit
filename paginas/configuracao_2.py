import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
import os
import streamlit as st
import pandas as pd
import os

path = 'api_contabil_TESTE\\data\\dados.csv'
print(path)
def preencher_contas_existentes(data_df):
    # Carrega o DataFrame existente que já possui as contas preenchidas
    try:
        df_existente = pd.read_csv("caminho_para_arquivo_existente.csv")
        st.write("Arquivo existente carregado com sucesso.")
    except FileNotFoundError:
        st.write("Arquivo existente não encontrado. Criando novo.")
        df_existente = pd.DataFrame(columns=['CONTA', 'DESCRIÇÃO', 'CONTA_DESCRICAO'])

    # Verifica o conteúdo do DataFrame existente
    st.write("Conteúdo do DataFrame existente:", df_existente.head())

    # Cria um dicionário para mapear contas já existentes para suas descrições
    conta_para_descricao = dict(zip(df_existente['CONTA'], df_existente['CONTA_DESCRICAO']))
    st.write("Mapeamento de contas para descrições:", conta_para_descricao)

    # Itera sobre as linhas do DataFrame importado
    for index, row in data_df.iterrows():
        conta = row['CONTA']
        # Se a conta já existir no DataFrame existente, preencha a descrição
        if conta in conta_para_descricao:
            data_df.at[index, 'CONTA_DESCRICAO'] = conta_para_descricao[conta]
            st.write(f"Conta {conta} preenchida com {conta_para_descricao[conta]}")

    return data_df


def inicializar_session():
    if 'tipo_arquivo' not in st.session_state:
        st.session_state['tipo_arquivo'] = ""

    if 'delimitador' not in st.session_state:
        st.session_state['delimitador'] = ""

    if 'encoding' not in st.session_state:
        st.session_state['encoding'] = ""

    if 'periodo' not in st.session_state:
        st.session_state['periodo'] = None
    
    if 'mes_exercicio' not in st.session_state:
        st.session_state['mes_exercicio'] = ""

    if 'ano_exercicio' not in st.session_state:
        st.session_state['ano_exercicio'] = ""

    if 'empresa' not in st.session_state:
        st.session_state['empresa'] = ""

    if 'cnpj' not in st.session_state:
        st.session_state['cnpj'] = ""

    if 'conta' not in st.session_state:
        st.session_state['conta'] = None

    if 'colunas' not in st.session_state:
        st.session_state['colunas'] = ""

    if 'descricao_conta' not in st.session_state:
        st.session_state['descricao_conta'] = None

    if 'valor' not in st.session_state:
        st.session_state['valor'] = None

    if 'novo_df' not in st.session_state:
        st.session_state['novo_df'] = ""

@st.dialog("Aviso")
def aviso(texto, tipo):
    if tipo == "sucesso":
        st.success(texto, icon="✅")
    elif tipo == "erro":
        st.warning(texto, icon="⚠️")

def separador_arquivo():
    # Lê o delimitador selecionado
    file_delimiter = st.session_state['delimitador']
    if file_delimiter == "Vírgula":
        sep = ","
    elif file_delimiter == "Ponto e Vírgula":
        sep = ";"
    return sep

@st.dialog("Carregar Arquivo")
def carregar_arquivo():
    # Cria o objeto
    arquivo_carregado = st.file_uploader("Inserir", type={"csv", "txt"})

    # Verifica se o arquivo foi carregado
    if arquivo_carregado is not None:     
        
        delimitador_escolhido = separador_arquivo()

        # Verifica do tipo do arquivo
        if st.session_state['tipo_arquivo'] == ".csv":
            try:
                # Lê o arquivo com o pandas e armazena
                df = pd.read_csv(arquivo_carregado, 
                                sep = delimitador_escolhido, 
                                encoding= st.session_state['encoding'],
                                on_bad_lines='warn'
                                )
                if 'arquivo_carregado' not in st.session_state:                    
                    st.session_state['arquivo_carregado'] = df
                    st.session_state['colunas'] = df.columns                
                    st.success('Arquivo carregado com sucesso', icon="✅")
            except:
                st.error('Erro ao carregar, volte a página de configuração e verifique os dados salvos', icon="🚨")

    if st.button("Fechar"):
        st.rerun()

# @st.cache_data
def ler_dados_conta():  
    if 'arquivo_carregado' in st.session_state:
        # Ler dados carregados
        data = st.session_state['arquivo_carregado']
        # Cria coluna 
        data['CONTA_DESCRICAO'] = ""

        # Verificar se as colunas existem no DataFrame
        coluna_conta = st.session_state['conta']
        coluna_descricao = st.session_state['descricao_conta']

        if coluna_conta not in data.columns or coluna_descricao not in data.columns:
            st.error("As colunas especificadas não existem no DataFrame.")
            return []

        # Concatenar as colunas 'CONTA' e 'DESCRIÇÃO' em uma nova coluna 'CONTA_DESCRICAO'
        data['CONTA_DESCRICAO'] = data[coluna_conta].astype(str) + ' - ' + data[coluna_descricao].astype(str)

        # Deleta NaN
        data.dropna(subset=['CONTA_DESCRICAO'], inplace=True)

        # Ler dados da coluna
        dados_unicos = data['CONTA_DESCRICAO'].unique()

        return dados_unicos

# Cria dataframe para realizar o "de-para" das contas contábeis
def criar_dataframe_alterar_dados(path):
    st.write(f"Path recebido: {path}")
    if 'arquivo_carregado' in st.session_state:
        dados_coluna_conta = []
        st.write("Conteúdo de dados_coluna_conta:", dados_coluna_conta)
        # Verifica se o usuario selecionou a coluna conta

        if st.session_state['conta'] != "":
            dados_coluna_conta = ler_dados_conta()

        dicionário = {
                    'CONTA':  [
                    '1','1.01','1.01.01', '1.01.02', '1.01.04', '1.02', '1.02.01', '2', '2.01',
                    '2.01.04', '2.02', '2.02.01', '2.03', '3.01', '3.02', '3.03', '3.05', '3.08', '3.11', '6.01.01.02'
                ],
                    'DESCRIÇÃO': ["Ativo", "Ativo Circulante", "Caixa e Equivalente de Caixa", 
                    "Aplicação Financeira", "Estoque", "Ativo Não Circulante", "Ativo Realizável a Long Prazo", 
                    "Passivo", "Passivo Circulante", "Empréstimo a Curto Prazo", "Passivo Não Circulante", 
                    "Empréstimo a longo Prazo", "Patrimônio Líquido", "Receita Líquida", "Custos", "Lucro Bruto",
                    "Resultado Antes dos Tributos", "Imposto de Renda e Contribuição Social Sobre o Lucro", "Lucro/Prejuízo Consolidado do Período", "Depreciação e Amortização"
                ],
                    'CONTA_DESCRICAO': ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "" , ""],
                }
        data_df = pd.DataFrame(dicionário)
        #############
        #data_df = preencher_contas_existentes(data_df)
        ###########
        dataframe = st.data_editor(
            data_df,
            column_config={
                "CONTA_DESCRICAO": st.column_config.SelectboxColumn(
                    "CONTA_DESCRICAO",
                    # help="The category of the app",
                    width="medium",
                    options=dados_coluna_conta,
                    required=True,
                )
            },
            hide_index=True,
            width = 700,  
            height= 700,  
        )
        # Ler dados inseridos pelo usuário
        data = st.session_state['arquivo_carregado']

        # Filtrar as linhas selecionadas
        st.session_state['novo_df'] = pd.merge(
            data, 
            dataframe, 
            left_on='CONTA_DESCRICAO', 
            right_on='CONTA_DESCRICAO', 
            how='inner'  
        )
        return dataframe

def criar_coluna_demonstrativo(data):
    # Constants
    CONTA_BALANCO_PATRIMONIAL_ATIVO = ['1','1.01','1.01.01', '1.01.02', '1.01.04', '1.02', '1.02.01']
    CONTA_BALANCO_PATRIMONIAL_PASSIVO = ['2', '2.01', '2.01.04', '2.02', '2.02.01', '2.03']
    CONTA_RESULTADOS = ['3.01', '3.02', '3.03', '3.05', '3.08', '3.11']        
    CONTA_FLUXO_CAIXA = ['6.01.01.02'] 

    data = data.copy()
    # Create column
    data['DEMONSTRATIVO'] = ""

    # Verify account 
    e_balanco_patrimonial_ativo = data.loc[:,'CONTA'].isin(CONTA_BALANCO_PATRIMONIAL_ATIVO)
    e_balanco_patrimonial_passivo = data.loc[:,'CONTA'].isin(CONTA_BALANCO_PATRIMONIAL_PASSIVO)
    e_resultado = data.loc[:,'CONTA'].isin(CONTA_RESULTADOS)
    e_fluxo_caixa = data.loc[:,'CONTA'].isin(CONTA_FLUXO_CAIXA)

    # Create the column
    data.loc[e_balanco_patrimonial_ativo, 'DEMONSTRATIVO'] = 'Balanço Patrimonial Ativo'
    data.loc[e_balanco_patrimonial_passivo, 'DEMONSTRATIVO'] = 'Balanço Patrimonial Passivo'
    data.loc[e_resultado, 'DEMONSTRATIVO'] = 'Demonstração do Resultado'
    data.loc[e_fluxo_caixa, 'DEMONSTRATIVO'] = 'Demonstração do Fluxo de Caixa' 
    return data

def insere_periodo_trimestral(df):
    df = df.copy()
    # Ler ano definido 
    ano = st.session_state['ano_exercicio']
    mes = st.session_state['mes_exercicio'] 

    if mes == '3':
        trimestre = 1
    elif mes == '6':
        trimestre = 2
    elif mes == '9':
        trimestre = 3
    elif mes == '12':
        trimestre = 4                            

    # df.loc[(df['MES'] == mes) & (df['ANO'] == ano), 'PERIODO'] = f"{trimestre}T{ano}"
    df['PERIODO'] =  f"{trimestre}T{ano}"
    return df


def criar_novo_df():
    if (st.session_state['conta'] is not None and 
        st.session_state['descricao_conta'] is not None and 
        st.session_state['valor'] is not None and
        st.session_state['periodo'] is not None):                   

        # Ler novo dataframe
        df = st.session_state['novo_df'].copy()

        # Inserindo dados nas colunas
        df['CNPJ'] = st.session_state['cnpj']     
        df['EMPRESA'] = st.session_state['empresa']
        df['VALOR'] = df[st.session_state['valor']]
        df['ANO'] = st.session_state['ano_exercicio']
        df['MES'] = st.session_state['mes_exercicio']

        # Verifica se dados são trimestrais ou anual
        if st.session_state['periodo'] == "TRIMESTRAL":
            # Cria codigo trimestral
            df = insere_periodo_trimestral(df)

        elif st.session_state['periodo'] == "ANUAL":
            # Inserir ANUAL na coluna PERIODO
            df['PERIODO'] = st.session_state['periodo']

        # Criar conta demonstrativo
        df = criar_coluna_demonstrativo(df)

        # Verificar e processar a coluna VALOR
        if df['VALOR'].any(): 
            # Remove pontos como separadores de milhares e substitui vírgulas por pontos
            df['VALOR'] = df['VALOR'].str.replace('.', '',  regex=False)
            df['VALOR'] = df['VALOR'].str.replace(',', '.', regex=False)
            df['VALOR'] = pd.to_numeric(df['VALOR'])  # Converte para numérico após o processamento

        # Filtrar colunas
        df = df[['CNPJ', 'EMPRESA', 'CONTA', 'DESCRIÇÃO', 'VALOR', 'DEMONSTRATIVO', 'ANO', 'MES', 'PERIODO']]

        # Armazena os dados no session_state
        # if 'dados_final' not in st.session_state:
        st.session_state['dados_final'] = df

        # Cria objeto dataframe
        novo_dataframe = st.dataframe(df, 
                            width=1200,
                            hide_index=True,
                            height=700) 
        return novo_dataframe

    # Caso as condições iniciais não sejam atendidas, retornar None ou uma mensagem de erro
    return None

def salvar_dados():

    # Ler dados do session_state
    df = st.session_state['dados_final']
    print(df)
    # Se arquivo existe concatena os dados novos 
    if st.session_state['arquivo_existe']:
        data_atual = pd.read_csv("./data/dados.csv", index_col=0)
        df = pd.concat([data_atual, df], ignore_index=True)    
        print(df)
        df.to_csv("data/dados.csv", sep=",", index=False)
    else:
        # Exporta os dados
        df.to_csv("data/dados.csv", sep=",", index=False)



def pagina_configuracao():
    inicializar_session()

    # Verificar se o arquivo existe e carregá-lo
    caminho_arquivo = "./data/dados.csv"
    if os.path.exists(caminho_arquivo):
        st.session_state['dados_salvos'] = pd.read_csv(caminho_arquivo)
        st.write("Arquivo 'dados.csv' carregado com sucesso.")
        # Exibir os primeiros registros do arquivo carregado
        st.write("Primeiros registros do arquivo carregado:")
        st.write(st.session_state['dados_salvos'].head())

        # Print para o console (log)
        print("Arquivo 'dados.csv' carregado com sucesso:")
        print(st.session_state['dados_salvos'].head())
    else:
        st.session_state['dados_salvos'] = pd.DataFrame()
        st.write("Arquivo 'dados.csv' não encontrado. Nenhum dado carregado.")
        print("Arquivo 'dados.csv' não encontrado. Nenhum dado carregado.")

    # Ajuste o número de abas para corresponder ao número de itens na lista
    tab1 = st.tabs(["Alterar Dados"])

    with tab1[0]:  # Acesse a única aba disponível na lista
        alt_conta_col1, alt_conta_col2, alt_conta_col3 = st.columns([1, 2, 1])
        with alt_conta_col1:                
            st.write("Associe as colunas abaixo com as colunas dos seus dados.")

        with alt_conta_col2:        
            if 'dados_salvos' in st.session_state and not st.session_state['dados_salvos'].empty:
                # Passa os dados carregados para a função de alterar dados
                criar_dataframe_alterar_dados(st.session_state['dados_salvos'])
            else:
                st.error("Nenhum dado foi carregado para alterar. Por favor, carregue um arquivo antes de prosseguir.")
