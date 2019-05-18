import time
import datetime
import statistics
from alpha_vantage.timeseries import TimeSeries
from StockManager import StockManager
from Stocks import Stock
from AllStocks import ALL_STOCKS

#TODO: Need to test if population functions update when adding a stock

class testSuite(object):

	def loadValuesIntoOneStock(self):
		testStock = Stock('TEST', 'testValues.txt')

		testStock.record = {
			"2019-03-18" : { "06:00:00" : (0.5, 45.10),
							  "06:15:00" : (73, 12)  },
			"2019-03-19" : { "06:15:00" : (83, 12) },
			"2019-03-20" : { "06:30:00" : (14, -6.0),
							 "06:31:00" : (18, 9) }
		}
		return testStock

	def loadValsForSkewKurtosis(self):
		testStock = Stock('TEST', 'testValues.txt')
		#3 days, 32 mins span
		testStock.record = {
			"2019-03-18" : { "06:00:00" : (61, 0),
								"06:01:00" : (61, 0),
								"06:02:00" : (61, 0),
								"06:03:00" : (61, 0),
								"06:04:00" : (61, 0),
								"06:05:00" : (64, 0),
								"06:06:00" : (64, 0),
								"06:07:00" : (64, 0),
								"06:08:00" : (64, 0),
								"06:09:00" : (64, 0),
								"06:10:00" : (64, 0),
								"06:11:00" : (64, 0),
								"06:12:00" : (64, 0),
								"06:13:00" : (64, 0),
								"06:14:00" : (64, 0),
								"06:15:00" : (64, 0),
								"06:16:00" : (64, 0),
								"06:17:00" : (64, 0),
								"06:18:00" : (64, 0),
								"06:19:00" : (64, 0),
								"06:20:00" : (64, 0),
								"06:21:00" : (64, 0),
								"06:22:00" : (64, 0),
								"06:23:00" : (67, 0),
								"06:24:00" : (67, 0),
								"06:25:00" : (67, 0),
								"06:26:00" : (67, 0),
								"06:27:00" : (67, 0),
								"06:28:00" : (67, 0),
								"06:29:00" : (67, 0),
								"06:30:00" : (67, 0),
								"06:31:00" : (67, 0),
								"06:32:00" : (67, 0),
								"06:33:00" : (67, 0),
								"06:34:00" : (67, 0),
								"06:35:00" : (67, 0),
								"06:36:00" : (67, 0),
								"06:37:00" : (67, 0),
								"06:38:00" : (67, 0),
								"06:39:00" : (67, 0),
								"06:40:00" : (67, 0),
								"06:41:00" : (67, 0),
								"06:42:00" : (67, 0),
								"06:43:00" : (67, 0),
								"06:44:00" : (67, 0),
								"06:45:00" : (67, 0),
								"06:46:00" : (67, 0),
								"06:47:00" : (67, 0),
								"06:48:00" : (67, 0),
								"06:49:00" : (67, 0),
								"06:50:00" : (67, 0),
								"06:51:00" : (67, 0),
								"06:52:00" : (67, 0),
								"06:53:00" : (67, 0),
								"06:54:00" : (67, 0),
								"06:55:00" : (67, 0),
								"06:56:00" : (67, 0),
								"06:57:00" : (67, 0),
								"06:58:00" : (67, 0),
								"06:59:00" : (67, 0),
								
							  						},
			
			"2019-03-19" : { "06:15:00" : (73, 0), 
								"06:16:00" : (73, 0),
								"06:17:00" : (73, 0),
								"06:18:00" : (73, 0),
								"06:19:00" : (73, 0),
								"06:20:00" : (73, 0),
								"06:21:00" : (73, 0),
								"06:22:00" : (73, 0)
													},

			"2019-03-21" : {	"06:01:00" : (67, 0),
								"06:02:00" : (67, 0),
								"06:03:00" : (67, 0),
								"06:04:00" : (67, 0),
								"06:05:00" : (67, 0),
								"06:06:00" : (70, 0),
								"06:07:00" : (70, 0),
								"06:08:00" : (70, 0),
								"06:09:00" : (70, 0),
								"06:10:00" : (70, 0),
								"06:11:00" : (70, 0),
								"06:12:00" : (70, 0),
								"06:13:00" : (70, 0),
								"06:14:00" : (70, 0),
								"06:15:00" : (70, 0),
								"06:16:00" : (70, 0),
								"06:17:00" : (70, 0),
								"06:18:00" : (70, 0),
								"06:19:00" : (70, 0),
								"06:20:00" : (70, 0),
								"06:21:00" : (70, 0),
								"06:22:00" : (70, 0),
								"06:23:00" : (70, 0),
								"06:24:00" : (70, 0),
								"06:25:00" : (70, 0),
								"06:26:00" : (70, 0),
								"06:27:00" : (70, 0),
								"06:28:00" : (70, 0),
								"06:29:00" : (70, 0),
								"06:30:00" : (70, 0),
								"06:31:00" : (70, 0),
								"06:32:00" : (70, 0)

													}	
		}

		return testStock

	"""============================== Sample Tests =============================="""

	#This test confirms that calculateStartDate, getSampleList work properly
	def testSampleMean(self):
		testStock = self.loadValsForSkewKurtosis()

		#Time range is all of our data 
		endDate = datetime.datetime(2019, 3, 21, 6, 32, 0, 0) #2019-03-21 06:32:00
		startDate = testStock.calculateStartDate(endDate, 32, 0, 3) #should return 2018-03-18 6:00:00
		sampleList = testStock.getSampleList(0, startDate, endDate, 1)#here
		sampleMean = testStock.getSampleMean(sampleList)
		assert(sampleMean == 67.45)
		sampleMean = 0.0
	
		#Time range is from our latest data to beyond our first data point
		endDate = datetime.datetime(2019, 3, 21, 6, 32, 0, 0)
		startDate = testStock.calculateStartDate(endDate, 32, 0, 7) 
		sampleList = testStock.getSampleList(0, startDate, endDate, 1)
		sampleMean = testStock.getSampleMean(sampleList)
		assert(sampleMean == 67.45)
		sampleMean = 0.0

		#Time range is from beyond our latest data to our earliest data point
		endDate = datetime.datetime(2019, 3, 22, 6, 32, 0, 0)
		startDate = testStock.calculateStartDate(endDate, 32, 0, 4) 
		sampleList = testStock.getSampleList(0, startDate, endDate, 1)
		sampleMean = testStock.getSampleMean(sampleList)
		assert(sampleMean == 67.45)
		sampleMean = 0.0

		#Time range is beyond our latest data and beyond our earliest data
		endDate = datetime.datetime(2019, 3, 25, 6, 32, 0, 0)
		startDate = testStock.calculateStartDate(endDate, 32, 0, 20) 
		sampleList = testStock.getSampleList(0, startDate, endDate, 1)
		sampleMean = testStock.getSampleMean(sampleList)
		assert(sampleMean == 67.45)
	
	def testSampleStdDev(self):
		testStock = self.loadValuesIntoOneStock()

		#Time range is all of our data 
		endDate = datetime.datetime(2019, 3, 21, 6, 32, 0, 0) #2019-03-21 06:32:00
		startDate = testStock.calculateStartDate(endDate, 32, 0, 3) #should return 2018-03-18 6:00:00
		sampleList1 = testStock.getSampleList(0, startDate, endDate, 1)#here
		sampleList2 = testStock.getSampleList(1, startDate, endDate, 1)#here
		
		sampleStdDev1 = testStock.getSampleStdDev(sampleList1)
		sampleStdDev2 = testStock.getSampleStdDev(sampleList2)
		assert(sampleStdDev1 == 37.52265982043384)
		assert(sampleStdDev2 == 18.703796406077565)
	
	def testSampleZScore(self):
		testStock = self.loadValuesIntoOneStock()

		#Test 1:

		#Time range does not include march 20th
		endDate = datetime.datetime(2019, 3, 19, 6, 32, 0, 0) #2019-03-19 06:32:00
		startDate = testStock.calculateStartDate(endDate, 32, 0, 3) #should return 2018-03-18 6:00:00
		sampleList1 = testStock.getSampleList(0, startDate, endDate, 1)#here
		sampleList2 = testStock.getSampleList(1, startDate, endDate, 1)#here
		sampleMean1 = testStock.getSampleMean(sampleList1) 	#52.166666666667
		sampleMean2 = testStock.getSampleMean(sampleList2) #23.03333
		sampleStdDev1 = testStock.getSampleStdDev(sampleList1) #45.023142197467
		sampleStdDev2 = testStock.getSampleStdDev(sampleList2) #19.11

		sampleZScore1 = testStock.getSampleZScore(10, sampleList1, sampleMean1, sampleStdDev1)
		sampleZScore2 = testStock.getSampleZScore(10, sampleList2, sampleMean2, sampleStdDev2)
		assert(sampleZScore1 == -0.9365553937068161)
		assert(sampleZScore2 == -0.6820059071091955)

		#Test 2:
		
		testStock = self.loadValsForSkewKurtosis()

		#Time range includes all
		endDate = datetime.datetime(2019, 3, 21, 6, 32, 0, 0) #2019-03-21 06:32:00
		startDate = testStock.calculateStartDate(endDate, 32, 0, 3) #should return 2018-03-18 6:00:00
		sampleList1 = testStock.getSampleList(0, startDate, endDate, 1)#here
		sampleMean1 = testStock.getSampleMean(sampleList1) 	
		sampleStdDev1 = testStock.getSampleStdDev(sampleList1) 

		sampleZScore1 = testStock.getSampleZScore(10, sampleList1, sampleMean1, sampleStdDev1)
		assert(sampleZScore1 == -19.5747744353607)
	
	def testSampleSkewness(self):
		testStock = self.loadValsForSkewKurtosis()

		#Time range includes all
		endDate = datetime.datetime(2019, 3, 21, 6, 32, 0, 0) #2019-03-21 06:32:00
		startDate = testStock.calculateStartDate(endDate, 32, 0, 3) #should return 2018-03-18 6:00:00
		sampleList1 = testStock.getSampleList(0, startDate, endDate, 1)#here
		sampleMean1 = testStock.getSampleMean(sampleList1) 	
		sampleStdDev1 = testStock.getSampleStdDev(sampleList1)

		sampleSkewness = testStock.getSampleSkewness(sampleList1, sampleMean1, sampleStdDev1)
		assert(sampleSkewness == -0.10816540728331094)

	def testSampleKurtosis(self):
		testStock = self.loadValsForSkewKurtosis()

		#Time range includes all
		endDate = datetime.datetime(2019, 3, 21, 6, 32, 0, 0) #2019-03-21 06:32:00
		startDate = testStock.calculateStartDate(endDate, 32, 0, 3) #should return 2018-03-18 6:00:00
		sampleList1 = testStock.getSampleList(0, startDate, endDate, 1)#here
		sampleMean1 = testStock.getSampleMean(sampleList1) 	
		sampleStdDev1 = testStock.getSampleStdDev(sampleList1)

		sampleKurtosis = testStock.getSampleKurtosis(sampleList1, sampleMean1, sampleStdDev1)
		assert(sampleKurtosis == -0.2665377180000241)


	"""============================== Population Tests =============================="""


	def testPopulationMean(self):
		testStock = self.loadValuesIntoOneStock()

		testStock.updatePopMean(0)
		testStock.updatePopMean(1)
		assert(37.7 == testStock.popMeans[0]) #for values
		assert(14.42 == testStock.popMeans[1]) #for volumes

	def testPopStdDev(self):
		testStock = self.loadValuesIntoOneStock()

		testStock.updatePopStdDev(0)
		testStock.updatePopStdDev(1)
		assert(33.56128722203604 == testStock.popStdDevs[0]) #for values
		assert(16.729184080522277 == testStock.popStdDevs[1]) #for volumes
		
	def testPopZScore(self):
		testStock = self.loadValuesIntoOneStock()
		#need to update the mean, deviations and set lastRecordedValue 
		#before calling updatePopZScore
		testStock.updatePopMean(0)
		testStock.updatePopMean(1)
		testStock.updatePopStdDev(0)
		testStock.updatePopStdDev(1)
		testStock.lastValueRecorded = (5, 14.2, "13:30:00")

		testStock.updatePopZScore(0, 5)
		testStock.updatePopZScore(1, 14.2)
		assert(-0.9743368835546175 == testStock.popZScores[0]) #for values
		assert(-0.01315067124260685 == testStock.popZScores[1]) #for volumes
		
	def testPopSkewness(self):
		testStock = self.loadValsForSkewKurtosis()
		#need to update the mean, deviations and set lastRecordedValue 
		#before calling updatePopZScore
		testStock.updatePopMean(0)
		assert(testStock.popMeans[0] == 67.45)
		testStock.updatePopStdDev(0)

		testStock.updatePopSkewness(0)
		assert(testStock.popSkewness[0] == -0.10815437112299223)

	def testPopKurtosis(self):
		testStock = self.loadValsForSkewKurtosis()
		#need to update the mean, deviations and set lastRecordedValue 
		#before calling updatePopZScore
		testStock.updatePopMean(0)
		testStock.updatePopStdDev(0)

		testStock.updatePopKurtosis(0)
		assert(testStock.popKurtosis[0] ==  -0.25824103146037247)

def main():
	#Sample Tests
	suite = testSuite()

	suite.testSampleMean()
	suite.testSampleStdDev()
	suite.testSampleZScore()
	suite.testSampleSkewness()
	suite.testSampleKurtosis()

	#Population Tests
	suite.testPopulationMean()
	suite.testPopStdDev()
	suite.testPopZScore()
	suite.testPopSkewness()
	suite.testPopKurtosis()
	print("Tests successful")

# runs the main() function
if __name__ == "__main__":
	main()
