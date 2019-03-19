import statistics
from AllStocks import ALL_STOCKS

class StockManager(object):

	def __init__(self):
		

	"""Returns a list of the most volatile stock"""
	def mostVolatileStocks():
		retList = [] #may change to a set
		highestVolatility = 0
		for stock in self.allStocks:
			if stock.volatility > highestVolatility: 
				highestVolatility = stock.volatility
				retList.clear()
				retList.append(stock)
			elif stock.volatility = highestVolatility:
				retList.append(stock)
		return retList

	"""Given a volatility level from 0-10, 
	returns a list of stocks with given volatility level """
	def pullStocksWithGivenVolatility(volatility):
		retList = [] #may change to a set
		for stock in self.allStocks:
			stock.updateVolatility() #for real time
			if stock.volatility = volatility:
				retList.append(stock)
		return retList

	"""Compare a given stocks volatility to its volatility on previous days
	returns true if more volatile than previous days, false otherwise"""
	def compareVolatilityToPreviousDays(stock):
		stock.updateVolatility()
		pass

	"""Return a list of stocks with high volume
	has to be compared to its previous volumes because each stock is different
	high volume stocks just mean that it's traded a lot, which can be good or bad"""
	def pullStocksWithHighVolume():
		#take each stocks volume std deviation, compare how far it is from std dev

	