#!/usr/bin/env python
# -*- coding: utf-8 -*-

# stock_finstate.py

import time
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
import requests
import mysql.connector
from sqlalchemy import create_engine

# pwd=input('Enter Password for server:')
pwd = 'cansentme'

def get_finstate_naver(code, fin_type='4', freq_type='Y'):
    '''
    * code: 종목코드
    * fin_type = '0': 재무제표 종류 (0: 주재무제표, 1: GAAP개별, 2: GAAP연결, 3: IFRS별도, 4:IFRS연결)
    * freq_type = 'Y': 기간 (Y:년, Q:분기)
    '''
    url_tmpl = 'http://companyinfo.stock.naver.com/v1/company/ajax/cF1001.aspx?' \
                   'cmp_cd=%s&fin_typ=%s&freq_typ=%s'

    url = url_tmpl % (code, fin_type, freq_type)

    dfs = pd.read_html(url)
    df = dfs[0]
    df = df.set_index('주요재무정보')
    df = df.T
    freq_type_map = {'Q':'분기', 'Y':'연간'}
    df = df.drop(freq_type_map[freq_type])
    df = df.reset_index()
    df = df.rename(columns={'index': 'date'})
    df['code'] = code
    df['fin_type'] = ''
    df['freq_type'] = freq_type
    for ix, r in df.iterrows():
        date_str = r['date'].replace('\t', '').replace('\n', '')
        date_str = date_str.replace('(E)', '')
        date_str = date_str.replace('/', '-')
        date_str = date_str.replace(')', '')
        try:
            df.set_value(ix, 'date', date_str.split('(')[0])
            df.set_value(ix, 'fin_type', date_str.split('(')[1])
        except:
            df.set_value(ix, 'date', '')
        
    cols = df.columns.tolist()
    cols = cols[-3:] + cols[:-3]
    df = df[cols]
    return df

if __name__ == "__main__":
    cnx_str = 'mysql+mysqlconnector://admin:'+pwd+'@localhost/findb'
    engine = create_engine(cnx_str, echo=False)

    df_master = pd.read_sql("SELECT * FROM stock_master", engine)
    for idx, r in df_master.iterrows():
        print(r['code'], r['name'])
        df = get_finstate_naver(r['code'], fin_type='4', freq_type='Q')
        df.to_sql('stock_finstate', con=engine, if_exists='append', index=False)
        df = get_finstate_naver(r['code'], fin_type='4', freq_type='Y')
        df.to_sql('stock_finstate', con=engine, if_exists='append', index=False)
