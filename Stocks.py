# file to hold stocks class to store stock data

class Stock(object):

	def __init__(self, symbol values={}):
		self.symbol = symbol
		self.volatility = 5	# 0-10
		self.values = []	# list of values for today
		self.previousValues = []	# list of values from past days
		# functions to execute on instantiation
		self.readValues()


	def saveValues():
		pass
		# writes values to file

	def readValues():
		pass
		# reads in previous and current day values

