#!/bin/python3

# update coin price in yiimp using foreign exchanges
# barrystyle 13092022

import requests, pymysql, os, sys, time, json

coingecko_init = False
coingecko_list = []

def fetch_vs_currency_cryptocompare(ticker, base, apikey):
    base_url = 'https://min-api.cryptocompare.com/data/price?fsym=XXXXX&tsyms=YYYYY&api_key=ZZZZZ'
    data_url = base_url.replace('XXXXX', ticker).replace('YYYYY', base).replace('ZZZZZ', apikey)
    try:
        t = requests.get(data_url)
        r = json.loads(t.text)
        return r[base.upper()]
    except:
        return None

def fetch_vs_currency_coingecko_init():
    global coingecko_init
    global coingecko_list
    coin_url = 'https://api.coingecko.com/api/v3/coins/list'
    if coingecko_init is True:
        return
    try:
        t = requests.get(coin_url)
        coingecko_list = json.loads(t.text)
        coingecko_init = True
    except:
        return

def fetch_currency_id_coingecko(symbol):
    global coingecko_init
    global coingecko_list
    sym = symbol.lower()
    fetch_vs_currency_coingecko_init()
    retitem = None
    for item in coingecko_list:
        if sym in item['symbol']:
           if len(sym) == len(item['symbol']):
              retitem = item
    return retitem['id']

def fetch_currency_price_coingecko(id, base):
    base_url = 'https://api.coingecko.com/api/v3/simple/price?ids=XXXXX&vs_currencies=YYYYY'
    data_url = base_url.replace('XXXXX', id).replace('YYYYY', base)
    try:
        t = requests.get(data_url)
        r = json.loads(t.text)
        return r[id][base]
    except:
        return None

def coingecko_simple_call(symbol, base):
    id = fetch_currency_id_coingecko(symbol)
    if id is None:
        return
    price = fetch_currency_price_coingecko(id, base)
    if price is None:
        return
    return price

def update_local_currencies(base, apikey, dbname, username, password, site):
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

            # allow a different api source
            if site == 0:
                cur_price = fetch_vs_currency_cryptocompare(cur_ticker, base, apikey)
            else:
                cur_price = coingecko_simple_call(cur_ticker, base)

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
src_site = 1            # 0 for cryptocompare or 1 for coingecko

update_local_currencies(base_currency, api_key, db_name, db_user, db_pass, src_site)
