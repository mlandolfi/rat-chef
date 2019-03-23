import time
import datetime
import statistics
from alpha_vantage.timeseries import TimeSeries
from StockManager import StockManager
from Stocks import Stock
from AllStocks import ALL_STOCKS

class testSuite(object):

	def loadValuesIntoOneStock(self):
		testStock = Stock('TEST', 'testValues.txt')
		testStock.values = {
			"13:00:00" : (10.5, 20.10),
			"13:15:00" : (20.3, -15.4),
			"13:30:00" : (5, 14.2)
		}

		testStock.previousValues = {
			"2019-03-18" : { "06:00:00" : (0.5, 45.10) },
			"2019-03-19" : { "06:15:00" : (83, 12) },
			"2019-03-20" : { "06:30:00" : (14, -6.0) },
		}
		return testStock

	def loadValuesForSkewnessAndKurtosis(self):
		testStock = Stock('TEST', 'testValues.txt')
		testStock.values = {
			"13:00:00" : (61, 20.10),
			"13:00:01" : (61, 20.10),
			"13:00:02" : (61, 20.10),
			"13:00:03" : (61, 20.10),
			"13:00:04" : (61, 20.10),
			"13:15:01" : (64, -15.4),
			"13:15:02" : (64, -15.4),
			"13:15:03" : (64, -15.4),
			"13:15:04" : (64, -15.4),
			"13:15:05" : (64, -15.4),
			"13:15:06" : (64, -15.4),
			"13:15:07" : (64, -15.4),
			"13:15:08" : (64, -15.4),
			"13:15:09" : (64, -15.4),
			"13:15:10" : (64, -15.4),
			"13:15:11" : (64, -15.4),
			"13:15:12" : (64, -15.4),
			"13:15:13" : (64, -15.4),
			"13:15:14" : (64, -15.4),
			"13:15:15" : (64, -15.4),
			"13:15:16" : (64, -15.4),
			"13:15:17" : (64, -15.4),
			"13:15:18" : (64, -15.4),
			"13:30:01" : (67, 14.2),
			"13:30:02" : (67, 14.2),
			"13:30:03" : (67, 14.2),
			"13:30:04" : (67, 14.2),
			"13:30:05" : (67, 14.2),
			"13:30:06" : (67, 14.2),
			"13:30:07" : (67, 14.2),
			"13:30:08" : (67, 14.2),
			"13:30:09" : (67, 14.2),
			"13:30:10" : (67, 14.2),
			"13:30:11" : (67, 14.2),
			"13:30:12" : (67, 14.2),
			"13:30:13" : (67, 14.2),
			"13:30:14" : (67, 14.2),
			"13:30:15" : (67, 14.2),
			"13:30:16" : (67, 14.2),
			"13:30:17" : (67, 14.2),
			"13:30:18" : (67, 14.2),
			"13:30:19" : (67, 14.2),
			"13:30:20" : (67, 14.2),
			"13:30:21" : (67, 14.2),
			"13:30:22" : (67, 14.2),
			"13:30:23" : (67, 14.2),
			"13:30:24" : (67, 14.2),
			"13:30:25" : (67, 14.2),
			"13:30:26" : (67, 14.2),
			"13:30:27" : (67, 14.2),
			"13:30:28" : (67, 14.2),
			"13:30:29" : (67, 14.2),
			"13:30:30" : (67, 14.2),
			"13:30:31" : (67, 14.2),
			"13:30:32" : (67, 14.2),
			"13:30:33" : (67, 14.2),
			"13:30:34" : (67, 14.2),
			"13:30:35" : (67, 14.2),
			"13:30:36" : (67, 14.2),
			"13:30:37" : (67, 14.2),
			"13:30:38" : (67, 14.2),
			"13:30:39" : (67, 14.2),
			"13:30:40" : (67, 14.2),
			"13:30:41" : (67, 14.2),
			"13:30:42" : (67, 14.2),
			"13:45:01" : (70, 45.10),
			"13:45:02" : (70, 45.10),
			"13:45:03" : (70, 45.10),
			"13:45:04" : (70, 45.10),
			"13:45:05" : (70, 45.10),
			"13:45:06" : (70, 45.10),
			"13:45:07" : (70, 45.10),
			"13:45:08" : (70, 45.10),
			"13:45:09" : (70, 45.10),
			"13:45:10" : (70, 45.10),
			"13:45:11" : (70, 45.10),
			"13:45:12" : (70, 45.10),
			"13:45:13" : (70, 45.10),
			"13:45:14" : (70, 45.10),
			"13:45:15" : (70, 45.10),
			"13:45:16" : (70, 45.10),
			"13:45:17" : (70, 45.10),
			"13:45:18" : (70, 45.10),
			"13:45:19" : (70, 45.10),
			"13:45:20" : (70, 45.10),
			"13:45:21" : (70, 45.10),
			"13:45:22" : (70, 45.10),
			"13:45:23" : (70, 45.10),
			"13:45:24" : (70, 45.10),
			"13:45:25" : (70, 45.10),
			"13:45:26" : (70, 45.10),
			"13:45:27" : (70, 45.10),

		}

		testStock.previousValues = {
			"2019-03-19" : { "06:15:01" : (73, 12) },
			"2019-03-20" : { "06:15:02" : (73, 12) },
			"2019-03-21" : { "06:15:03" : (73, 12) },
			"2019-03-22" : { "06:15:04" : (73, 12) },
			"2019-03-23" : { "06:15:05" : (73, 12) },
			"2019-03-24" : { "06:15:06" : (73, 12) },
			"2019-03-25" : { "06:15:07" : (73, 12) },
			"2019-03-26" : { "06:15:08" : (73, 12) },
		}
		return testStock

	def testPopulationMean(self):
		testStock = self.loadValuesIntoOneStock()
		valueList = testStock.collectRecordedValues(0)
		volumeList = testStock.collectRecordedValues(1)
		testStock.updateMean(0, valueList)
		testStock.updateMean(1, volumeList)
		assert(22.21666666666667 == testStock.means[0]) #for values
		assert(11.666666666666668 == testStock.means[1]) #for volumes

	def testStdDev(self):
		testStock = self.loadValuesIntoOneStock()
		valueList = testStock.collectRecordedValues(0)
		volumeList = testStock.collectRecordedValues(1)
		testStock.updateStdDev(0, valueList)
		testStock.updateStdDev(1, volumeList)
		assert(27.90193641229145 == testStock.stdDevs[0]) #for values
		assert(19.322496963096903 == testStock.stdDevs[1]) #for volumes

	def testZScore(self):
		testStock = self.loadValuesIntoOneStock()
		valueList = testStock.collectRecordedValues(0)
		volumeList = testStock.collectRecordedValues(1)
		#need to update the mean, deviations and set lastRecordedValue 
		#before calling updateZScore
		testStock.updateMean(0, valueList)
		testStock.updateMean(1, volumeList)
		testStock.updateStdDev(0, valueList)
		testStock.updateStdDev(1, volumeList)
		testStock.lastValueRecorded = (5, 14.2, "13:30:00")
		testStock.updateZScore(0, valueList)
		testStock.updateZScore(1, volumeList)
		assert(-0.6170420006792907 == testStock.zScores[0]) #for values
		assert(0.13110796902551577 == testStock.zScores[1]) #for volumes

	def testSkewness(self):
		testStock = self.loadValuesForSkewnessAndKurtosis()
		valueList = testStock.collectRecordedValues(0)
		#need to update the mean, deviations and set lastRecordedValue 
		#before calling updateZScore
		testStock.updateMean(0, valueList)
		testStock.updateStdDev(0, valueList)
		testStock.updateSkewness(0)
		assert(testStock.skewness[0] == -0.10815437112299184)

	def testKurtosis(self):
		testStock = self.loadValuesForSkewnessAndKurtosis()
		valueList = testStock.collectRecordedValues(0)
		#need to update the mean, deviations and set lastRecordedValue 
		#before calling updateZScore
		testStock.updateMean(0, valueList)
		testStock.updateStdDev(0, valueList)
		testStock.updateKurtosis(0)
		assert(testStock.kurtosis[0] == 2.7417589685396195)

def main():
	suite = testSuite()
	suite.testPopulationMean()
	suite.testStdDev()
	suite.testZScore()
	suite.testSkewness()
	suite.testKurtosis()

# runs the main() function
if __name__ == "__main__":
	main()
