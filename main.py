import streamlit as st
import pandas as pd
import os
from streamlit_option_menu import option_menu
from streamlit_option_menu import option_menu

import paginas.Resultados as dre
import paginas.Indicadores as indicadores
import paginas.BalancoPatrimonial as bp
import paginas.Dashboard as dashboard
import paginas.configuracao as config


# Configuração da página
st.set_page_config(
    page_title='Aplicativo',
    layout='wide',
    page_icon=":bar_chart:",
    initial_sidebar_state='expanded'
)

st.markdown("""
<style>
    #header, footer {visibility: hidden;}

    /* This code gets the first element on the sidebar,
    and overrides its default styling */
    section[data-testid="stSidebar"] div:first-child {
        top: 0;
        height: 100vh;
    }
    .st-emotion-cache-1jicfl2 {
    width: 100%;
    padding: 1rem 4rem 2rem;
    min-width: auto;
    max-width: initial;
}
    .st-emotion-cache-12fmjuu {
    padding: 0rem 2rem 2rem;
    background-color: transparent;            
}
            
    .st-emotion-cache-h4xjwg {
    padding: 0rem 2rem 2rem;
    background-color: transparent;            
}
    .st-emotion-cache-1xarl3l {
    font-size: 1.80rem;
    padding-bottom: 0.25rem;
}
            
</style>
""",unsafe_allow_html=True)


footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
color: gray;
text-align: center;
}
</style>
<div class="footer">
<p>Developed by UNION IT</p>
</div>
"""


@st.dialog("Aviso")
def aviso(texto, tipo):
    if tipo == "sucesso":
        st.success('Esta é uma mensagem de sucesso!', icon="✅")
    elif tipo == "erro":
        st.warning(texto, icon="⚠️")


def verifica_dados():
    import os
    import pandas as pd
    import streamlit as st

    # Verifica primeiro se um arquivo foi carregado via upload e está salvo no session_state
    if 'arquivo_path' in st.session_state and os.path.isfile(st.session_state['arquivo_path']):
        st.write(f"Usando arquivo carregado: {st.session_state['arquivo_path']}")
        
        # Verifica se o arquivo pode ser lido
        try:
            dados = pd.read_csv(st.session_state['arquivo_path'])
            st.write("Arquivo carregado lido com sucesso.")
        except Exception as e:
            st.error(f"Erro ao ler o arquivo carregado: {e}")
            return False
        return True  # Se o arquivo via upload existe e foi lido com sucesso, use-o

    # Caso contrário, tenta encontrar o arquivo mais recente na pasta 'data'
    path_pasta = 'data'
    arquivo_padrao = 'arezzo_novo_anual.csv'
    caminho_padrao = os.path.join(path_pasta, arquivo_padrao)

    # Verifica se a pasta existe
    if not os.path.exists(path_pasta):
        st.error(f"A pasta '{path_pasta}' não existe.")
        return False

    # Lista todos os arquivos na pasta 'data'
    arquivos = [f for f in os.listdir(path_pasta) if os.path.isfile(os.path.join(path_pasta, f))]
    if not arquivos:
        st.error(f"Nenhum arquivo encontrado na pasta '{path_pasta}'.")
        return False

    # Remove o arquivo padrão da lista, se existir
    if arquivo_padrao in arquivos:
        arquivos.remove(arquivo_padrao)

    if arquivos:
        # Se houver outros arquivos, seleciona o mais recente
        arquivos_caminhos = [os.path.join(path_pasta, f) for f in arquivos]
        arquivo_recente = max(arquivos_caminhos, key=os.path.getmtime)
        st.session_state['arquivo_path'] = arquivo_recente
        st.write(f"Usando arquivo mais recente carregado: {arquivo_recente}")

        # Tenta ler o arquivo
        try:
            dados = pd.read_csv(arquivo_recente)
            st.write("Arquivo carregado lido com sucesso.")
        except Exception as e:
            st.error(f"Erro ao ler o arquivo carregado: {e}")
            return False
        return True
    else:
        # Se não houver outros arquivos, usa o arquivo padrão
        if os.path.isfile(caminho_padrao):
            st.session_state['arquivo_path'] = caminho_padrao
            st.write(f"Usando arquivo padrão: {caminho_padrao}")

            # Tenta ler o arquivo padrão
            try:
                dados = pd.read_csv(caminho_padrao)
                st.write("Arquivo padrão lido com sucesso.")
            except Exception as e:
                st.error(f"Erro ao ler o arquivo padrão: {e}")
                return False
            return True    
        else:
            st.error(f"O arquivo padrão '{arquivo_padrao}' não foi encontrado na pasta '{path_pasta}'.")
            return False  # Retorna False se nenhum arquivo for encontrado


if 'arquivo_existe' not in st.session_state:
    st.session_state['arquivo_existe'] = verifica_dados()

# Se o arquivo existir, carrega os dados
if st.session_state['arquivo_existe']:
    if 'data_anual' not in st.session_state:
        # Carrega o arquivo que foi salvo no session_state (pode ser o do upload ou o padrão)
        st.session_state['data'] = pd.read_csv(st.session_state['arquivo_path'])
        pd.to_numeric(st.session_state['data']["VALOR"])   
        pd.to_datetime(st.session_state['data']["ANO"])

    selected2 = option_menu(None, ['Dashboard', 'Indicadores', 'Balanço Patrimonial', 'Resultado', 'Configuração'  ], 
        icons=['house', 'activity', "list-task",'list-task'], 
        menu_icon="cast", default_index=0, orientation="horizontal")
    
    # selected2 = option_menu(None, ['Dashboard','Configuração' ], 
    #     icons=['house', 'activity', "list-task",'list-task'], 
    #     menu_icon="cast", default_index=0, orientation="horizontal")
    
    

    try:
        if selected2 == "Dashboard":
            dashboard.dashboard()

        elif selected2 == "Indicadores":
            indicadores.pagina_indicadores()

        elif selected2 == "Balanço Patrimonial":
            bp.pagina_bp()

        elif selected2 == "Resultado":
            dre.pagina_dre()

        elif selected2 == "Configuração":
            config.pagina_configuracao()
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar a página {selected2}: {e}")

    st.markdown(footer, unsafe_allow_html=True)

else:
    selected2 = option_menu(None, ['Dashboard', 'Indicadores', 'Balanço Patrimonial', 'Resultado', 'Configuração'  ], 
        icons=['house', 'activity', "list-task",'list-task'], 
        menu_icon="cast", default_index=4, orientation="horizontal")

    if selected2 == "Dashboard":
        st.error('Ausência de dados', icon="🚨")
        st.write("Vá para a aba de configuração para inserir dados")    
        aviso("Não existem dados, vá até a página de configuração e insira.", "erro")

    if selected2 == "Indicadores":
        st.error('Ausência de dados', icon="🚨")
        st.write("Vá para a aba de configuração para inserir dados")
        aviso("Não existem dados, vá até a página de configuração e insira.", "erro")


    if selected2 == "Balanço Patrimonial":
        st.error('Ausência de dados', icon="🚨")
        st.write("Vá para a aba de configuração para inserir dados")
        aviso("Não existem dados, vá até a página de configuração e insira.", "erro")

    if selected2 == "Resultado":
        st.error('Ausência de dados', icon="🚨")
        st.write("Vá para a aba de configuração para inserir dados")
        aviso("Não existem dados, vá até a página de configuração e insira.", "erro")

    if selected2 == "Configuração":
        config.pagina_configuracao()

    st.markdown(footer,unsafe_allow_html=True)

def verificar_status_carregamento():
    # Verifica se o arquivo foi carregado
    if 'arquivo_carregado_sucesso' in st.session_state and st.session_state['arquivo_carregado_sucesso']:
        st.write("O arquivo foi carregado com sucesso. Você pode prosseguir com as próximas etapas.")
        # Habilite ou mostre elementos que dependem do arquivo carregado
        if 'arquivo_carregado' in st.session_state:
            st.write("Mostrando as primeiras linhas do arquivo carregado:")
            st.write(st.session_state['arquivo_carregado'].head())
    else:
        st.warning("Por favor, carregue um arquivo para prosseguir.")
