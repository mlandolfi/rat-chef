import time
import datetime
import statistics
from alpha_vantage.timeseries import TimeSeries
from StockManager import StockManager
from Stocks import Stock
from AllStocks import ALL_STOCKS

class testSuite(object):

	def testing(self):
		print('in testing')
		self.values.clear()
		for key in self.previousValues:
			key.clear()
		self.previousValues.clear()
		print('values' , self.values)
		for key in self.previousValues:
			print (self.previousValues[key])
		print('previousValues', self.previousValues)

	def loadValuesIntoOneStock(self):
		googleStock = Stock('GOOGL', 'googleValues.txt')
		googleStock.values = {
			0 : (10.5, 20.10),
			1 : (20.3, -15.4),
			2 : (5, 14.2)
		}

		googleStock.previousValues = {
			3 : { 6 : (0.5, 45.10) },
			4 : { 7 : (83, 12) },
			5 : { 8 : (14, -6.0) },
		}

		for time in googleStock.values:
			print (googleStock.values[time])
		for date in googleStock.previousValues:
			for time in date:
				print(googleStock.values[date][time])

	def testPopulationMean(self):
		pass
	def testStdDev(self):
		pass
	def testZScore(self):
		pass
	def testSkewness(self):
		pass
	def testKurtosis(self):
		pass

def main():
	suite = testSuite()
	suite.loadValuesIntoOneStock()

# runs the main() function
if __name__ == "__main__":
	main()
