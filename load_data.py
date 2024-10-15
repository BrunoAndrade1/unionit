import streamlit as st
import pandas as pd
import snowflake.connector


# Importar dados da BD
@st.cache_data
def get_data():
  with my_cnx.cursor() as my_cur:
    my_cur.execute("SELECT * FROM fato")
    return my_cur.fetchall()

# conexao com BD
my_cnx = snowflake.connector.connect(
    user='aderbal_silva',
    password='aderbal_123',
    account='qa82978.sa-east-1.aws',
    warehouse='COMPUTE_WH',
    database='DB_CONTABIL',
    schema='PUBLIC',
    role = "SYSADMIN"
)

@st.cache_data
def load_data():
    # Instancia dos dados importados
    data_fato = get_data()

    # Cria dataframe
    columns = ['CNPJ', 'EMPRESA', 'CONTA', 'DESCRIÇÃO', 'VALOR', 'DEMONSTRATIVO', 'ANO', 'MES', 'PERIODO']
    data = pd.DataFrame(data_fato, columns=columns)

    pd.to_numeric(data["VALOR"])   
    pd.to_numeric(data["MES"])   
    pd.to_datetime(data["ANO"]) 
    data.reset_index(inplace=True) 
    return data
