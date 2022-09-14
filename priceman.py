#!/bin/python3

# update coin price in yiimp using foreign exchanges
# barrystyle 13092022

import requests, pymysql, os, sys, time, json

def fetch_vs_currency(ticker, base, apikey):
    base_url = 'https://min-api.cryptocompare.com/data/price?fsym=XXXXX&tsyms=YYYYY&api_key=ZZZZZ'
    data_url = base_url.replace('XXXXX', ticker).replace('YYYYY', base).replace('ZZZZZ', apikey)
    try:
        t = requests.get(data_url)
        r = json.loads(t.text)
        return r[base.upper()]
    except:
        return None

def update_local_currencies(base, apikey, dbname, username, password):
    try:
        connection = pymysql.connect(host='localhost',
                                 user=username,
                                 password=password,
                                 database=dbname,
                                 cursorclass=pymysql.cursors.DictCursor,
                                 autocommit=True)
        cursor = connection.cursor()

        # batch all currencies
        sql = 'SELECT * FROM `coins`'
        cursor.execute(sql)
        result = cursor.fetchall()

        # update all at once
        for item in result:
            cur_id = item['id']
            cur_ticker = item['symbol']
            cur_price = fetch_vs_currency(cur_ticker, base, apikey)
            if cur_price is None:
                pass
            sql = 'UPDATE coins ' + \
                  'SET price = ' + str(cur_price) + ' ' + \
                  'WHERE id = ' + str(cur_id)
            cursor.execute(sql)
            print ('updated ' + str(cur_ticker) + ' to ' + str(cur_price) + ' ' + base.upper())
    except:
        print ('error')

###################
base_currency = 'btc'
api_key = ''            # get one from https://min-api.cryptocompare.com/
db_name = 'yiimp'       # or yiimpfrontend
db_user = ''
db_pass = ''

update_local_currencies(base_currency, api_key, db_name, db_user, db_pass)
