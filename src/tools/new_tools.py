from utils import get_default_period_init, get_default_period_end
import pandas as pd
import requests
import requests
import os
from dotenv import load_dotenv
import json
import pandas as pd

load_dotenv()

base_url = "https://api.dadosdemercado.com.br/v1"
bearer_token = os.getenv("BEARER_TOKEN")

def list_cia():
    '''Retorna lista de empresas listadas na B3 com campos: nome, nome comercial e código CVM'''
    url = f"{base_url}/companies"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        companies = response.json()
        return [{
            'name': company['name'],
            'trade_name': company['trade_name'],
            'cvm_code': company['cvm_code'],
            'is_b3_listed': company['is_b3_listed']
        } for company in companies if company['is_b3_listed']]
    else:
        raise Exception(f"Failed to list companies: {response.status_code} {response.text}")


def get_balance_sheet(cvm_code, statement_type="con", reference_date="2024-01-01"):
    '''Retorna a lista de balanços divulgados pela empresa.
    Parâmetros:
        cvm_code (str): Código CVM da empresa
        statement_type (str): Tipo de resultado. Valores possíveis: con, ind, con*, ind*
        reference_date (str): Data de referência do balanço no formato %Y-%m-%d
    '''
    url = f"{base_url}/companies/{cvm_code}/balances"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {"reference_date": reference_date, "statement_type": statement_type}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get balance sheet: {response.status_code} {response.text}")

def get_income_statements(cvm_code, statement_type="con", period_type="year"):
    '''Retorna a lista de resultados divulgados pela empresa.
    Parâmetros:
        cvm_code (str): Código CVM da empresa
        statement_type (str): Tipo de resultado. Valores possíveis: con, ind, con*, ind*
        period_type (str): Tipo de período. Valores possíveis: ttm, quarter, year
    '''
    url = f"{base_url}/companies/{cvm_code}/incomes"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {"statement_type": statement_type, "period_type": period_type}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get income statements: {response.status_code} {response.text}")

def get_cash_flows(cvm_code, statement_type="con", period_type="year"):
    '''Retorna a lista de fluxos de caixa divulgados pela empresa.
    Parâmetros:
        cvm_code (str): Código CVM da empresa
        statement_type (str): Tipo de resultado. Valores possíveis: con, ind, con*, ind*
        period_type (str): Tipo de período. Valores possíveis: ttm, quarter, year
    '''
    url = f"{base_url}/companies/{cvm_code}/cash_flows"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {"statement_type": statement_type, "period_type": period_type}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get cash flows: {response.status_code} {response.text}")


def get_market_ratios(cvm_code, statement_type="con", period_init=get_default_period_init(get_default_period_end()).strftime('%Y-%m-%d'),   
                      period_end=get_default_period_end().strftime('%Y-%m-%d')):
    '''Retorna o histórico de indicadores de mercado da empresa.
    Parâmetros:
        cvm_code (str): Código CVM da empresa
        statement_type (str): Tipo de resultado. Valores possíveis: con, ind, con*, ind*
        period_init (str): Data de início dos indicadores
        period_end (str): Data de fim dos indicadores
    '''
    url = f"{base_url}/companies/{cvm_code}/market_ratios"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {"statement_type": statement_type}
    if period_init:
        params["period_init"] = period_init
    if period_end:
        params["period_end"] = period_end
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get market ratios: {response.status_code} {response.text}")
    
def get_financial_ratios(cvm_code, statement_type="con", period_type="ttm"):
    '''Retorna a lista de indicadores financeiros por período da empresa.
    Parâmetros:
        cvm_code (str): Código CVM da empresa
        statement_type (str): Tipo de resultado. Valores possíveis: con, ind, con*, ind*
        period_type (str): Tipo de período. Valores possíveis: year, ttm
    '''
    url = f"{base_url}/companies/{cvm_code}/ratios"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {"statement_type": statement_type, "period_type": period_type}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get financial ratios: {response.status_code} {response.text}")


def get_quotes(ticker, period_init=None, period_end=None):
    '''Retorna um DataFrame com cotações para um ativo.
    Parâmetros:
        ticker (str): Código do ticker na B3
        period_init (str): Data de início das cotações
        period_end (str): Data de fim das cotações
    '''
    url = f"{base_url}/tickers/{ticker}/quotes"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {}
    if period_init:
        params["period_init"] = period_init
    if period_end:
        params["period_end"] = period_end
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df[['open', 'close', 'adj_close', 'min', 'max', 'volume']]
    else:
        raise Exception(f"Failed to get quotes: {response.status_code} {response.text}")
    

def list_cia():
    '''Retorna lista de empresas listadas na B3 com campos: nome, nome comercial e código CVM'''
    url = f"{base_url}/companies"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        companies = response.json()
        return [{
            'name': company['name'],
            'trade_name': company['trade_name'],
            'cvm_code': company['cvm_code'],
            'is_b3_listed': company['is_b3_listed']
        } for company in companies if company['is_b3_listed']]
    else:
        raise Exception(f"Failed to list companies: {response.status_code} {response.text}")

def list_funds():
    '''Retorna a lista de fundos de investimento disponíveis na plataforma.
    Retorna:
        begin_date: Data de início do fundo
        benchmark: Benchmark do fundo
        cnpj: CNPJ do fundo
        fund_class: Classe do fundo
        cvm_code: Código CVM
        name: Razão social
        trade_name: Nome do fundo
        net_worth: Patrimônio líquido
        shareholders: Número de cotistas
        type: Tipo do fundo
        management_fee: Taxa de administração
        performance_fee: Taxa de performance
        management_fee_description: Descrição da taxa de administração
        performance_fee_description: Descrição da taxa de performance
    '''
    url = f"{base_url}/funds"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        funds = response.json()
        return [{
            'begin_date': fund.get('begin_date'),
            'benchmark': fund.get('benchmark'),
            'cnpj': fund.get('cnpj'),
            'fund_class': fund.get('fund_class'),
            'cvm_code': fund.get('cvm_code'),
            'name': fund.get('name'),
            'trade_name': fund.get('trade_name'),
            'net_worth': fund.get('net_worth'),
            'shareholders': fund.get('shareholders'),
            'type': fund.get('type'),
            'management_fee': fund.get('management_fee'),
            'performance_fee': fund.get('performance_fee'),
            'management_fee_description': fund.get('management_fee_description'),
            'performance_fee_description': fund.get('performance_fee_description')
        } for fund in funds]
    else:
        raise Exception(f"Failed to list funds: {response.status_code} {response.text}")

def list_tickers():
    '''Retorna a lista de tickers disponíveis na plataforma.'' 
    Retorna:
    [{
        'change': float,  # Variação percentual
        'currency': str,  # Moeda de negociação
        'isin': str,  # Código ISIN
        'issuer_code': str,  # Código do emissor
        'last_quote': {  # Última cotação
            'adj_close': float,  # Preço de fechamento ajustado
            'close': float,  # Preço de fechamento
            'date': str,  # Data
            'max': float,  # Preço máximo
            'min': float,  # Preço mínimo 
            'open': float,  # Preço de abertura
            'volume': int  # Volume negociado
        },
        'market': str,  # Mercado
        'market_type': str,  # Tipo de mercado
        'name': str,  # Nome da empresa
        'penultimate_quote': {  # Penúltima cotação
            'adj_close': float,
            'close': float,
            'date': str,
            'max': float,
            'min': float,
            'open': float,
            'volume': int
        },
        'ticker': str,  # Código de negociação
        'type': str  # Tipo do ativo
    }]'''

    url = f"{base_url}/tickers"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {"ticker_type": "stock"}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:     
        return response.json()
    else:
        raise Exception(f"Failed to list companies: {response.status_code} {response.text}")

def match_company_data():
    '''Retorna DataFrame com dados combinados de empresas e tickers, sem duplicatas'''
    companies = list_cia()
    tickers = list_tickers()
    
    # Criar DataFrame base com empresas
    df_companies = pd.DataFrame(companies)
    
    # Criar DataFrame com tickers
    df_tickers = pd.DataFrame(tickers)
    
    # Remover duplicatas baseado no issuer_code (mantendo primeira ocorrência)
    df_tickers_unique = df_tickers.drop_duplicates(
        subset=['issuer_code'], 
        keep='first'
    )
    
    # Fazer o merge usando trade_name e name como chaves
    df_merged = pd.merge(
        df_companies,
        df_tickers_unique[['name', 'isin', 'issuer_code']],
        left_on='trade_name',
        right_on='name',
        how='inner'
    )
    
    # Limpar e reorganizar colunas
    df_merged = df_merged[[
        'name_x',
        'trade_name',
        'cvm_code',
        'isin',
        'issuer_code'
    ]].rename(columns={'name_x': 'name'})
    
    return df_merged

