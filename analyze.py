import matplotlib.pyplot as plt
import numpy as np

from Stockfighter.Api import StockFighterApi
import logging
import time
import math

api_key = '267658536e6b6eaa862c6b73ecb2cc7a86e795cb'
log_level = logging.DEBUG
api = StockFighterApi(api_key, log_level)

my_account = "KBK68955331" # CHANGE
venue = "YNHDEX" # CHANGE
json = api.venue_stocks(venue)
target_stock = json['symbols'][0]['symbol']

best_bids = np.array([])
best_asks = np.array([])
last = np.array([])

count = 0

while count < 300:
    json = api.stock_quote(venue, target_stock)
    last = np.append(last, json['last'])
    
    json = api.stock_orderbook(venue, target_stock)
    if json['bids']:
        best_bids = np.append(best_bids, json['bids'][0]['price'])
    else:
        best_bids = np.append(best_bids, 0)
    if json['asks']:
        best_asks = np.append(best_asks, json['asks'][0]['price'])
    else:
        best_asks = np.append(best_asks, 0)
        
    time.sleep(1)
    count += 1
    print count

plt.plot(last, 'r--')
plt.plot(best_asks, 'bo')
plt.plot(best_bids, 'go')
plt.show()
