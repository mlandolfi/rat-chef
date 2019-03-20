import statistics
from AllStocks import ALL_STOCKS

class StockManager(object):

	def __init__(self):
		self.allStocks = ALL_STOCKS

	"""Returns a list of the most volatile stock"""
	def mostVolatileStocks(self):
		retList = [] #may change to a set
		highestVolatility = 0
		for stock in self.allStocks:
			if stock.volatility > highestVolatility: 
				highestVolatility = stock.volatility
				retList.clear()
				retList.append(stock)
			elif stock.volatility == highestVolatility:
				retList.append(stock)
		return retList

	"""Given a volatility level from 0-10, 
	returns a list of stocks with given volatility level """
	def pullStocksWithGivenVolatility(self, volatility):
		retList = [] #may change to a set
		for stock in self.allStocks:
			stock.updateVolatility() #for real time
			if stock.volatility == volatility:
				retList.append(stock)
		return retList

	"""Compare a given stocks volatility to its volatility on previous days
	returns true if more volatile than previous days, false otherwise"""
	def compareVolatilityToPreviousDays(self, stock):
		stock.updateVolatility()
		pass

	"""Return a list of stocks higher/lower than the given zScore threshold
		index 0 = value, index 1 = volume, higher = true means above zScoreThreshold, false otherwise"""
	def pullStocksByZScoreThreshold(self, index, zScoreThreshold, higher):
		retList = []
		currentList = []
		for stock, stockObj in self.allStocks.items():
			currentList = stockObj.collectRecordedValues()
			#need to update populationMean and stdDev before calculating z-score
			stockObj.updatePopulationMean(index, currentList)
			stockObj.updateStdDev(index, currentList)
			stockObj.updateZScore(index, currentList)
			#if we are looking for a z-score above our treshold
			if higher is True:
				if stockObj.zScores[index] >= zScoreThreshold:
					retList.append(stockObj)
			#z-score below our threshold
			else:
				if stockObj.zScores[index] <= zScoreThreshold:
					retList.append(stockObj)
	
		return retList

	def __str__(self):
		retString = ""
		for name, obj in self.allStocks.items():
			retString += "name: " + name +  " obj: " + str(obj) + "\n"
		return retString