
# coding: utf-8

# In[9]:

import matplotlib.pyplot as plt
from huobi_api_market import *
from huobi_api_trade import *
import time
import numpy as np
from scipy.optimize import curve_fit, leastsq
from scipy.stats import norm
from numpy import exp, log, sqrt, pi
from random import random
import matplotlib.mlab as mlab

np.set_printoptions(suppress=True)
#N_POLLS=10000                            #number of polls for trades
WINDOW_LEN=3000                          #size of the window to use for binned_trades in ticks(POLL_INTERVAL)
POLL_INTERVAL=0.3333                      #time between polls in seconds, too long time interval can cause trades to be missed
N_BINS=1500                               #size of bins for volume profile in CNY
PRICE_RANGE=0.05                         #range of price for binning, 0.05 means 0.95*price and 1.05*price 
DUST_THRESHOLD=0.002                    #trades smaller that this amount in BTC are ignored
WHALE_THRESHOLD=380                      #trades larger that this amount in BTC are ignored

TRADE_TICK=1.0                       #tick time for trading thread in s
LONG_THRESHOLD=1.0                   #n gaussian standard deviations at which algorithm decides to long
SHORT_THRESHOLD=1.0                  #n gaussian standard deviations at which algorithm decides to short
SPREAD=0.0                          #bid-ask spread on huobi in CNY

class portfolio:
    def __init__(self, cny, btc):
        self.cny=cny
        self.btc=btc
    def buy(self, amount, price):        #amount in usd
        if amount>self.cny:
            amount=self.cny
        self.cny-=amount
        self.btc+=float(amount)/(price+SPREAD)
    def sell(self, amount, price):           #amount in btc
        if amount>self.btc:
            amount=self.btc
        self.cny+=amount*(price-SPREAD)
        self.btc-=amount
    def show(self, price):
        print 'CNY: ', self.cny
        print 'BTC: ', self.btc
        print 'Spread: ', SPREAD
        print 'Total CNY equivalent: ', self.cny+self.btc*price

def mergelist(a, b):
    merge_length=1
    if a==b:
        return a
    while merge_length<len(b):
        #print merge_length
        #print a[-merge_length:], b[:merge_length]
        if a[-merge_length:-merge_length+3]==b[:3]:
            return a+b[merge_length:]
            break
        merge_length+=1
    return 'no merge'

def subtractlist(a,b):        #returns new elements in a not in b (a-b)
    merge_length=1
    if a==b:
        return []
    while merge_length<len(b):
        #print merge_length
        #print a[-merge_length:-merge_length+3], b[:3]
        if a[-merge_length:-merge_length+3]==b[:3]:               #if 3 elements are same, lists are merged from that point
            print a[-merge_length:-merge_length+3], b[:3]
            a=a+b[merge_length:]
            #print a
            a=a[:-len(b)]
            return a
        merge_length+=1
    return 'no merge'

def subtractlist2(a,b):          #returns new elements in a not in b (a-b), slower but works better when huobi returns nonsensical trade series
    for i in range(0, len(b)-2, 3):
        for j in range(len(a)-2):
            #print i,j
            if b[i]==a[j] and b[i+1]==a[j+1] and b[i+2]==a[j+2]:
                return a[:j]
    #print 'no match found, cannot merge list, continuing...'
    #print a
    #print ''
    #print b
    return a

def bintrades(trades, bins, binned):         #input trades has to be a sorted list, n makes sure that all trades for 1 tick goes into 1 new entry
    for i in binned:
        binned[i].append(0.0)
    bin_n=0
    j=0
    while j<len(trades):
        #print j, bin_n
        if trades[j][0]>=bins[bin_n] and trades[j][0]<bins[bin_n+1]:
            binned[str(bins[bin_n])][-1]+=trades[j][1] 
        else:
            bin_n+=1
            j-=1
        j+=1
    if len(binned[str(bins[0])])>WINDOW_LEN:
        for key in binned:
            binned[key].pop(0)
    return binned

def purgenoise(trades, dust_thresh, whale_thresh):
    i=0
    while i<len(trades):
        if trades[i][1]<=dust_thresh:
            trades.pop(i)
        elif trades[i][1]>=whale_thresh:
            trades.pop(i)
        i+=1
    return trades

def get_data():
    global binned_trades
    #a=[[2,3],[3,45],[2,3],[1,23],[34,2],[31,3], [32,1]]
    #b=[[1,23],[34,2], [31,3],[32,2],[31,11],[31,11]]
    #print mergelist(a,b)
    #print subtractlist2(a,b)

    bins=np.linspace((1-PRICE_RANGE)*round(get_ticker()['ticker']['last']),(1+PRICE_RANGE)*round(get_ticker()['ticker']['last']),num=N_BINS)
    bins=list(bins)
    bins.append(bins[-1]+(bins[1]-bins[0]))

    binned_trades={}
    for i in range(len(bins)):
        binned_trades[str(bins[i])]=[]

    #print binned_trades[str(bins[84])]
    #print bins[83]

    trades=[]
    raw=get_trades()
    for n in range(len(raw)):
        trades.append([raw[n]['price'], raw[n]['amount']])

    trades=purgenoise(trades, DUST_THRESHOLD, WHALE_THRESHOLD)
    trades=sorted(trades, key=lambda x: x[0])   

    binned_trades=bintrades(trades,bins, binned_trades)

    #for i in range(N_POLLS):
    global ntick
    ntick=0
    print 'Getting data in background...'
    while True:
        ntick+=1
        #print '.',
        trades2=[]
        time.sleep(POLL_INTERVAL)
        #print 'get_trades'
        raw=get_trades()
        #print 'appending trades2'
        for n in range(len(raw)):
            trades2.append([raw[n]['price'], raw[n]['amount']])
        #print 'purging noise'
        trades2=purgenoise(trades2, DUST_THRESHOLD, WHALE_THRESHOLD)
        #print 'substracting list'
        trades_new=subtractlist2(trades2, trades)

        #if abs(len(trades_new)-len(trades))<=3:
            #print 'Some trades might have been missed'
        #    break

        trades_new=sorted(trades_new, key=lambda x: x[0])
        #print 'binning trades'
        binned_trades=bintrades(trades_new, bins, binned_trades)
        trades=trades2


# In[13]:

#p=portfolio(1000.0, 0.5)
#p.show(1222)
#p.sell(100000000.0,1222)
#p.show(1222)


# In[ ]:

import threading
import time

def hist(show=False):
    global histogram
    global mu
    global stdev
    histogram=[]
    #print binned_trades
    for key in binned_trades:
        histogram.append([float(key),sum(binned_trades[key])])

    histogram=sorted(histogram, key=lambda x: x[0]) 
    histogram=np.array(histogram)
    histogram=histogram.transpose()

    dx=histogram[0][1]-histogram[0][0]
    x=np.array(histogram[0])
    y=np.array(histogram[1])
    
    x_mean=sum(y*x)/sum(y)
    #print x_mean
    
    fitfunc  = lambda p, x: p[0]*exp(-0.5*((x-p[1])/p[2])**2)
    errfunc  = lambda p, x, y: (y - fitfunc(p, x))

    init  = [max(y), x_mean, 0.5]

    out   = leastsq(errfunc, init, args=(x, y))
    c = out[0]

    mu=c[1]
    stdev=abs(c[2])
    
    if show==True:
        print 'A=', c[0], ', mu=', mu, ', stdev=',stdev
        plt.axvline(x=mu-stdev*LONG_THRESHOLD, ymin=0, ymax=c[0], color='green')
        plt.axvline(x=mu+stdev*LONG_THRESHOLD, ymin=0, ymax=c[0], color='red')
        plt.bar(x, y, width=x[1]-x[0], color='gray', edgecolor='gray')
        plt.plot(x, fitfunc(c, x))
        plt.show()
        print 'Time period of data: ', len(binned_trades[key])
        print 'Tick N. ', ntick
    
def trade(initialize=False):
    global p
    global price
    global portfolio_history
    global price_history
    time.sleep(30)
    price=get_ticker()['ticker']['last']
    
    while True:
        price=get_ticker()['ticker']['last']
        time.sleep(TRADE_TICK)
        if len(binned_trades.itervalues().next())==WINDOW_LEN:
            hist(show=False)
            buy_price=LONG_THRESHOLD
            #print price, mu-stdev*LONG_THRESHOLD, mu-stdev*SHORT_THRESHOLD
            if price<mu-stdev*LONG_THRESHOLD and p.cny>1:
                print 'Buying at: ', price
                p.buy(99999.0, price)
            elif price>mu+stdev*SHORT_THRESHOLD and p.btc>0.001:
                print 'Selling at: ', price
                p.sell(99999.0, price)
        portfolio_history.append(float(p.cny+p.btc*price))
        price_history.append(initial_equity_btc*float(price))
            
    
def main():
    while True:
        print ''
        cin=str(raw_input('Enter command (hist: show histogram, port: show current portfolio, price: show last BTCCNY, history: portfolio returns): '))
        if cin=='hist':
            print ''
            hist(show=True)
        if cin=='port':
            print ''
            p.show(get_ticker()['ticker']['last'])
        if cin=='price':
            print ''
            print get_ticker()['ticker']['last']
        if cin=='history':
            print ''
            plt.plot(portfolio_history, color='black')
            plt.plot(price_history, color='gray')
            plt.show()


# In[ ]:

price=get_ticker()['ticker']['last']
p=portfolio(1000.0, 0.5)
portfolio_history=[]
price_history=[]
initial_equity_btc=float(p.cny+p.btc*price)/float(price)

t1 = threading.Thread(target=get_data)
t1.start()
print 'Data thread started'
t2 = threading.Thread(target=trade, args=(True,))
t2.start()
print 'Trading thread started'
time.sleep(15)
t3 = threading.Thread(target=main)
t3.start()
print 'Main thread started'

while True:
    time.sleep(30)
    if not t1.isAlive():
        print 'Restarting data thread'
        t1 = threading.Thread(target=get_data)
        t1.start()
    if not t2.isAlive():
        print 'Restarting trading thread'
        t2 = threading.Thread(target=trade, args=(False,))
        t2.start()
    if not t3.isAlive():
        print 'Restarting main thread'
        t3 = threading.Thread(target=main)
        t3.start()


# In[ ]:

#hist()

