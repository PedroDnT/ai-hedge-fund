from utils import get_default_period_init, get_default_period_end
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import json

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
            'is_b3_listed': company['is_b3_listed'],
            'sector': company.get('sector'),
            'subsector': company.get('subsector'),
            'segment': company.get('segment')
        } for company in companies if company['is_b3_listed']]
    else:
        raise Exception(f"Failed to list companies: {response.status_code} {response.text}")

def get_balance_sheet(cvm_code, statement_type="con", reference_date=None):
    '''Retorna o balanço patrimonial da empresa.
    Parâmetros:
        cvm_code (str): Código CVM da empresa
        statement_type (str): Tipo de demonstração. Valores possíveis: con, ind
        reference_date (str): Data de referência no formato %Y-%m-%d
    '''
    url = f"{base_url}/companies/{cvm_code}/balances"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {"statement_type": statement_type}
    if reference_date:
        params["reference_date"] = reference_date
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get balance sheet: {response.status_code} {response.text}")

def get_income_statements(cvm_code, statement_type="con", period_type="year"):
    '''Retorna a demonstração de resultados da empresa.
    Parâmetros:
        cvm_code (str): Código CVM da empresa
        statement_type (str): Tipo de demonstração. Valores possíveis: con, ind
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
    '''Retorna o fluxo de caixa da empresa.
    Parâmetros:
        cvm_code (str): Código CVM da empresa
        statement_type (str): Tipo de demonstração. Valores possíveis: con, ind
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

def get_financial_ratios(cvm_code, statement_type="con", period_type="ttm"):
    '''Retorna os indicadores financeiros da empresa.
    Parâmetros:
        cvm_code (str): Código CVM da empresa
        statement_type (str): Tipo de demonstração. Valores possíveis: con, ind
        period_type (str): Tipo de período. Valores possíveis: ttm, year
    '''
    url = f"{base_url}/companies/{cvm_code}/ratios"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {"statement_type": statement_type, "period_type": period_type}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get financial ratios: {response.status_code} {response.text}")

def get_market_ratios(cvm_code, statement_type="con", period_init=None, period_end=None):
    '''Retorna os indicadores de mercado da empresa.
    Parâmetros:
        cvm_code (str): Código CVM da empresa
        statement_type (str): Tipo de demonstração. Valores possíveis: con, ind
        period_init (str): Data inicial no formato %Y-%m-%d
        period_end (str): Data final no formato %Y-%m-%d
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

def get_quotes(ticker, period_init=None, period_end=None):
    '''Retorna as cotações do ativo.
    Parâmetros:
        ticker (str): Código do ativo na B3
        period_init (str): Data inicial no formato %Y-%m-%d
        period_end (str): Data final no formato %Y-%m-%d
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

def list_tickers():
    '''Retorna a lista de ativos disponíveis.'''
    url = f"{base_url}/tickers"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    params = {"ticker_type": "stock"}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to list tickers: {response.status_code} {response.text}")

def list_funds():
    '''Retorna a lista de fundos de investimento.'''
    url = f"{base_url}/funds"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to list funds: {response.status_code} {response.text}")

def match_company_data():
    '''Retorna DataFrame com dados combinados de empresas e tickers'''
    companies = list_cia()
    tickers = list_tickers()
    
    # Create DataFrames
    df_companies = pd.DataFrame(companies)
    df_tickers = pd.DataFrame(tickers)
    
    # Remove duplicates based on issuer_code
    df_tickers_unique = df_tickers.drop_duplicates(
        subset=['issuer_code'], 
        keep='first'
    )
    
    # Merge using trade_name and name
    df_merged = pd.merge(
        df_companies,
        df_tickers_unique[['name', 'isin', 'issuer_code', 'ticker']],
        left_on='trade_name',
        right_on='name',
        how='inner'
    )
    
    return df_merged 