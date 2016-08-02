
# coding: utf-8

# In[1]:

import urllib2
from urllib2 import URLError
import json

btc_ticker='http://api.huobi.com/staticmarket/ticker_btc_json.js'
btc_depth='http://api.huobi.com/staticmarket/depth_btc_json.js'
btc_1min='http://api.huobi.com/staticmarket/btc_kline_[period]_json.js'

def get_ticker():
    while True:
        try:
            a=json.loads(urllib2.urlopen(btc_ticker).read())
            return a
        except urllib2.URLError, e:
            print 'Timeout error'

def get_depth():
    return json.loads(urllib2.urlopen(btc_depth).read())

def get_candle(time):
    url='http://api.huobi.com/staticmarket/btc_kline_'+str(time)+'_json.js'
    return json.loads(urllib2.urlopen(url).read())

def get_trades():
    url='http://api.huobi.com/staticmarket/detail_btc_json.js'
    while True:
        try:
            a=json.loads(urllib2.urlopen(url).read())['trades']
            return a
        except urllib2.URLError, e:
            print 'Timeout error'
        

