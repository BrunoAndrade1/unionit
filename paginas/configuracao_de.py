import streamlit as st
import pandas as pd

def inicializar_session():
    keys_default = {
        'tipo_arquivo': "",
        'delimitador': "",
        'encoding': "",
        'periodo': None,
        'mes_exercicio': "",
        'ano_exercicio': "",
        'empresa': "",
        'cnpj': "",
        'conta': None,
        'colunas': "",
        'descricao_conta': None,
        'valor': None,
        'novo_df': "",
        'dados_final': None,
        'tipo_excel': ""
    }
    
    for key, default in keys_default.items():
        if key not in st.session_state:
            st.session_state[key] = default

def aviso(texto, tipo):
    if tipo == "sucesso":
        st.success(texto, icon="✅")
    elif tipo == "erro":
        st.warning(texto, icon="⚠️")

def separador_arquivo():
    delimitadores = {
        "Vírgula": ",",
        "Ponto e Vírgula": ";"
    }
    return delimitadores.get(st.session_state['delimitador'], ",")

# Função específica para ler e formatar o balancete
def carregar_e_formatar_balancete(arquivo):
    # Ler o arquivo Excel, pulando as primeiras 6 linhas
    df_cleaned = pd.read_excel(arquivo, skiprows=6)
    
    # Renomear as colunas principais
    df_cleaned.columns = df_cleaned.iloc[0]
    df_cleaned = df_cleaned.drop(0)
    
    # Preencher os valores ausentes na descrição com o valor da linha anterior usando ffill()
    df_cleaned['Descrição da conta'] = df_cleaned['Descrição da conta'].ffill()
    
    # Unir as colunas I até M para formar a "Descrição da conta" completa
    df_cleaned['Descrição da conta'] = df_cleaned.iloc[:, 8:13].apply(lambda row: ' '.join(row.dropna().astype(str)), axis=1)
    
    # Função para formatar a hierarquia de contas de acordo com a classificação
    def format_hierarchy_by_classification(row):
        classification = str(row['Classificação']).strip()
        
        # Verifica se a classificação contém apenas números e pontos
        if not classification.replace('.', '').isdigit():
            return row['Descrição da conta']
        
        # Contar o número de níveis na classificação
        indent_level = classification.count('.')
        
        # Definir quantos espaços por nível de subconta
        spaces_per_level = 4  # Ajustável, dependendo de quanta indentação você quer
        
        # Personalizar os títulos principais com maiúsculas e adicionar indentação para subcontas
        if indent_level == 0:
            return row['Descrição da conta'].upper()  # Títulos principais em maiúsculas
        else:
            return ' ' * (indent_level * spaces_per_level) + row['Descrição da conta'].capitalize()
    
    # Aplicar a função de hierarquia à coluna "Descrição da conta"
    df_cleaned['Descrição da conta'] = df_cleaned.apply(format_hierarchy_by_classification, axis=1)
    
    # Criar um novo dataframe com as colunas desejadas
    df_new = df_cleaned[['Classificação', 'Descrição da conta', 'Saldo Anterior', 'Débito', 'Crédito', 'Saldo Atual']].copy()
    
    # Unir as colunas de saldo (colunas 17 a 21) para formar um valor de "Saldo Anterior" consolidado
    # Ajuste este trecho se necessário, dependendo da estrutura real do seu arquivo
    df_new['Saldo Anterior'] = df_cleaned.iloc[:, 17:22].apply(lambda row: ' '.join(row.dropna().astype(str)), axis=1)
    
    return df_new

def detectar_tipo_excel(arquivo):
    try:
        df_preview = pd.read_excel(arquivo)
        colunas_balancete = ['Classificação', 'Descrição da conta', 'Saldo Anterior', 'Débito', 'Crédito', 'Saldo Atual']
        if all(coluna in df_preview.columns for coluna in colunas_balancete):
            return "balancete"
        else:
            return "padrao"
    except Exception as e:
        st.error(f"Erro ao detectar o tipo de arquivo Excel: {e}")
        return "padrao"

def carregar_arquivo():
    arquivo_carregado = st.file_uploader("Inserir", type={"csv", "txt", "xls", "xlsx", "xlsm", "xlsb", "ods"})

    if arquivo_carregado is not None:
        extensao_arquivo = arquivo_carregado.name.split('.')[-1].lower()
        tipo_arquivo_selecionado = st.session_state.get('tipo_arquivo', '').lower()

        try:
            if tipo_arquivo_selecionado == "balancete":
                # Chama a função específica para balancete
                df = carregar_e_formatar_balancete(arquivo_carregado)
            elif extensao_arquivo == "csv":
                delimitador_escolhido = separador_arquivo()
                df = pd.read_csv(arquivo_carregado,
                                 sep=delimitador_escolhido,
                                 encoding=st.session_state.get('encoding', 'utf-8'),
                                 on_bad_lines='warn')
            elif extensao_arquivo in ["xls", "xlsx", "xlsm", "xlsb"]:
                # Detecta o tipo de arquivo Excel
                tipo_detectado = detectar_tipo_excel(arquivo_carregado)
                st.write(f"Tipo de arquivo detectado: **{tipo_detectado.capitalize()}**")

                # Adiciona a opção "Balancete" ao selectbox
                opcoes_tipo_excel = ["Padrão", "Balancete"]
                if tipo_detectado not in opcoes_tipo_excel:
                    opcoes_tipo_excel.append(tipo_detectado.capitalize())

                st.session_state['tipo_excel'] = st.selectbox(
                    "Confirme o tipo de arquivo Excel",
                    opcoes_tipo_excel,
                    index=opcoes_tipo_excel.index(tipo_detectado.capitalize())
                )

                if st.session_state['tipo_excel'].lower() == "balancete":
                    df = carregar_e_formatar_balancete(arquivo_carregado)
                else:
                    df = pd.read_excel(arquivo_carregado)
            elif extensao_arquivo == "ods":
                df = pd.read_excel(arquivo_carregado, engine='odf')
            elif extensao_arquivo == "txt":
                delimitador_escolhido = separador_arquivo()
                df = pd.read_csv(arquivo_carregado,
                                 sep=delimitador_escolhido,
                                 encoding=st.session_state.get('encoding', 'utf-8'),
                                 on_bad_lines='warn')
            else:
                st.error("Extensão de arquivo não suportada.", icon="🚨")
                return

            # Armazena o dataframe no session_state
            st.session_state['arquivo_carregado'] = df
            st.session_state['colunas'] = df.columns.tolist()
            st.success('Arquivo carregado com sucesso', icon="✅")

        except Exception as e:
            st.error(f'Erro ao carregar o arquivo: {e}', icon="🚨")

    if st.button("Fechar"):
        st.experimental_rerun()

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
            'CONTA_DESCRICAO': ["" for _ in range(20)],
        }
        data_df = pd.DataFrame(dicionario)
        dataframe = st.data_editor(
            data_df,
            column_config={
                "CONTA_DESCRICAO": st.column_config.SelectboxColumn(
                    "CONTA_DESCRICAO",
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
            how='inner'  # 'inner' garante que só sejam mantidas as linhas onde os valores são iguais
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
    e_balanco_patrimonial_ativo = data['CONTA'].isin(CONTA_BALANCO_PATRIMONIAL_ATIVO)
    e_balanco_patrimonial_passivo = data['CONTA'].isin(CONTA_BALANCO_PATRIMONIAL_PASSIVO)
    e_resultado = data['CONTA'].isin(CONTA_RESULTADOS)
    e_fluxo_caixa = data['CONTA'].isin(CONTA_FLUXO_CAIXA)

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

    trimestre = None
    if mes == '3':
        trimestre = 1
    elif mes == '6':
        trimestre = 2
    elif mes == '9':
        trimestre = 3
    elif mes == '12':
        trimestre = 4

    if trimestre is not None:
        df['PERIODO'] =  f"{trimestre}T{ano}"
    else:
        df['PERIODO'] = f"{mes}/{ano}"
    return df

def criar_novo_df():
    if (st.session_state['conta'] is not None and 
        st.session_state['descricao_conta'] is not None and 
        st.session_state['valor'] is not None and
        st.session_state['periodo'] is not None and
        'novo_df' in st.session_state):                   

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
        else:
            df['PERIODO'] = f"{df['MES']}/{df['ANO']}"

        # Criar conta demonstrativo
        df = criar_coluna_demonstrativo(df)

        # Verificar e processar a coluna VALOR
        if df['VALOR'].any(): 
            # Remove pontos como separadores de milhares e substitui vírgulas por pontos
            df['VALOR'] = df['VALOR'].astype(str)
            df['VALOR'] = df['VALOR'].str.replace('.', '',  regex=False)
            df['VALOR'] = df['VALOR'].str.replace(',', '.', regex=False)
            df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce')  # Converte para numérico após o processamento

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
    # Se arquivo existe concatena os dados novos 
    try:
        data_atual = pd.read_csv("./data/dados.csv")
        df = pd.concat([data_atual, df], ignore_index=True)
        df.to_csv("data/dados.csv", sep=",", index=False)
    except FileNotFoundError:
        # Exporta os dados
        df.to_csv("data/dados.csv", sep=",", index=False)

def pagina_configuracao():
    inicializar_session()

    tab1, tab2, tab3, tab4 = st.tabs(["Configuração", "Carregar Arquivo", "Alterar Dados", "Exportar Dados"])

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
                        (".pdf", ".xlsx", "Balancete",'teste'),  # Adicionado "Balancete"
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
                    st.session_state['empresa'] = st.text_input("Nome")
                with info_emp_col2:
                    st.session_state['cnpj'] = st.text_input("CNPJ")

        with configuracao_col2:
            with st.container():
                st.write("Informações do Período.")         

                info_periodo_col1, info_periodo_col2, info_periodo_col3 = st.columns(3)
                with info_periodo_col1:
                    st.session_state['periodo'] = st.selectbox(
                        "Período dos dados",
                        ("MENSAL", "TRIMESTRAL", "ANUAL"),
                        index=0,
                        placeholder="SELECIONE O PERÍODO"
                    )

                with info_periodo_col2:
                    st.session_state['mes_exercicio'] = st.selectbox(
                        "Mês de Exercício",
                        ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"),
                        index=0,
                        placeholder="SELECIONE O MÊS"
                    )

                with info_periodo_col3:
                    st.session_state['ano_exercicio'] = st.text_input("Ano", 
                        placeholder="Digite o ano"
                    )

    # Carregar arquivo                 
    with tab2:
        if 'tipo_arquivo' not in st.session_state or st.session_state['tipo_arquivo'] == "":
            st.warning("Por favor, configure as informações na aba 'Configuração' antes de carregar o arquivo.")
        else:
            carregar_arquivo_main_col1, carregar_arquivo_main_col2 = st.columns(2)
            with carregar_arquivo_main_col1:
                with st.container():
                    st.write("Pressione 'Inserir' para carregar o arquivo")

                    if st.button("Inserir"):
                        carregar_arquivo()

                if 'colunas' in st.session_state and st.session_state['colunas'] != "":
                    with st.container():
                        st.write("Associe as colunas abaixo com as colunas dos seus dados.")

                        carregar_arquivo_col1, carregar_arquivo_col2, carregar_arquivo_col3 = st.columns(3)
                        # Ler as colunas dos dados do usuario
                        lista_colunas = st.session_state['colunas']

                        with carregar_arquivo_col1:                        
                            st.session_state['conta'] = st.selectbox(
                                "Conta",
                                lista_colunas,  
                                index=0,
                                placeholder="SELECIONE A COLUNA"
                            )
                        with carregar_arquivo_col2:                            
                            st.session_state['descricao_conta'] = st.selectbox(
                                "Descrição da Conta",
                                lista_colunas,  
                                index=0,
                                placeholder="SELECIONE A COLUNA"
                            )
                        with carregar_arquivo_col3:                        
                            st.session_state['valor'] = st.selectbox(
                                "Valor",
                                lista_colunas,  
                                index=0,
                                placeholder="SELECIONE A COLUNA"
                            )
                else:
                    st.info("Por favor, carregue um arquivo para continuar.")

    # Alterar Dados                 
    with tab3:      
        if 'novo_df' in st.session_state:
            alt_conta_col1, alt_conta_col2, alt_conta_col3 = st.columns([1,2,1])
            with alt_conta_col1:                
                st.write("Associe as colunas abaixo com as colunas dos seus dados.")

            with alt_conta_col2:        
                criar_dataframe_alterar_dados()
        else:
            st.info("Por favor, carregue e processe o arquivo na aba 'Carregar Arquivo' antes de alterar dados.")

    # Exportar Dados                 
    with tab4:
        if 'dados_final' in st.session_state:
            exp_col1, exp_col2 = st.columns([3, 1], gap="small")
            with exp_col1:
                criar_novo_df()     

            with exp_col2:
                if st.button("Gravar"):
                    salvar_dados()  # Chama a função para salvar os dados
                    aviso("Dados gravados!", "sucesso")

                    # Gerar CSV para download
                    df_salvo = st.session_state['dados_final']  # Acessa o DataFrame salvo
                    csv = df_salvo.to_csv(index=False).encode('utf-8')  # Converte o DataFrame para CSV

                    # Adiciona o botão de download
                    st.download_button(
                        label="Baixar dados",
                        data=csv,
                        file_name='dados.csv',
                        mime='text/csv'
                    )
        else:
            st.info("Por favor, crie o novo DataFrame na aba 'Alterar Dados' antes de exportar.")

# Chamada principal para executar a aplicação
if __name__ == "__main__":
    pagina_configuracao()
