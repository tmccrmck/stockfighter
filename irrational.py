from Stockfighter.Api import StockFighterApi
import logging
import time
import math
from functools import reduce

api_key = '267658536e6b6eaa862c6b73ecb2cc7a86e795cb'
log_level = logging.NOTSET
api = StockFighterApi(api_key, log_level)

my_account = "BS93345148" # CHANGE
venue = "ABKBEX" # CHANGE
json = api.venue_stocks(venue) 

target_stock = json['symbols'][0]['symbol']

class L(list):
	def append(self, item):
		list.append(self, item)
		if len(self) > 20: self[:1]=[]

def update_history():
	revenue = 0
	cost = 0
	json = api.account_stock_orders(venue, my_account, target_stock)

	sellOrders = list(filter(lambda order: order['direction'] == 'sell', json['orders']))
	buyOrders = list(filter(lambda order: order['direction'] == 'buy', json['orders']))

	sharesSold = reduce(lambda x, sell: x + sell['totalFilled'], sellOrders, 0)
	sharesPurchased = reduce(lambda x, sell: x + sell['totalFilled'], buyOrders, 0)

	for order in sellOrders:
		revenue += reduce(lambda rev, sell: rev + (sell['qty'] * sell['price']), order['fills'], 0)
	for order in buyOrders:
		cost += reduce(lambda rev, sell: rev + (sell['qty'] * sell['price']), order['fills'], 0)

	return sharesSold, sharesPurchased, revenue, cost

def get_multipliers(numShares):
	if numShares > 0:
		sell_multiplier = .03 - math.log(abs(numShares),70) / 100
		buy_multiplier = 0.02 + math.log(abs(numShares),70) / 100
	elif numShares < 0:
		sell_multiplier = .03 + math.log(abs(numShares),70) / 100
		buy_multiplier = 0.02 - math.log(abs(numShares),70) / 100
	else:
		sell_multiplier = .02
		buy_multiplier = .02
	return sell_multiplier, buy_multiplier

def basic_strategy():
	last_trades = L()
	nav = 0

	sharesSold, sharesPurchased, revenue, cost = update_history()

	while nav < 25000000:
		numShares = sharesPurchased - sharesSold
		sold = False
		bought = False

		json = api.stock_quote(venue, target_stock)
		last_trades.append(json['last'])
		average = sum(last_trades) / len(last_trades)

		sell_multiplier, buy_multiplier = get_multipliers(numShares)

		json = api.stock_orderbook(venue, target_stock)
		priceNeeded = average + (sell_multiplier * average)
		if json['bids']:
			bestPrice = json['bids'][0]['price']
			qty = min(json['bids'][0]['qty'], 999 + numShares)
			print("Best bid: %s. Selling if > %.2f with multiplier %.3f" % (bestPrice, priceNeeded, sell_multiplier))
			if bestPrice > priceNeeded and int(qty) != 0:
				sell = api.stock_order(venue, my_account, target_stock, bestPrice, int(qty), 'sell', 'limit')
				sold = True
				print("   Selling %s at price: %s" % (int(qty), bestPrice))
		
		json = api.stock_orderbook(venue, target_stock)
		priceNeeded = average - (buy_multiplier * average)
		if json['asks']:
			bestPrice = json['asks'][0]['price']
			qty = min(json['asks'][0]['qty'], 999 - numShares)
			print("Best sell: %s. Buying if < %.2f with multiplier %.3f" % (bestPrice, priceNeeded, buy_multiplier))
			if bestPrice < priceNeeded and int(qty) != 0:
				buy = api.stock_order(venue, my_account, target_stock, bestPrice, int(qty), 'buy', 'limit')
				bought = True
				print("   Buying %s at price: %s" % (int(qty), bestPrice))

		time.sleep(1.5)

		if sold:
			json = api.stock_order_cancel(venue, target_stock, sell['id'])
			for fill in json['fills']:
				sharesSold += fill['qty']
				revenue += (fill['qty'] * fill['price'])
		if bought:
			json = api.stock_order_cancel(venue, target_stock, buy['id'])
			for fill in json['fills']:
				sharesPurchased += fill['qty']
				cost += (fill['qty'] * fill['price'])

		nav = (revenue - cost) + numShares * last_trades[-1]

		print("Position = ", numShares)
		print("Cash = $", (revenue - cost) / 100)
		print("Nav = $", nav / 100)
		print("---------------------------------------------")

	print("Exited with: $", nav / 100)

basic_strategy()