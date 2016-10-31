from Stockfighter.Api import StockFighterApi
import logging
import time

api_key = '267658536e6b6eaa862c6b73ecb2cc7a86e795cb'
log_level = logging.DEBUG
api = StockFighterApi(api_key, log_level)

my_account = "BPS4143581" # CHANGE
venue = "IVCEX" # CHANGE
json = api.venue_stocks(venue) 

target_stock = json['symbols'][0]['symbol']

def best_bid():
	json = api.stock_orderbook(venue, target_stock)
	if 'bids' in json:
		return json['bids'][-1]
	else:
		time.sleep(1)
		return best_bid()

def last_bid():
	json = api.stock_quote(venue, target_stock)
	# if 'ask' not in json or 'bid' not in json:
	# 	time.sleep(0.5)
	# 	last_bid()
	return json


def basic_strategy():

	total = 0
	while total < 100000:
		quote = last_bid()

		price = int(quote['last'] - quote['last'] / 100)
		qty = int(5000)

		json = api.stock_order(venue, my_account, target_stock, price, qty, 'buy', 'limit')
		order_id = json['id']

		time.sleep(8)
		json = api.stock_order_cancel(venue, target_stock, order_id)
		
		total += json['totalFilled']

		print("Captain, we have ", total, " bought out of 100,000!")
		print("---------------------------------------------")

basic_strategy()
