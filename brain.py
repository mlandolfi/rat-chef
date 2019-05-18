import json
import datetime
import statistics
from fractions import Fraction
from Stocks import Stock

#TODO: Need to update populations because mike fucked itup
class brain(object):

	def __init__(self):
		self.stockList = [] #
		bitcoin = Stock("BTC-USD")
		self.stockList.append(bitcoin)
		self.featureVectors = {} #key is ticker, value is list of obtainIndividualFeatureVector
		self.weights = {} #key is ticker, value is list of obtainIndividualFeatureVector
		

		#Each feature vector will include
			#sample calculations for various times, and population calculations

	def setAllFeatureVectors(self):
		for stock in self.stockList:
			if not stock.ticker in self.featureVectors.keys():
				self.featureVectors[stock.ticker] = self.obtainIndividualFeatureVector(stock)
				print(self.featureVectors[stock.ticker])



	def obtainIndividualFeatureVector(self, stock):
		"""[#5x(5 min) for value then volume, 5x(10 min) for value then volume, 5x(15 min), 5x(20 min), 5x(30 min), 5x(45 min), 5x(1hr)
		5x(2hr), 5x(7hr), 5x(from currentTime back to 12:00am), 5x (all of previous day),
		5x(past week), 5x(2 weeks), population stuff here] """
		featureVector = []

		today = datetime.datetime.today()
		today = datetime.datetime(2018, today.month, today.day, today.hour, today.minute, 0, 0)
		start = today = datetime.datetime(2018, 1, today.day, today.hour, today.minute, 0, 0)

		fiveMinValue = stock.getAllSampleValues(0, today, 5, 0, 0, 1)
		fiveMinVolume = stock.getAllSampleValues(1, today, 5, 0, 0, 1)
		featureVector += fiveMinValue #[] 
		featureVector += fiveMinVolume

		tenMinValue = stock.getAllSampleValues(0, today, 10, 0, 0, 1)
		tenMinVolume = stock.getAllSampleValues(1, today, 10, 0, 0, 1)
		featureVector += tenMinValue
		featureVector += tenMinVolume

		ftnMinValue = stock.getAllSampleValues(0, today, 15, 0, 0, 1)
		ftnMinVolume = stock.getAllSampleValues(1, today, 15, 0, 0, 1)
		featureVector += ftnMinValue
		featureVector += ftnMinVolume

		twtyMinValue = stock.getAllSampleValues(0, today, 20, 0, 0, 1)
		twtyMinVolume = stock.getAllSampleValues(1, today, 20, 0, 0, 1)
		featureVector += twtyMinValue
		featureVector += twtyMinVolume

		thrtyMinValue = stock.getAllSampleValues(0, today, 30, 0, 0, 1)
		thrtyMinVolume = stock.getAllSampleValues(1, today, 30, 0, 0, 1)
		featureVector += thrtyMinValue
		featureVector += thrtyMinVolume


		fourtyfiveMinValue = stock.getAllSampleValues(0, today, 45, 0, 0, 1)
		fourtyfiveMinVolume = stock.getAllSampleValues(1, today, 45, 0, 0, 1)
		featureVector += fourtyfiveMinValue
		featureVector += fourtyfiveMinVolume


		hrValue = stock.getAllSampleValues(0, today, 0, 1, 0, 1)
		hrVolume = stock.getAllSampleValues(1, today, 0, 1, 0, 1)
		featureVector += hrValue
		featureVector += hrVolume

		twoHrValue = stock.getAllSampleValues(0, today, 0, 2, 0, 1)
		twoHrVolume = stock.getAllSampleValues(1, today, 0, 2, 0, 1)
		featureVector += twoHrValue
		featureVector += twoHrVolume

		svnHrValue = stock.getAllSampleValues(0, today, 0, 7, 0, 1)
		svnHrVolume = stock.getAllSampleValues(1, today, 0, 7, 0, 1)
		featureVector += svnHrValue
		featureVector += svnHrVolume
		#put from currentTime back to 12am, all of previous day here

		previousDayValue = stock.getAllSampleValues(0, today, 0, 0, 1, 1)
		previousDayVolume = stock.getAllSampleValues(1, today, 0, 0, 1, 1)
		featureVector += previousDayValue
		featureVector += previousDayVolume

		weekValue = stock.getAllSampleValues(0, today, 0, 0, 7, 1)
		weekVolume = stock.getAllSampleValues(1, today, 0, 0, 7, 1)
		featureVector += weekValue
		featureVector += weekVolume

		twoWeekValue = stock.getAllSampleValues(0, today, 0, 0, 14, 1)
		twoWeekVolume = stock.getAllSampleValues(1, today, 0, 0, 14, 1)
		featureVector += twoWeekValue
		featureVector += twoWeekVolume

		print("Slow boys")
		#populations
		stock.updatePopMean(0)
		stock.updatePopMean(1)
		stock.updatePopStdDev(0)
		stock.updatePopStdDev(1)
		xVal= stock.obtainXForZScore(0, start, today, 1)
		xVol = stock.obtainXForZScore(1, start, today, 1)
		stock.updatePopZScore(0, xVal)
		stock.updatePopZScore(1, xVol)
		stock.updatePopSkewness(0)
		stock.updatePopSkewness(1)
		stock.updatePopKurtosis(0)
		stock.updatePopKurtosis(1)

		featureVector.append(stock.popMeans[0])
		featureVector.append(stock.popMeans[1])
		featureVector.append(stock.popStdDevs[0])
		featureVector.append(stock.popStdDevs[1])
		featureVector.append(stock.popZScores[0])
		featureVector.append(stock.popZScores[1])
		featureVector.append(stock.popSkewness[0])
		featureVector.append(stock.popSkewness[1])
		featureVector.append(stock.popKurtosis[0])
		featureVector.append(stock.popKurtosis[1])

		return featureVector

	def perceptron(self):
		pass