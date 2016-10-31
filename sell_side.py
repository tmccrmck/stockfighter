from Stockfighter.Api import StockFighterApi
import logging
import time

api_key = '267658536e6b6eaa862c6b73ecb2cc7a86e795cb'
log_level = logging.DEBUG
api = StockFighterApi(api_key, log_level)

my_account = "EHH47508772" # CHANGE
venue = "MMSBEX" # CHANGE
json = api.venue_stocks(venue) 

target_stock = json['symbols'][0]['symbol']

class L(list):
	def append(self, item):
		list.append(self, item)
		if len(self) > 20: self[:1]=[]

def basic_strategy():
	position = 0
	last_trades = L()
	money = 0
	nav = 0

	sell_multiplier = 0.03
	buy_multiplier = 0.03
	# json = api.account_stock_orders(venue, my_account, target_stock)

	# for order in json['orders']:
	# 	for fill in order['fills']:
	# 		if order['direction'] is 'buy':
	# 			position += fill['qty']
	# 			money = money - (fill['qty'] * fill['price'])
	# 		elif order['direction'] is 'sell':
	# 			position -= fill['qty']
	# 			money = money + (fill['qty'] * fill['price'])

	while money < 1000000:
		sold = False
		bought = False

		json = api.stock_quote(venue, target_stock)
		last_trades.append(json['last'])
		if len(last_trades) < 20:
			time.sleep(0.5)
			continue
		average = sum(last_trades) / 20

		json = api.stock_orderbook(venue, target_stock)
		if json['bids']:
			bestPrice = json['bids'][0]['price']
			priceNeeded = average + (sell_multiplier * average)
			qty = min(json['bids'][0]['qty'], max(abs(position), 100))
			# print("Current best price is %s and only selling if > %s" % (bestPrice, priceNeeded))
			if bestPrice > priceNeeded:
				sell = api.stock_order(venue, my_account, target_stock, bestPrice, qty, 'sell', 'limit')
				sold = True

		json = api.stock_orderbook(venue, target_stock)
		if json['asks']:
			bestPrice = json['asks'][0]['price']
			priceNeeded = average - (buy_multiplier * average)
			qty = min(json['bids'][0]['qty'], max(abs(position), 100))
			# print("Current best price is %s and only buying if < %s" % (bestPrice, priceNeeded))
			if bestPrice < average - (buy_multiplier * average):
				buy = api.stock_order(venue, my_account, target_stock, bestPrice, qty, 'buy', 'limit')
				bought = True

		time.sleep(1)

		if sold:
			json = api.stock_order_cancel(venue, target_stock, sell['id'])
			for fill in json['fills']:
				position -= fill['qty']
				money = money + (fill['qty'] * fill['price'])
		if bought:
			json = api.stock_order_cancel(venue, target_stock, buy['id'])
			for fill in json['fills']:
				position += fill['qty']
				money = money - (fill['qty'] * fill['price'])

		print("Cash = $", money / 100.0)
		print("position = ", position)
		print("Nav = ", nav)
		print("---------------------------------------------")

basic_strategy()