import streamlit as st
import pandas as pd
import shutil
import os

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


def carregar_arquivo():
    # Cria o objeto para upload do arquivo
    arquivo_carregado = st.file_uploader("Selecione o arquivo", type={"csv", "txt"})

    # Verifica se o arquivo foi carregado
    if arquivo_carregado is not None:             
        delimitador_escolhido = separador_arquivo()

        # Verifica o tipo do arquivo
        if st.session_state['tipo_arquivo'] == ".csv":
            try:
                # Lê o arquivo com o pandas e armazena
                df = pd.read_csv(arquivo_carregado, 
                                 sep=delimitador_escolhido, 
                                 encoding=st.session_state['encoding'],
                                 on_bad_lines='warn'  # Usando warn para ignorar linhas com problemas
                                )
                
                # Exibe informações para debug
                st.write("DataFrame carregado: ", df.head())  
                st.write("Colunas: ", df.columns)  

                # Armazena no session_state para acessar em outras partes do app
                st.session_state['arquivo_carregado'] = df
                st.session_state['colunas'] = df.columns

                # Mostra mensagem de sucesso
                st.success('Arquivo carregado com sucesso', icon="✅")

                # Sinaliza que o arquivo foi carregado
                st.session_state['arquivo_carregado_sucesso'] = True

            except Exception as e:
                # Mostra um aviso de erro caso algo dê errado durante a leitura do arquivo
                st.error(f'Erro ao carregar o arquivo: {e}', icon="🚨")
                st.session_state['arquivo_carregado_sucesso'] = False  # Reseta a sinalização para evitar reprocessamento
            
            # Mensagem de aviso se houver problemas com linhas
            if df is not None and df.empty:
                st.warning("Algumas linhas foram ignoradas durante o carregamento. Verifique o arquivo para mais detalhes.", icon="⚠️")

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
def criar_dataframe_alterar_dados():
    if 'arquivo_carregado' in st.session_state:
        dados_coluna_conta = []
        
        # Verifica se o usuario selecionou a coluna conta
        if st.session_state['conta'] != "":
            dados_coluna_conta = ler_dados_conta()

        dicionario = {
                    'CONTA':  [
                    '1','1.01','1.01.01', '1.01.02', '1.01.04', '1.02', '1.02.01', '2', '2.01',
                    '2.01.04', '2.02', '2.02.01', '2.03', '3.01', '3.02', '3.03', '3.05', '3.08', '3.11', '6.01.01.02'
                ],
                    'DESCRIÇÃO': ["Ativo", "Ativo Circulante", "Caixa e Equivalente de Caixa", 
                    "Aplicação Financeira", "Estoque", "Ativo Não Circulante", "Ativo Realizável a Longo Prazo", 
                    "Passivo", "Passivo Circulante", "Empréstimo a Curto Prazo", "Passivo Não Circulante", 
                    "Empréstimo a Longo Prazo", "Patrimônio Líquido", "Receita Líquida", "Custos", "Lucro Bruto",
                    "Resultado Antes dos Tributos", "Imposto de Renda e Contribuição Social Sobre o Lucro", "Lucro/Prejuízo Consolidado do Período", "Depreciação e Amortização"
                ],
                    'CONTA_DESCRICAO': ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "" , ""],
                }
        data_df = pd.DataFrame(dicionario)
        dataframe = st.data_editor(
            data_df,
            column_config={
                "CONTA_DESCRICAO": st.column_config.SelectboxColumn(
                    "CONTA_DESCRICAO",
                    width="medium",
                    options=dados_coluna_conta,
                    required=True,
                )
            },
            hide_index=True,
            width=700,  
            height=700,  
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
    else:
        trimestre = None

    if trimestre:
        df['PERIODO'] =  f"{trimestre}T{ano}"
    else:
        df['PERIODO'] = f"M{mes}/{ano}"
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
            df['VALOR'] = df['VALOR'].astype(str).str.replace('.', '', regex=False)
            df['VALOR'] = df['VALOR'].str.replace(',', '.', regex=False)
            df['VALOR'] = pd.to_numeric(df['VALOR'])  # Converte para numérico após o processamento

        # Filtrar colunas
        df = df[['CNPJ', 'EMPRESA', 'CONTA', 'DESCRIÇÃO', 'VALOR', 'DEMONSTRATIVO', 'ANO', 'MES', 'PERIODO']]

        # Armazena os dados no session_state
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
    if 'arquivo_existe' in st.session_state and st.session_state['arquivo_existe']:
        data_atual = pd.read_csv("./data/dados.csv", index_col=0)
        df = pd.concat([data_atual, df], ignore_index=True)    

        print(df)
        df.to_csv("data/dados.csv", sep=",", index=False)
    else:
        # Exporta os dados
        df.to_csv("data/dados.csv", sep=",", index=False)


import os
import json
import streamlit as st

def carregar_e_salvar_arquivo():
    # Carregar o arquivo com file_uploader
    arquivo_carregado = st.file_uploader("Selecione o arquivo", type={"csv", "txt", "xlsx"})
    
    if arquivo_carregado is not None:
        # Input para o nome do arquivo
        nome_arquivo = st.text_input("Digite o nome do arquivo (sem extensão):")

        if nome_arquivo and st.button("Salvar Arquivo"):
            # Diretório onde o arquivo será salvo
            extensao = os.path.splitext(arquivo_carregado.name)[1]
            caminho_destino = os.path.join("data", f"{nome_arquivo}{extensao}")

            # Salvando o arquivo na pasta data
            with open(caminho_destino, "wb") as f:
                f.write(arquivo_carregado.getbuffer())

            # Armazena o caminho no session_state
            st.session_state['arquivo_path'] = caminho_destino

            # Salva o caminho do arquivo em um arquivo JSON
            with open('ultimo_arquivo.json', 'w') as f:
                json.dump({'arquivo_path': caminho_destino}, f)

            st.success(f"Arquivo salvo como: {caminho_destino}")
        else:
            st.warning("Por favor, insira um nome válido para o arquivo.")

            

            
def pagina_configuracao():
    inicializar_session()

    tab1, tab2, tab3, tab4 , tab5 = st.tabs(["Configuração", "Carregar Arquivo", "Alterar Dados", "Exportar Dados","Upload_api"])

    with tab1:
        st.write("Entre com as informações dos dados que você quer inserir.")
        
        configuracao_col1, configuracao_col2 = st.columns(2)
        with configuracao_col1:
            with st.container():
                st.write("Informações do arquivo.")        

                info_file_col1, info_file_col2, info_file_col3 = st.columns(3)
                with info_file_col1:
                    st.session_state['tipo_arquivo'] = st.selectbox(
                        "Tipo de Arquivo",
                        (".csv", ".pdf", ".xlsx"),
                    )

                with info_file_col2:
                    st.session_state['delimitador'] = st.selectbox(
                        "Delimitador",
                        ("Vírgula", "Ponto e Vírgula"),
                    )

                with info_file_col3:
                    st.session_state['encoding'] = st.selectbox(
                        "Encoding",
                        ("UTF-8", "ISO-8859-1"),
                    )

            with st.container():
                st.write("Informações da Empresa.")         

                info_emp_col1, info_emp_col2 = st.columns(2)
                with info_emp_col1:
                        st.session_state['empresa'] = st.text_input("Nome", 
                    )
                with info_emp_col2:
                    st.session_state['cnpj'] = st.text_input("CNPJ", 
                    )

        with configuracao_col2:
            with st.container():
                st.write("Informações do Período.")         

                info_periodo_col1, info_periodo_col2, info_periodo_col3 = st.columns(3)
                with info_periodo_col1:
                    st.session_state['periodo'] = st.selectbox(
                        "Período dos dados",
                        ("MENSAL", "TRIMESTRAL", "ANUAL"),
                        index=None,
                        placeholder="SELECIONE O PERÍODO"
                    )

                with info_periodo_col2:
                    st.session_state['mes_exercicio'] = st.selectbox(
                        "Mês de Exercício",
                        ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"),
                        index=None,
                        placeholder="SELECIONE O MÊS"
                    )

                with info_periodo_col3:
                    st.session_state['ano_exercicio'] = st.text_input("Ano", 
                        placeholder="Digite o ano"
                    )
    # Carregar arquivo                 
    with tab2:        
        carregar_arquivo_main_col1, carregar_arquivo_main_col2 = st.columns(2)
        with carregar_arquivo_main_col1:
            with st.container():
                st.write("Faça o upload do arquivo abaixo:")
                carregar_arquivo()

            if 'arquivo_carregado' in st.session_state:
                with st.container():
                    st.write("Associe as colunas abaixo com as colunas dos seus dados.")

                    carregar_arquivo_col1, carregar_arquivo_col2, carregar_arquivo_col3 = st.columns(3)
                    # Ler as colunas dos dados do usuario
                    lista_colunas = st.session_state['colunas']

                    with carregar_arquivo_col1:                        
                        st.session_state['conta'] = st.selectbox(
                            "Conta",
                            lista_colunas,  
                            index=None,
                            placeholder="SELECIONE A COLUNA"
                        )
                    with carregar_arquivo_col2:                            
                        st.session_state['descricao_conta'] = st.selectbox(
                            "Descrição da Conta",
                            lista_colunas,  
                            index=None,
                            placeholder="SELECIONE A COLUNA"
                        )
                    with carregar_arquivo_col3:                        
                        st.session_state['valor'] = st.selectbox(
                            "Valor",
                            lista_colunas,  
                            index=None,
                            placeholder="SELECIONE A COLUNA"
                        ) 

    # Alterar Dados                 
    with tab3:      
        if 'arquivo_carregado' in st.session_state:
            alt_conta_col1, alt_conta_col2, alt_conta_col3 = st.columns([1,2,1])
            with alt_conta_col1:                
                st.write("Associe as contas abaixo com as suas contas.")

            with alt_conta_col2:        
                criar_dataframe_alterar_dados()
        else:
            st.warning("Por favor, carregue um arquivo primeiro.")

    # Exportar Dados                 
    # Exportar Dados                 
    with tab4:
        if 'novo_df' in st.session_state:
            exp_col1, exp_col2 = st.columns([3, 1], gap="small")
            with exp_col1:
                df_final = criar_novo_df()  # Cria o DataFrame final
            
            with exp_col2:
                if st.button("Gravar"):
                    salvar_dados()
                    aviso("Dados gravados!", "sucesso")

                # Verifica se os dados finais estão disponíveis para download
                if 'dados_final' in st.session_state:
                    # Converte o DataFrame em CSV
                    csv = st.session_state['dados_final'].to_csv(index=False).encode('utf-8')

                    # Botão para baixar o CSV
                    st.download_button(
                        label="Baixar dados",
                        data=csv,
                        file_name='dados_final.csv',
                        mime='text/csv',
                    )
        else:
            st.warning("Por favor, altere os dados primeiro.")

    with tab5:
        st.write("Faça o upload de um arquivo para a pasta 'data'.")
        carregar_e_salvar_arquivo()

pagina_configuracao()

