import time
import datetime
import statistics
from alpha_vantage.timeseries import TimeSeries
from StockManager import StockManager
from Stocks import Stock
from AllStocks import ALL_STOCKS

class testSuite(object):

	def loadValuesIntoOneStock(self):
		googleStock = Stock('GOOGL', 'googleValues.txt')
		googleStock.values = {
			"13:00:00" : (10.5, 20.10),
			"13:15:00" : (20.3, -15.4),
			"13:30:00" : (5, 14.2)
		}

		googleStock.previousValues = {
			"2019-03-18" : { "06:00:00" : (0.5, 45.10) },
			"2019-03-19" : { "06:15:00" : (83, 12) },
			"2019-03-20" : { "06:30:00" : (14, -6.0) },
		}
		return googleStock

	def testPopulationMean(self):
		googleStock = self.loadValuesIntoOneStock()
		valueList = googleStock.collectRecordedValues(0)
		volumeList = googleStock.collectRecordedValues(1)
		googleStock.updateMean(0, valueList)
		googleStock.updateMean(1, volumeList)
		assert(22.21666666666667 == googleStock.means[0]) #for values
		assert(11.666666666666668 == googleStock.means[1]) #for volumes

	def testStdDev(self):
		googleStock = self.loadValuesIntoOneStock()
		valueList = googleStock.collectRecordedValues(0)
		volumeList = googleStock.collectRecordedValues(1)
		googleStock.updateStdDev(0, valueList)
		googleStock.updateStdDev(1, volumeList)
		assert(27.90193641229145 == googleStock.stdDevs[0]) #for values
		assert(19.322496963096903 == googleStock.stdDevs[1]) #for volumes

	def testZScore(self):
		googleStock = self.loadValuesIntoOneStock()
		valueList = googleStock.collectRecordedValues(0)
		volumeList = googleStock.collectRecordedValues(1)
		#need to update the mean, deviations and set lastRecordedValue 
		#before calling updateZScore
		googleStock.updateMean(0, valueList)
		googleStock.updateMean(1, volumeList)
		googleStock.updateStdDev(0, valueList)
		googleStock.updateStdDev(1, volumeList)
		googleStock.updateZScore(0, valueList)
		googleStock.updateZScore(1, volumeList)
		googleStock.lastValueRecorded = (5, 14.2, "13:30:00")
		#need to fix this lastValueRecorded nonsense
		print(googleStock.zScores[0])
		print(googleStock.zScores[1])
		assert(27.90193641229145 == googleStock.stdDevs[0]) #for values
		assert(19.322496963096903 == googleStock.stdDevs[1]) #for volumes
	def testSkewness(self):
		pass
	def testKurtosis(self):
		pass

def main():
	suite = testSuite()
	suite.testPopulationMean()
	suite.testStdDev()
	suite.testZScore()

# runs the main() function
if __name__ == "__main__":
	main()
