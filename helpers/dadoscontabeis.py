import pandas as pd
import streamlit as st
import helpers.criarGraficos as grf
import helpers.analises as anls
import helpers.demonstrativos as demo

def get_valor_anual(df, ano, conta):
    """
    Retrieves the value for a specific account and year from the DataFrame.

    Parameters:
        df (DataFrame): The DataFrame containing the financial data.
        ano (int): The year to filter.
        conta (str): The account code to filter.

    Returns:
        float: The value associated with the account and year, or 0 if not found.
    """
    filtro = df.loc[(df['ANO'] == ano) & (df['CONTA'] == conta), "VALOR"]
    if not filtro.empty:
        return filtro.values[0]
    else:
        return 0

def get_valor_anual_mes(df, ano, mes, conta, coluna):
    """
    Retrieves the value for a specific account, year, and month from the DataFrame.

    Parameters:
        df (DataFrame): The DataFrame containing the financial data.
        ano (int): The year to filter.
        mes (int): The month to filter.
        conta (str): The account code to filter.
        coluna (str): The column from which to retrieve the value.

    Returns:
        float: The value associated with the filters, or 0 if not found.
    """
    filtro = df.loc[(df['ANO'] == ano) & (df['MES'] == mes) & (df['CONTA'] == conta), coluna]
    if not filtro.empty:
        return filtro.values[0]
    else:
        return 0

def ler_contas_anual(df, ano):
    """
    Extracts financial account values for a specific year and returns them as a dictionary.

    Parameters:
        df (DataFrame): The DataFrame containing the financial data.
        ano (int): The year to filter.

    Returns:
        dict: A dictionary containing the financial account values.
    """
    data = {
        'estoque': get_valor_anual(df, ano, "1.01.04"),
        'ativo_total': get_valor_anual(df, ano, "1"),
        'ativo_circulante': get_valor_anual(df, ano, "1.01"),
        'caixa_eq': get_valor_anual(df, ano, "1.01.01"),
        'realizavel_longo_prazo': get_valor_anual(df, ano, "1.02.01"),
        'passivo_total': get_valor_anual(df, ano, "2"),
        'passivo_circulante': get_valor_anual(df, ano, "2.01"),
        'passivo_nao_circulante': get_valor_anual(df, ano, "2.02"),
        'patrimonio_liquido': get_valor_anual(df, ano, "2.03"),
        'emprestimo_curto_prazo': get_valor_anual(df, ano, "2.01.04"),
        'emprestimo_longo_prazo_valor': get_valor_anual(df, ano, "2.02.01"),
        'equivalente_caixa': get_valor_anual(df, ano, "1.01.01"),
        'aplicacao_financeira': get_valor_anual(df, ano, "1.01.02"),
        'receita_liquida': get_valor_anual(df, ano, "3.01"),
        'receita_total': get_valor_anual(df, ano, "3.03"),
        'lucro_bruto': get_valor_anual(df, ano, "3.03"),
        'impostos': get_valor_anual(df, ano, "3.08"),
        'lucro_liquido': get_valor_anual(df, ano, "3.11"),
        'ebit': get_valor_anual(df, ano, "3.05"),
        'depreciacao_amortizacao': get_valor_anual(df, ano, "6.01.01.02"),
    }
    # Calculate EBITDA
    data['ebitda'] = data['ebit'] + data['depreciacao_amortizacao']
    return data

def ordena_dataframe_decrescente(df, inicio, fim):
    """
    Sorts the DataFrame in descending order based on the 'TRIMESTRE' column.

    Parameters:
        df (DataFrame): The DataFrame to sort.
        inicio (int): The start year.
        fim (int): The end year.

    Returns:
        DataFrame: The sorted DataFrame.
    """
    trimestres_ordenados = ["4", "3", "2", "1"]
    anos = [str(ano) for ano in range(fim, inicio - 1, -1)]
    trimestres_ordenados = [f"{tri}T{ano}" for ano in anos for tri in trimestres_ordenados]

    df['TRIMESTRE'] = pd.Categorical(df['TRIMESTRE'], categories=trimestres_ordenados, ordered=True)
    df_sorted = df.sort_values('TRIMESTRE')
    return df_sorted

def ordena_tabular_anual(df):
    """
    Reorders the columns of the DataFrame for annual tabular display.

    Parameters:
        df (DataFrame): The DataFrame to reorder.

    Returns:
        DataFrame: The DataFrame with reordered columns.
    """
    colunas_ordenadas = ['ÍNDICES'] + df.columns[1:][::-1].tolist()
    return df[colunas_ordenadas]

def data_receita_liquida_custos_trimestral(df, inicio, fim):
    """
    Prepares data for plotting quarterly net revenue, costs, and net income.

    Parameters:
        df (DataFrame): The DataFrame containing the financial data.
        inicio (int): The start year.
        fim (int): The end year.

    Returns:
        DataFrame: The prepared DataFrame.
    """
    df = df[df['CONTA'].isin(["3.02", "3.01", "3.11"])]
    df = df[(df["ANO"] >= inicio) & (df["ANO"] <= fim)]

    df_pivot = df.pivot_table(index='PERIODO', columns='DESCRIÇÃO', values='VALOR').reset_index()
    df_pivot.columns.name = None
    df_pivot.columns = ['PERIODO', 'CUSTOS', 'LUCRO LIQUIDO', 'RECEITA LIQUIDA']

    df_final = anls.cria_coluna_mes_ano(df_pivot)
    return df_final

def data_receita_liquida_custos_anual(df, ano_inicio, ano_fim):
    """
    Prepares data for plotting annual net revenue, costs, and net income.

    Parameters:
        df (DataFrame): The DataFrame containing the financial data.
        ano_inicio (int): The start year.
        ano_fim (int): The end year.

    Returns:
        DataFrame: The prepared DataFrame.
    """
    df = df[(df["ANO"] >= ano_inicio) & (df["ANO"] <= ano_fim)]
    df = df[df['CONTA'].isin(["3.02", "3.01", "3.11"])]

    df_pivot = df.pivot_table(index='ANO', columns='DESCRIÇÃO', values='VALOR').reset_index()
    df_pivot.columns.name = None
    df_pivot.columns = ['ANO', 'CUSTOS', 'RECEITA LIQUIDA', 'LUCRO LIQUIDO']
    return df_pivot

def data_bp_anual(df, inicio, fim):
    """
    Prepares annual balance sheet data for plotting.

    Parameters:
        df (DataFrame): The DataFrame containing the financial data.
        inicio (int): The start year.
        fim (int): The end year.

    Returns:
        tuple: DataFrames for assets, liabilities, and equity.
    """
    df = df[['CONTA', 'DESCRIÇÃO', 'VALOR', 'PERIODO', 'ANO', 'MES']]
    df = df[(df["ANO"] >= inicio) & (df["ANO"] <= fim)]

    df_ativo = df[df['CONTA'] == '1'].copy()
    df_ativo_circ = df[df['CONTA'] == '1.01'].copy()
    df_ativo_n_circ = df[df['CONTA'] == '1.02'].copy()
    df_passivo_circ = df[df['CONTA'] == '2.01'].copy()
    df_passivo_n_circ = df[df['CONTA'] == '2.02'].copy()
    df_patrimonio_liq = df[df['CONTA'] == '2.03'].copy()

    lista_passivo = []
    for ano in range(inicio, fim + 1):
        passivo_total = get_valor_anual(df, ano, "2")
        patrimonio_liquido = get_valor_anual(df, ano, "2.03")
        periodo = df.loc[(df['ANO'] == ano) & (df['CONTA'] == "2.03"), 'PERIODO'].iloc[0]
        passivo = passivo_total - patrimonio_liquido

        lista_passivo.append({
            'CONTA': "2",
            'DESCRIÇÃO': "Passivo sem patri liq",
            'VALOR': round(passivo, 2),
            'PERIODO': periodo,
            'ANO': ano
        })

    df_passivo = pd.DataFrame(lista_passivo)
    return df_ativo, df_ativo_circ, df_ativo_n_circ, df_passivo_circ, df_passivo_n_circ, df_patrimonio_liq, df_passivo

def data_bp_trimestral(df, inicio, fim):
    """
    Prepares quarterly balance sheet data for plotting.

    Parameters:
        df (DataFrame): The DataFrame containing the financial data.
        inicio (int): The start year.
        fim (int): The end year.

    Returns:
        tuple: DataFrames for the main data and liabilities without equity.
    """
    df = df[['CONTA', 'DESCRIÇÃO', 'VALOR', 'PERIODO', 'ANO', 'MES']]
    df = df.dropna()
    df = df.sort_values('PERIODO')
    df = df[(df["ANO"] >= inicio) & (df["ANO"] <= fim)]

    lista = []
    for ano in range(inicio, fim + 1):
        for mes in df['MES'].unique():
            filtro_passivo = df.loc[(df['ANO'] == ano) & (df['MES'] == mes) & (df['CONTA'] == "2"), "VALOR"]
            filtro_patrimonio = df.loc[(df['ANO'] == ano) & (df['MES'] == mes) & (df['CONTA'] == "2.03"), "VALOR"]
            if not filtro_passivo.empty and not filtro_patrimonio.empty:
                passivo_total = filtro_passivo.values[0]
                patrimonio_liquido = filtro_patrimonio.values[0]
                periodo = df.loc[(df['ANO'] == ano) & (df['MES'] == mes) & (df['CONTA'] == "2"), "PERIODO"].values[0]
                passivo = passivo_total - patrimonio_liquido

                lista.append({
                    'CONTA': "2",
                    'DESCRIÇÃO': "Passivo sem patri liq",
                    'VALOR': round(passivo, 2),
                    'PERIODO': periodo,
                    'ANO': ano,
                    'MES': mes
                })

    df_passivo_sem_patrimonio = pd.DataFrame(lista)
    return df, df_passivo_sem_patrimonio

def data_margens_anual(df, inicio, fim):
    """
    Calculates annual financial ratios and margins.

    Parameters:
        df (DataFrame): The DataFrame containing the financial data.
        inicio (int): The start year.
        fim (int): The end year.

    Returns:
        tuple: DataFrames for margins, liquidity ratios, pivoted indicators, and all indicators.
    """
    indices = [
        "Líquidez Geral", "Líquidez Corrente", "Líquidez Seca",
        "Líquidez Imediata", "Solvência Geral", "Margem de Lucro",
        "Margem Líquida", "Giro do Ativo"
    ]

    ind_geral = []
    for indice in indices:
        for ano in range(inicio, fim + 1):
            data = ler_contas_anual(df, ano)
            if indice == "Líquidez Geral":
                denominator = data['passivo_circulante'] + data['passivo_nao_circulante']
                numerator = data['ativo_circulante'] + data['realizavel_longo_prazo']
            elif indice == "Líquidez Corrente":
                denominator = data['passivo_circulante']
                numerator = data['ativo_circulante']
            elif indice == "Líquidez Seca":
                denominator = data['passivo_circulante']
                numerator = data['ativo_circulante'] - data['estoque']
            elif indice == "Líquidez Imediata":
                denominator = data['passivo_circulante']
                numerator = data['caixa_eq']
            elif indice == "Solvência Geral":
                denominator = data['passivo_circulante'] + data['passivo_nao_circulante']
                numerator = data['ativo_total']
            elif indice == "Margem de Lucro":
                denominator = data['receita_total']
                numerator = data['lucro_liquido']
                if denominator != 0:
                    resultado = (numerator / denominator) * 100
                else:
                    resultado = float('nan')
                ind_geral.append({'ÍNDICES': indice, 'ANO': ano, 'VALOR': round(resultado, 2)})
                continue
            elif indice == "Margem Líquida":
                denominator = data['receita_liquida']
                numerator = data['lucro_liquido']
                if denominator != 0:
                    resultado = (numerator / denominator) * 100
                else:
                    resultado = float('nan')
                ind_geral.append({'ÍNDICES': indice, 'ANO': ano, 'VALOR': round(resultado, 2)})
                continue
            elif indice == "Giro do Ativo":
                denominator = data['receita_total']
                numerator = data['lucro_liquido']
                if denominator != 0:
                    resultado = numerator / denominator
                else:
                    resultado = float('nan')
                ind_geral.append({'ÍNDICES': indice, 'ANO': ano, 'VALOR': round(resultado, 2)})
                continue

            if denominator != 0:
                resultado = numerator / denominator
            else:
                resultado = float('nan')

            ind_geral.append({'ÍNDICES': indice, 'ANO': ano, 'VALOR': round(resultado, 2)})

    df_indicadores = pd.DataFrame(ind_geral)
    df_indicadores_pivot = df_indicadores.pivot_table(index='ÍNDICES', columns='ANO', values='VALOR').reset_index()
    df_indicadores_pivot.columns.name = None
    df_indicadores_pivot = ordena_tabular_anual(df_indicadores_pivot)

    df_margens = df_indicadores[df_indicadores["ÍNDICES"].isin(["Margem Líquida", "Margem de Lucro"])]
    df_liquidez = df_indicadores[df_indicadores["ÍNDICES"].isin([
        "Líquidez Geral", "Líquidez Corrente", "Líquidez Seca",
        "Líquidez Imediata", "Solvência Geral", "Giro do Ativo"
    ])]

    return df_margens, df_liquidez, df_indicadores_pivot, df_indicadores

def data_margens_trimestral(df, inicio, fim):
    """
    Calculates quarterly financial ratios and margins.

    Parameters:
        df (DataFrame): The DataFrame containing the financial data.
        inicio (int): The start year.
        fim (int): The end year.

    Returns:
        tuple: DataFrames for margins, liquidity ratios, pivoted indicators, and all indicators.
    """
    indices = [
        "Líquidez Geral", "Líquidez Corrente", "Líquidez Seca",
        "Líquidez Imediata", "Solvência Geral", "Margem de Lucro",
        "Margem Líquida", "Giro do Ativo"
    ]

    ind_geral = []
    for indice in indices:
        for ano in range(inicio, fim + 1):
            for mes in df['MES'].unique():
                filtro = df[(df['ANO'] == ano) & (df['MES'] == mes)]
                data = {}
                for conta in ["1", "1.01", "1.02.01", "1.01.04", "1.01.01", "2", "2.01", "2.02", "2.03", "3.03", "3.01", "3.11"]:
                    valor = filtro.loc[filtro['CONTA'] == conta, 'VALOR']
                    data[conta] = valor.values[0] if not valor.empty else 0
                trimestre = filtro['PERIODO'].iloc[0] if not filtro.empty else None

                if indice == "Líquidez Geral":
                    numerator = data['1.01'] + data['1.02.01']
                    denominator = data['2.01'] + data['2.02']
                elif indice == "Líquidez Corrente":
                    numerator = data['1.01']
                    denominator = data['2.01']
                elif indice == "Líquidez Seca":
                    numerator = data['1.01'] - data['1.01.04']
                    denominator = data['2.01']
                elif indice == "Líquidez Imediata":
                    numerator = data['1.01.01']
                    denominator = data['2.01']
                elif indice == "Solvência Geral":
                    numerator = data['1']
                    denominator = data['2.01'] + data['2.02']
                elif indice == "Margem de Lucro":
                    numerator = data['3.11']
                    denominator = data['3.03']
                    if denominator != 0:
                        resultado = (numerator / denominator) * 100
                    else:
                        resultado = float('nan')
                    ind_geral.append({'ÍNDICES': indice, 'TRIMESTRE': trimestre, 'VALOR': round(resultado, 2), 'ANO': ano})
                    continue
                elif indice == "Margem Líquida":
                    numerator = data['3.11']
                    denominator = data['3.01']
                    if denominator != 0:
                        resultado = (numerator / denominator) * 100
                    else:
                        resultado = float('nan')
                    ind_geral.append({'ÍNDICES': indice, 'TRIMESTRE': trimestre, 'VALOR': round(resultado, 2), 'ANO': ano})
                    continue
                elif indice == "Giro do Ativo":
                    numerator = data['3.11']
                    denominator = data['3.03']
                    if denominator != 0:
                        resultado = numerator / denominator
                    else:
                        resultado = float('nan')
                    ind_geral.append({'ÍNDICES': indice, 'TRIMESTRE': trimestre, 'VALOR': round(resultado, 2), 'ANO': ano})
                    continue

                if denominator != 0:
                    resultado = numerator / denominator
                else:
                    resultado = float('nan')

                ind_geral.append({'ÍNDICES': indice, 'TRIMESTRE': trimestre, 'VALOR': round(resultado, 2), 'ANO': ano})

    df_indicadores = pd.DataFrame(ind_geral)
    df_indicadores = ordena_dataframe_decrescente(df_indicadores, inicio, fim)
    df_indicadores_pivot = df_indicadores.pivot_table(index='ÍNDICES', columns='TRIMESTRE', values='VALOR').reset_index()
    df_indicadores_pivot.columns.name = None

    df_margens = df_indicadores[df_indicadores["ÍNDICES"].isin(["Margem Líquida", "Margem de Lucro"])]
    df_liquidez = df_indicadores[df_indicadores["ÍNDICES"].isin([
        "Líquidez Geral", "Líquidez Corrente", "Líquidez Seca",
        "Líquidez Imediata", "Solvência Geral", "Giro do Ativo"
    ])]

    return df_margens, df_liquidez, df_indicadores_pivot, df_indicadores

def data_grafico_margens_dashboard(df):
    """
    Prepares data for dashboard margin graphs.

    Parameters:
        df (DataFrame): The DataFrame containing the financial data.

    Returns:
        DataFrame: The prepared DataFrame with margins.
    """
    ano_fim = df['ANO'].max()
    ano_inicio = ano_fim - 5
    df = df[(df["ANO"] >= ano_inicio) & (df["ANO"] <= ano_fim)]
    df = df[(df["PERIODO"] == 'ANUAL') & (df["DEMONSTRATIVO"] == 'Demonstração do Resultado')]
    df = df.sort_values('ANO')

    indices = ["Lucro", "Líquida"]
    ind_geral = []
    for indice in indices:
        for ano in range(ano_inicio, ano_fim + 1):
            data = ler_contas_anual(df, ano)###################
            if indice == "Lucro":
                denominator = data['receita_total']
                numerator = data['lucro_liquido']
            elif indice == "Líquida":
                denominator = data['receita_liquida']
                numerator = data['lucro_liquido']

            if denominator != 0:
                resultado = (numerator / denominator) * 100
            else:
                resultado = float('nan')

            ind_geral.append({'MARGENS': indice, 'ANO': ano, 'VALOR': round(resultado, 2)})

    df_margens = pd.DataFrame(ind_geral)
    return df_margens

def calcula_indicadores_grafico_dashboard(df):
    """
    Calculates indicators for the dashboard graphs.

    Parameters:
        df (DataFrame): The DataFrame containing the financial data.

    Returns:
        DataFrame: The prepared DataFrame with indicators.
    """
    fim = df['ANO'].max()
    inicio = fim - 5
    df = df[(df["ANO"] >= inicio) & (df["ANO"] <= fim)]
    df = df[df["PERIODO"] == 'ANUAL']
    df = df.sort_values('ANO')

    indices = ["EBITDA", "EBIT", "Bruta"]
    ind_geral = []
    for indice in indices:
        for ano in range(inicio, fim + 1):
            data = ler_contas_anual(df, ano)
            if indice == "EBITDA":
                denominator = data['receita_liquida']
                numerator = data['ebitda']
            elif indice == "EBIT":
                denominator = data['receita_liquida']
                numerator = data['ebit']
            elif indice == "Bruta":
                denominator = data['receita_liquida']
                numerator = data['lucro_bruto']

            if denominator != 0:
                resultado = (numerator / denominator) * 100
            else:
                resultado = float('nan')

            ind_geral.append({'MARGENS': indice, 'ANO': ano, 'VALOR': round(resultado, 2)})

    df_dash = pd.DataFrame(ind_geral)
    return df_dash

def data_dashboard(df):
    """
    Prepares data for the dashboard indicators.

    Parameters:
        df (DataFrame): The DataFrame containing the financial data.

    Returns:
        DataFrame: The prepared DataFrame with dashboard indicators.
    """
    ano_fim = df['ANO'].max()
    anos_disponiveis = sorted(df['ANO'].unique())

    if len(anos_disponiveis) >= 5:
        periodo_5anos = ano_fim - 5
    else:
        periodo_5anos = anos_disponiveis[0]

    df_5anos = df[(df["PERIODO"] == 'ANUAL') & (df["ANO"] == periodo_5anos)]
    df = df[(df["PERIODO"] == 'ANUAL') & (df["ANO"] == ano_fim)]

    data_atual = ler_contas_anual(df, ano_fim)
    data_5anos = ler_contas_anual(df_5anos, periodo_5anos)

    rec_liq_cagr_vi = data_5anos['receita_liquida']
    cagr_lucro_liquido_vi = data_5anos['lucro_liquido']

    divida_bruta = data_atual['emprestimo_curto_prazo'] + data_atual['emprestimo_longo_prazo_valor']
    ebitda = data_atual['ebitda']

    indices = [
        "Div_liq_pl", "Div_liq_ebit", "CAGR RECEITAS", "CAGR LUCROS", "GA", "ROIC",
        "Ebit_rec_liq", "Ebitda_rec_liq", "Div_liq_ebitda", "Margem_liquida",
        "PL_ativos", "Passivos_ativos", "Liq_corrente", "Margem_Bruta", "ROE", "ROA"
    ]

    dash_geral = []
    for indice in indices:
        if indice == "PL_ativos":
            denominator = data_atual['ativo_total']
            numerator = data_atual['ativo_total'] - data_atual['passivo_total']
        elif indice == "CAGR RECEITAS":
            if rec_liq_cagr_vi > 0:
                res = ((data_atual['receita_liquida'] / rec_liq_cagr_vi) ** (1/5) - 1) * 100
            else:
                res = float('nan')
            dash_geral.append({'ANO': ano_fim, 'ÍNDICES': indice, 'VALOR': round(res, 2)})
            continue
        elif indice == "CAGR LUCROS":
            if cagr_lucro_liquido_vi > 0:
                res = ((data_atual['lucro_liquido'] / cagr_lucro_liquido_vi) ** (1/5) - 1) * 100
            else:
                res = float('nan')
            dash_geral.append({'ANO': ano_fim, 'ÍNDICES': indice, 'VALOR': round(res, 2)})
            continue
        elif indice == "ROIC":
            denominator = data_atual['patrimonio_liquido'] + divida_bruta
            numerator = data_atual['ebit'] + data_atual['impostos']
        elif indice == "GA":
            denominator = data_atual['ativo_total']
            numerator = data_atual['receita_liquida']
        elif indice == "Div_liq_pl":
            denominator = data_atual['patrimonio_liquido']
            numerator = divida_bruta
        elif indice == "Div_liq_ebit":
            denominator = data_atual['ebit']
            numerator = divida_bruta
        elif indice == "Div_liq_ebitda":
            denominator = ebitda
            numerator = divida_bruta
        elif indice == "Ebitda_rec_liq":
            denominator = data_atual['receita_liquida']
            numerator = ebitda
        elif indice == "Ebit_rec_liq":
            denominator = data_atual['receita_liquida']
            numerator = data_atual['ebit']
        elif indice == "Passivos_ativos":
            denominator = data_atual['ativo_total']
            numerator = data_atual['passivo_total']
        elif indice == "Liq_corrente":
            denominator = data_atual['passivo_circulante']
            numerator = data_atual['ativo_circulante']
        elif indice == "ROE":
            denominator = data_atual['patrimonio_liquido']
            numerator = data_atual['lucro_liquido']
        elif indice == "ROA":
            denominator = data_atual['ativo_total']
            numerator = data_atual['lucro_liquido']
        elif indice == "Margem_Bruta":
            denominator = data_atual['receita_liquida']
            numerator = data_atual['lucro_bruto']
        elif indice == "Margem_liquida":
            denominator = data_atual['receita_liquida']
            numerator = data_atual['lucro_liquido']

        if denominator != 0:
            res = (numerator / denominator) * 100 if "Margem" in indice or "RO" in indice else numerator / denominator
        else:
            res = float('nan')

        dash_geral.append({'ANO': ano_fim, 'ÍNDICES': indice, 'VALOR': round(res, 2)})

    df_dash = pd.DataFrame(dash_geral)
    return df_dash
