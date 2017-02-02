#!/usr/bin/python3

import io
import requests
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
from datetime import datetime, timedelta

import localsetting as ls


pwd = ls.PASSWORD
host = ls.HOST


def get_krx_stock_marcap(schdate):
    # STEP 1.
    gen_otp_url = 'http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx'
    gen_otp_data = {
        'name': 'fileDown',
        'filetype':'xls',
        'url': 'MKD/04/0404/04040200/mkd04040200_01',
        'market_gubun': 'ALL',
        'indx_ind_cd': '',
        'sect_tp_cd': 'ALL',
        #'schdate': '20170201',
        'schdate': schdate,
        'pagePath':'/contents/MKD/04/0404/04040200/MKD04040200.jsp',
    }
    r = requests.post(gen_otp_url, gen_otp_data)
    code = r.content

    # STEP 2.
    down_url = 'http://file.krx.co.kr/download.jspx'
    down_data = {
        'code': code,
    }

    r = requests.post(down_url, down_data)
    f = io.BytesIO(r.content)
    
    usecols = ['종목코드', '종목명', '현재가', '대비', '등락률', '거래량', '거래대금', '시가총액', '상장주식수(천주)', '외국인 보유주식수', '외국인 지분율(%)']
    df = pd.read_excel(f, usecols=usecols)
    df.columns = ['code', 'name', 'price', 'net_change', 'change_ratio', 'volume', 'trade_amnt', 'marcap', 'stocks', 'for_stocks', 'for_ratio']

    int_cols = ['price','net_change', 'change_ratio', 'volume', 'trade_amnt', 'marcap', 'stocks', 'for_stocks', 'for_ratio']
    df[int_cols] = df[int_cols].replace(to_replace=',', value='', regex=True)

    return df


create_table_sql = """
    create table if not exists stock_marcap(
        date datetime,
        code varchar(20), 
        name varchar(50),
        price int,
        net_change int,
        change_ratio int,
        volume bigint,
        trade_amnt bigint,
        marcap bigint,
        stocks bigint,
        for_stocks bigint,
        for_ratio bigint,
        primary key (date, code)
)
"""

insert_sql = """
    replace into stock_marcap(date, code, name, price, net_change, change_ratio, volume, trade_amnt, marcap, stocks, for_stocks, for_ratio)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

if __name__ == "__main__":
    cnx_str = 'mysql+mysqlconnector://admin:'+pwd+'@'+host+'/findb'
    engine = create_engine(cnx_str, echo=False)
    engine.execute(create_table_sql)


    # DB의 마지막 저장일 구하기
    last_datetime = None
    sql = "select max(date) as maxdate from stock_marcap"
    result = engine.execute(sql)
    result_list = result.fetchall()
    last_datetime = result_list[0][0]

    if last_datetime is None:
        last_datetime = datetime(2000, 1, 1)
    today = datetime.today()
    d = last_datetime
    delta = today - datetime(d.year, d.month, d.day)

    for i in range(delta.days + 1):
        try:
            d = last_datetime + timedelta(days=i)
            schdate = d.strftime("%Y%m%d")
            print("Get marcap data at {}".format(schdate))
            df_marcap = get_krx_stock_marcap(schdate)
            print('> ', df_marcap.shape)

            for ix, r in df_marcap.iterrows():
                engine.execute(insert_sql, (d.strftime('%Y-%m-%d %H:%M:%S'), r['code'], r['name'], r['price'], r['net_change'], r['change_ratio'], r['volume'], r['trade_amnt'], r['marcap'], r['stocks'], r['for_stocks'], r['for_ratio'] ))
        except Exception as e:
            print('> Exception: ', e.args[0])

#    df = get_krx_stock_marcap()
#    print(df)
