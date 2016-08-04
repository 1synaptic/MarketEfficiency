
# coding: utf-8

# In[46]:


import hashlib
import time
import urllib2
import urllib
import urlparse  


#在此输入您的Key
ACCESS_KEY = "df0a91d2-5a427d51-2c8afed4-3c41d"
SECRET_KEY = "11dd47eb-98ce24b3-be34dfb8-5c60a"
#don't even try it, it's a throwaway account


HUOBI_SERVICE_API="https://api.huobi.com/apiv3"
ACCOUNT_INFO = "get_account_info"
GET_ORDERS = "get_orders"
ORDER_INFO = "order_info"
BUY = "buy"
BUY_MARKET = "buy_market"
CANCEL_ORDER = "cancel_order"
NEW_DEAL_ORDERS = "get_new_deal_orders"
ORDER_ID_BY_TRADE_ID = "get_order_id_by_trade_id"
SELL = "sell"
SELL_MARKET = "sell_market"

'''
发送信息到api
'''
def send2api(pParams, extra):
	pParams['access_key'] = ACCESS_KEY
	pParams['created'] = int(time.time())
	pParams['sign'] = createSign(pParams)
	if(extra) :
		for k in extra:
			v = extra.get(k)
			if(v != None):
				pParams[k] = v
		#pParams.update(extra)
	tResult = httpRequest(HUOBI_SERVICE_API, pParams)
	return tResult

'''
生成签名
'''
def createSign(params):
	params['secret_key'] = SECRET_KEY;
	params = sorted(params.items(), key=lambda d:d[0], reverse=False)
	message = urllib.urlencode(params)
	message=message.encode(encoding='UTF8')
	m = hashlib.md5()
	m.update(message)
	m.digest()
	sig=m.hexdigest()
	return sig

'''
request
'''
def httpRequest(url, params):
    postdata = urllib.urlencode(params)
    postdata = postdata.encode('utf-8')

    fp = urllib.urlopen(url, postdata)
    #if fp.status != 200 :
        #return None
    #else:
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    fp.close()
    return mystr


# In[52]:


'''
获取账号详情
'''
def getAccountInfo(method):
	params = {"method":method}
	extra = {}
	res = send2api(params, extra)
	return res
'''
获取所有正在进行的委托
'''
def getOrders(coinType,method):
	params = {"method":method}
	params['coin_type'] = coinType
	extra = {}
	res = send2api(params, extra)
	return res
'''
获取订单详情
@param coinType
@param id
'''
def getOrderInfo(coinType,id,method):
	params = {"method":method}
	params['coin_type'] = coinType
	params['id'] = id
	extra = {}
	res = send2api(params, extra)
	return res

'''
限价买入
@param coinType
@param price
@param amount
@param tradePassword
@param tradeid
@param method
'''
def buy(coinType,price,amount,tradePassword,tradeid,method):
	params = {"method":method}
	params['coin_type'] = coinType
	params['price'] = price
	params['amount'] = amount
	extra = {}
	extra['trade_password'] = tradePassword
	extra['trade_id'] = tradeid
	res = send2api(params, extra)
	return res

'''
限价卖出
@param coinType
@param price
@param amount
@param tradePassword
@param tradeid
'''
def sell(coinType,price,amount,tradePassword,tradeid,method):
	params = {"method":method}
	params['coin_type'] = coinType
	params['price'] = price
	params['amount'] = amount
	extra = {}
	extra['trade_password'] = tradePassword
	extra['trade_id'] = tradeid
	res = send2api(params, extra)
	return res

'''
市价买
@param coinType
@param amount
@param tradePassword
@param tradeid
'''

def buyMarket(coinType,amount,tradePassword,tradeid,method):
	params = {"method":method}
	params['coin_type'] = coinType
	params['amount'] = amount
	extra = {}
	extra['trade_password'] = tradePassword
	extra['trade_id'] = tradeid
	res = send2api(params, extra)
	return res

'''
市价卖出
@param coinType
@param amount
@param tradePassword
@param tradeid
'''
def sellMarket(coinType,amount,tradePassword,tradeid,method):
	params = {"method":method}
	params['coin_type'] = coinType
	params['amount'] = amount
	extra = {}
	extra['trade_password'] = tradePassword
	extra['trade_id'] = tradeid
	res = send2api(params, extra)
	return res

'''
查询个人最新10条成交订单
@param coinType
'''
def getNewDealOrders(coinType,method):
	params = {"method":method}
	params['coin_type'] = coinType
	extra = {}
	res = send2api(params, extra)
	return res
'''
根据trade_id查询oder_id
@param coinType
@param tradeid
'''
def getOrderIdByTradeId(coinType,tradeid,method):
	params = {"method":method}
	params['coin_type'] = coinType
	params['trade_id'] = tradeid
	extra = {}
	res = send2api(params, extra)
	return res


'''
撤销订单
@param coinType
@param id
'''

def cancelOrder(coinType,id,method):
	params = {"method":method}
	params['coin_type'] = coinType
	params['id'] = id
	extra = {}
	res = send2api(params, extra)
	return res

