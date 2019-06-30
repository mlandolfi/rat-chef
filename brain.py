import json
import datetime
import statistics
from fractions import Fraction
from Stocks import Stock
import numpy

#TODO: Need to update populations because mike fucked itup
class brain(object):

	def __init__(self, stockList, miraConst, noise):
		self.stockList = stockList #
		self.featureVectors = {} #key is ticker, value is list of obtainIndividualFeatureVector
		self.weights = {} #key is ticker, value is list of obtainIndividualFeatureVector
		self.miraConst = miraConst
		self.noise = noise

		#Each feature vector will include
			#sample calculations for various times, and population calculations

	def setAllFeatureVectors(self, fromWhen, stock=None):
		if (stock != None):
			self.featureVectors[stock.ticker] = self.obtainIndividualFeatureVector(stock, fromWhen)
			return
		for stock in self.stockList:
			if not stock.ticker in self.featureVectors.keys():
				self.featureVectors[stock.ticker] = self.obtainIndividualFeatureVector(stock, fromWhen)
				# print(self.featureVectors[stock.ticker])

	def initializeWeights(self):
		self.weights = {} # list of lists
		for ticker in self.featureVectors.keys():
			self.weights[ticker] = [0] * len(self.featureVectors[ticker])

	def normalizeFeatures(self, features):
		denom = max(features)
		retFeatures = []
		for i in range(len(features)):
			retFeatures.append(features[i] / denom)
		return retFeatures

	def adjustWeights(self, weights, features, scalar):
		adjustedWeights = []
		for i in range(len(weights)):
			if (features[i] < 0):
				multiplier = max(features[i], -1*self.miraConst)
			else:
				multiplier = min(features[i], self.miraConst)
			adjustedWeights.append(weights[i] + scalar*(multiplier))
		return numpy.array(adjustedWeights)
			

	def train(self, startDate, endDate, stock):
		print ("training for {} from {} to {}".format(stock.ticker, startDate, endDate))
		currentTime = startDate
		weights = self.weights[stock.ticker]
		correctGuesses = 0
		guesses = 0
		while currentTime < endDate:
			nextTime = currentTime + datetime.timedelta(minutes=1)
			# continue if no values for current time or next time
			if (stock.getValue(currentTime) == None or stock.getValue(nextTime+datetime.timedelta(minutes=4)) == None):
				currentTime += datetime.timedelta(minutes=1)
				continue
			self.setAllFeatureVectors(currentTime, stock)
			
			predicted = numpy.dot(self.featureVectors[stock.ticker], weights)
			print ('\npredicted: ', predicted)
			guesses += 1
			# output<-0.5 sell; -0.5<output<0.5 hold; output>0.5 buy

			actual = stock.getValue(nextTime+datetime.timedelta(minutes=4)) - stock.getValue(currentTime)

			# print ("current price: {}".format(stock.getValue(currentTime)))
			# print ("predict: {}".format("rise" if predicted > 0 else "fall"))
			# print ("price in 1 hour: {}".format(stock.getValue(nextTime+datetime.timedelta(minutes=59))))

			weightsNumpy = numpy.array(weights)
			featuresNumpy = numpy.array(self.featureVectors[stock.ticker])
			# print ("before: ", weights)
			# print ("adjustment: ", featuresNumpy)

			# conditionals for incorrect predictions
			if (predicted <= 0 and actual > 0):
				# weights = numpy.add(weights, self.featureVectors[stock.ticker])
				weights = self.adjustWeights(weightsNumpy, featuresNumpy, 1)
			elif (predicted >= 0 and actual < 0):
				# weights = numpy.subtract(weights, self.featureVectors[stock.ticker])
				weights = self.adjustWeights(weightsNumpy, featuresNumpy, -1)
			else:
				correctGuesses += 1		
			# print ("\nweights\n: ", weights)

			print ("\r{} percent so far".format(round(100*(correctGuesses/guesses))), end="")

			if (guesses >= 1440):
				print ("\r{} percent correct over day".format(round(100*(correctGuesses/guesses))))
				guesses = 0
				correctGuesses = 0

			# increment to the next minute
			currentTime = nextTime

		# resetting the weights vector
		self.weights[stock.ticker] = weights
		# print ("\n{} percent correct".format(correctGuesses/guesses))
		print (weights)

	def test(self, startDate, endDate, stock):
		print ("testing for {} from {} to {}".format(stock.ticker, startDate, endDate))
		currentTime = startDate
		weights = self.weights[stock.ticker]
		correctGuesses = 0
		guesses = 0
		noiseGuesses = 0
		correctNoiseGuesses = 0
		while currentTime < endDate:
			nextTime = currentTime + datetime.timedelta(minutes=1)
			# continue if no values for current time or next time
			if (stock.getValue(currentTime) == None or stock.getValue(nextTime+datetime.timedelta(minutes=4)) == None):
				currentTime += datetime.timedelta(minutes=1)
				continue
			self.setAllFeatureVectors(currentTime, stock)

			predicted = numpy.dot(self.featureVectors[stock.ticker], weights)
			# print (predicted)

			if (predicted > self.noise or predicted < -1*self.noise):
				noiseGuesses += 1

			guesses += 1
			# output<-0.5 sell; -0.5<output<0.5 hold; output>0.5 buy

			actual = stock.getValue(nextTime+datetime.timedelta(minutes=4)) - stock.getValue(currentTime)

			if ((predicted > self.noise and actual > 0) or predicted < -1*self.noise and actual < 0):
				correctNoiseGuesses += 1

			if ((predicted < 0 and actual < 0) or
				(predicted > 0 and actual > 0)):
				correctGuesses += 1
				# print("Predicted correct")
			else:
				pass
				# print("Predicted wrong")

			print ("\r{} percent so far".format(round(100*(correctGuesses/guesses))), end="")

			currentTime = nextTime

		print ("\n{} percent correct out of {}".format(correctGuesses/guesses, guesses))
		print ("{} noise percent correct out of {}".format(correctNoiseGuesses/noiseGuesses, noiseGuesses))

	def obtainIndividualFeatureVector(self, stock, fromWhen):
		"""[#5x(5 min) for value then volume, 5x(10 min) for value then volume, 5x(15 min), 5x(20 min), 5x(30 min), 5x(45 min), 5x(1hr)
		5x(2hr), 5x(7hr), 5x(from currentTime back to 12:00am), 5x (all of previous day),
		5x(past week), 5x(2 weeks), population stuff here] """
		featureVector = []

		today = datetime.datetime.today()
		today = datetime.datetime(2018, today.month, today.day, today.hour, today.minute, 0, 0)
		today = fromWhen
		# print(today)
		start = today = datetime.datetime(2018, 1, today.day, today.hour, today.minute, 0, 0)

		fiveMinValue = stock.getAllSampleValues(0, today, 5, 0, 0, 1)
		fiveMinVolume = stock.getAllSampleValues(1, today, 5, 0, 0, 1)
		# featureVector += fiveMinValue #[] 
		# featureVector += fiveMinVolume

		tenMinValue = stock.getAllSampleValues(0, today, 10, 0, 0, 1)
		tenMinVolume = stock.getAllSampleValues(1, today, 10, 0, 0, 1)
		# featureVector += tenMinValue
		# featureVector += tenMinVolume

		ftnMinValue = stock.getAllSampleValues(0, today, 15, 0, 0, 1)
		ftnMinVolume = stock.getAllSampleValues(1, today, 15, 0, 0, 1)
		# featureVector += ftnMinValue
		# featureVector += ftnMinVolume

		twtyMinValue = stock.getAllSampleValues(0, today, 20, 0, 0, 1)
		twtyMinVolume = stock.getAllSampleValues(1, today, 20, 0, 0, 1)
		# featureVector += twtyMinValue
		# featureVector += twtyMinVolume

		thrtyMinValue = stock.getAllSampleValues(0, today, 30, 0, 0, 1)
		thrtyMinVolume = stock.getAllSampleValues(1, today, 30, 0, 0, 1)
		# featureVector += thrtyMinValue
		# featureVector += thrtyMinVolume


		fourtyfiveMinValue = stock.getAllSampleValues(0, today, 45, 0, 0, 1)
		fourtyfiveMinVolume = stock.getAllSampleValues(1, today, 45, 0, 0, 1)
		# featureVector += fourtyfiveMinValue
		# featureVector += fourtyfiveMinVolume


		hrValue = stock.getAllSampleValues(0, today, 0, 1, 0, 1)
		hrVolume = stock.getAllSampleValues(1, today, 0, 1, 0, 1)
		# featureVector += hrValue
		# featureVector += hrVolume

		twoHrValue = stock.getAllSampleValues(0, today, 0, 2, 0, 1)
		twoHrVolume = stock.getAllSampleValues(1, today, 0, 2, 0, 1)
		# featureVector += twoHrValue
		# featureVector += twoHrVolume

		# return featureVector

		svnHrValue = stock.getAllSampleValues(0, today, 0, 7, 0, 1)
		svnHrVolume = stock.getAllSampleValues(1, today, 0, 7, 0, 1)
		# featureVector += svnHrValue
		# featurelVector += svnHrVolume


		tenMinValue = stock.getAllSampleValues(0, today, 10, 0, 0, 1)
		tenMinVolume = stock.getAllSampleValues(1, today, 10, 0, 0, 1)
		# featureVector += tenMinValue
		# featureVector += tenMinVolume

		ftnMinValue = stock.getAllSampleValues(0, today, 15, 0, 0, 1)
		ftnMinVolume = stock.getAllSampleValues(1, today, 15, 0, 0, 1)
		# featureVector += ftnMinValue
		# featureVector += ftnMinVolume

		twtyMinValue = stock.getAllSampleValues(0, today, 20, 0, 0, 1)
		twtyMinVolume = stock.getAllSampleValues(1, today, 20, 0, 0, 1)
		# featureVector += twtyMinValue
		# featureVector += twtyMinVolume

		thrtyMinValue = stock.getAllSampleValues(0, today, 30, 0, 0, 1)
		thrtyMinVolume = stock.getAllSampleValues(1, today, 30, 0, 0, 1)
		# featureVector += thrtyMinValue
		# featureVector += thrtyMinVolume


		fourtyfiveMinValue = stock.getAllSampleValues(0, today, 45, 0, 0, 1)
		fourtyfiveMinVolume = stock.getAllSampleValues(1, today, 45, 0, 0, 1)
		# featureVector += fourtyfiveMinValue
		# featureVector += fourtyfiveMinVolume


		hrValue = stock.getAllSampleValues(0, today, 0, 1, 0, 1)
		hrVolume = stock.getAllSampleValues(1, today, 0, 1, 0, 1)
		# featureVector += hrValue
		# featureVector += hrVolume

		twoHrValue = stock.getAllSampleValues(0, today, 0, 2, 0, 1)
		twoHrVolume = stock.getAllSampleValues(1, today, 0, 2, 0, 1)
		# featureVector += twoHrValue
		# featureVector += twoHrVolume

		# return featureVector

		svnHrValue = stock.getAllSampleValues(0, today, 0, 7, 0, 1)
		svnHrVolume = stock.getAllSampleValues(1, today, 0, 7, 0, 1)
		# featureVector += svnHrValue
		# featureVector += svnHrVolume

		# return featureVector

		#put from currentTime back to 12am, all of previous day here

		previousDayValue = stock.getAllSampleValues(0, today, 0, 0, 1, 1)
		previousDayVolume = stock.getAllSampleValues(1, today, 0, 0, 1, 1)
		# featureVector += previousDayValue
		# featureVector += previousDayVolume

		# return featureVector

		weekValue = stock.getAllSampleValues(0, today, 0, 0, 7, 1)
		weekVolume = stock.getAllSampleValues(1, today, 0, 0, 7, 1)
		# featureVector += weekValue
		# featureVector += weekVolume

		# return featureVector

		twoWeekValue = stock.getAllSampleValues(0, today, 0, 0, 14, 1)
		twoWeekVolume = stock.getAllSampleValues(1, today, 0, 0, 14, 1)
		# featureVector += twoWeekValue
		# featureVector += twoWeekVolume

		# return featureVector

		#put from currentTime back to 12am, all of previous day here

		# previousDayValue = stock.getAllSampleValues(0, today, 0, 0, 1, 1)
		# previousDayVolume = stock.getAllSampleValues(1, today, 0, 0, 1, 1)
		# featureVector += previousDayValue
		# featureVector += previousDayVolume

		# return featureVector

		# weekValue = stock.getAllSampleValues(0, today, 0, 0, 7, 1)
		# weekVolume = stock.getAllSampleValues(1, today, 0, 0, 7, 1)
		# featureVector += weekValue
		# featureVector += weekVolume

		# return featureVector

		# twoWeekValue = stock.getAllSampleValues(0, today, 0, 0, 14, 1)
		# twoWeekVolume = stock.getAllSampleValues(1, today, 0, 0, 14, 1)
		# featureVector += twoWeekValue
		# featureVector += twoWeekVolume

		# return featureVector

		# print("Slow boys")
		#populations
		# stock.updatePopMean(0)
		# stock.updatePopMean(1)
		# stock.updatePopStdDev(0)
		# stock.updatePopStdDev(1)
		# xVal = stock.obtainXForZScore(0, start, today, 1)
		# xVol = stock.obtainXForZScore(1, start, today, 1)
		# stock.updatePopZScore(0, xVal)
		# stock.updatePopZScore(1, xVol)
		# stock.updatePopSkewness(0)
		# stock.updatePopSkewness(1)
		# stock.updatePopKurtosis(0)
		# stock.updatePopKurtosis(1)

		# featureVector.append(stock.popMeans[0])
		# featureVector.append(stock.popMeans[1])
		# featureVector.append(stock.popStdDevs[0])
		# featureVector.append(stock.popStdDevs[1])
		# featureVector.append(stock.popZScores[0])
		# featureVector.append(stock.popZScores[1])
		# featureVector.append(stock.popSkewness[0])
		# featureVector.append(stock.popSkewness[1])
		# featureVector.append(stock.popKurtosis[0])
		# featureVector.append(stock.popKurtosis[1])

		# [mean, stdDev, zScore, skewness, kurtosis]

		# fiveMin features
		featureVector.append(1 if fiveMinValue[0] > hrValue[0] else -1)
		featureVector.append(1 if fiveMinValue[1] > hrValue[1] else 0)
		featureVector.append(1 if fiveMinValue[2] > hrValue[2] else 0)
		featureVector.append(1 if fiveMinValue[3] > hrValue[3] else 0)
		featureVector.append(1 if fiveMinValue[4] > hrValue[4] else 0)

		featureVector.append(1 if fiveMinVolume[0] > hrVolume[0] else 0)
		featureVector.append(1 if fiveMinVolume[1] > hrVolume[1] else 0)
		featureVector.append(1 if fiveMinVolume[2] > hrVolume[2] else 0)
		featureVector.append(1 if fiveMinVolume[3] > hrVolume[3] else 0)
		featureVector.append(1 if fiveMinVolume[4] > hrVolume[4] else 0)

		featureVector.append(1 if fiveMinValue[0] > thrtyMinValue[0] else 0)
		featureVector.append(1 if fiveMinValue[1] > thrtyMinValue[1] else 0)
		featureVector.append(1 if fiveMinValue[2] > thrtyMinValue[2] else 0)
		featureVector.append(1 if fiveMinValue[3] > thrtyMinValue[3] else 0)
		featureVector.append(1 if fiveMinValue[4] > thrtyMinValue[4] else 0)

		featureVector.append(1 if fiveMinVolume[0] > thrtyMinVolume[0] else 0)
		featureVector.append(1 if fiveMinVolume[1] > thrtyMinVolume[1] else 0)
		featureVector.append(1 if fiveMinVolume[2] > thrtyMinVolume[2] else 0)
		featureVector.append(1 if fiveMinVolume[3] > thrtyMinVolume[3] else 0)
		featureVector.append(1 if fiveMinVolume[4] > thrtyMinVolume[4] else 0)

		featureVector.append(1 if fiveMinValue[0] > twtyMinValue[0] else 0)
		featureVector.append(1 if fiveMinValue[1] > twtyMinValue[1] else 0)
		featureVector.append(1 if fiveMinValue[2] > twtyMinValue[2] else 0)
		featureVector.append(1 if fiveMinValue[3] > twtyMinValue[3] else 0)
		featureVector.append(1 if fiveMinValue[4] > twtyMinValue[4] else 0)

		featureVector.append(1 if fiveMinVolume[0] > twtyMinVolume[0] else 0)
		featureVector.append(1 if fiveMinVolume[1] > twtyMinVolume[1] else 0)
		featureVector.append(1 if fiveMinVolume[2] > twtyMinVolume[2] else 0)
		featureVector.append(1 if fiveMinVolume[3] > twtyMinVolume[3] else 0)
		featureVector.append(1 if fiveMinVolume[4] > twtyMinVolume[4] else 0)

		featureVector.append(1 if fiveMinValue[0] > ftnMinValue[0] else 0)
		featureVector.append(1 if fiveMinValue[1] > ftnMinValue[1] else 0)
		featureVector.append(1 if fiveMinValue[2] > ftnMinValue[2] else 0)
		featureVector.append(1 if fiveMinValue[3] > ftnMinValue[3] else 0)
		featureVector.append(1 if fiveMinValue[4] > ftnMinValue[4] else 0)

		featureVector.append(1 if fiveMinVolume[0] > ftnMinVolume[0] else 0)
		featureVector.append(1 if fiveMinVolume[1] > ftnMinVolume[1] else 0)
		featureVector.append(1 if fiveMinVolume[2] > ftnMinVolume[2] else 0)
		featureVector.append(1 if fiveMinVolume[3] > ftnMinVolume[3] else 0)
		featureVector.append(1 if fiveMinVolume[4] > ftnMinVolume[4] else 0)

		featureVector.append(1 if fiveMinValue[0] > tenMinValue[0] else 0)
		featureVector.append(1 if fiveMinValue[1] > tenMinValue[1] else 0)
		featureVector.append(1 if fiveMinValue[2] > tenMinValue[2] else 0)
		featureVector.append(1 if fiveMinValue[3] > tenMinValue[3] else 0)
		featureVector.append(1 if fiveMinValue[4] > tenMinValue[4] else 0)

		featureVector.append(1 if fiveMinVolume[0] > tenMinVolume[0] else 0)
		featureVector.append(1 if fiveMinVolume[1] > tenMinVolume[1] else 0)
		featureVector.append(1 if fiveMinVolume[2] > tenMinVolume[2] else 0)
		featureVector.append(1 if fiveMinVolume[3] > tenMinVolume[3] else 0)
		featureVector.append(1 if fiveMinVolume[4] > tenMinVolume[4] else 0)

		# tenMin features
		featureVector.append(1 if tenMinValue[0] > hrValue[0] else 0)
		featureVector.append(1 if tenMinValue[1] > hrValue[1] else 0)
		featureVector.append(1 if tenMinValue[2] > hrValue[2] else 0)
		featureVector.append(1 if tenMinValue[3] > hrValue[3] else 0)
		featureVector.append(1 if tenMinValue[4] > hrValue[4] else 0)

		featureVector.append(1 if tenMinVolume[0] > hrVolume[0] else 0)
		featureVector.append(1 if tenMinVolume[1] > hrVolume[1] else 0)
		featureVector.append(1 if tenMinVolume[2] > hrVolume[2] else 0)
		featureVector.append(1 if tenMinVolume[3] > hrVolume[3] else 0)
		featureVector.append(1 if tenMinVolume[4] > hrVolume[4] else 0)

		featureVector.append(1 if tenMinValue[0] > thrtyMinValue[0] else 0)
		featureVector.append(1 if tenMinValue[1] > thrtyMinValue[1] else 0)
		featureVector.append(1 if tenMinValue[2] > thrtyMinValue[2] else 0)
		featureVector.append(1 if tenMinValue[3] > thrtyMinValue[3] else 0)
		featureVector.append(1 if tenMinValue[4] > thrtyMinValue[4] else 0)

		featureVector.append(1 if tenMinVolume[0] > thrtyMinVolume[0] else 0)
		featureVector.append(1 if tenMinVolume[1] > thrtyMinVolume[1] else 0)
		featureVector.append(1 if tenMinVolume[2] > thrtyMinVolume[2] else 0)
		featureVector.append(1 if tenMinVolume[3] > thrtyMinVolume[3] else 0)
		featureVector.append(1 if tenMinVolume[4] > thrtyMinVolume[4] else 0)

		featureVector.append(1 if tenMinValue[0] > twtyMinValue[0] else 0)
		featureVector.append(1 if tenMinValue[1] > twtyMinValue[1] else 0)
		featureVector.append(1 if tenMinValue[2] > twtyMinValue[2] else 0)
		featureVector.append(1 if tenMinValue[3] > twtyMinValue[3] else 0)
		featureVector.append(1 if tenMinValue[4] > twtyMinValue[4] else 0)

		featureVector.append(1 if tenMinVolume[0] > twtyMinVolume[0] else 0)
		featureVector.append(1 if tenMinVolume[1] > twtyMinVolume[1] else 0)
		featureVector.append(1 if tenMinVolume[2] > twtyMinVolume[2] else 0)
		featureVector.append(1 if tenMinVolume[3] > twtyMinVolume[3] else 0)
		featureVector.append(1 if tenMinVolume[4] > twtyMinVolume[4] else 0)

		featureVector.append(1 if tenMinValue[0] > ftnMinValue[0] else 0)
		featureVector.append(1 if tenMinValue[1] > ftnMinValue[1] else 0)
		featureVector.append(1 if tenMinValue[2] > ftnMinValue[2] else 0)
		featureVector.append(1 if tenMinValue[3] > ftnMinValue[3] else 0)
		featureVector.append(1 if tenMinValue[4] > ftnMinValue[4] else 0)

		featureVector.append(1 if tenMinVolume[0] > ftnMinVolume[0] else 0)
		featureVector.append(1 if tenMinVolume[1] > ftnMinVolume[1] else 0)
		featureVector.append(1 if tenMinVolume[2] > ftnMinVolume[2] else 0)
		featureVector.append(1 if tenMinVolume[3] > ftnMinVolume[3] else 0)
		featureVector.append(1 if tenMinVolume[4] > ftnMinVolume[4] else 0)

		# ftnMin (15) features
		featureVector.append(1 if ftnMinValue[0] > hrValue[0] else 0)
		featureVector.append(1 if ftnMinValue[1] > hrValue[1] else 0)
		featureVector.append(1 if ftnMinValue[2] > hrValue[2] else 0)
		featureVector.append(1 if ftnMinValue[3] > hrValue[3] else 0)
		featureVector.append(1 if ftnMinValue[4] > hrValue[4] else 0)

		featureVector.append(1 if ftnMinVolume[0] > hrVolume[0] else 0)
		featureVector.append(1 if ftnMinVolume[1] > hrVolume[1] else 0)
		featureVector.append(1 if ftnMinVolume[2] > hrVolume[2] else 0)
		featureVector.append(1 if ftnMinVolume[3] > hrVolume[3] else 0)
		featureVector.append(1 if ftnMinVolume[4] > hrVolume[4] else 0)

		featureVector.append(1 if ftnMinValue[0] > thrtyMinValue[0] else 0)
		featureVector.append(1 if ftnMinValue[1] > thrtyMinValue[1] else 0)
		featureVector.append(1 if ftnMinValue[2] > thrtyMinValue[2] else 0)
		featureVector.append(1 if ftnMinValue[3] > thrtyMinValue[3] else 0)
		featureVector.append(1 if ftnMinValue[4] > thrtyMinValue[4] else 0)

		featureVector.append(1 if ftnMinVolume[0] > thrtyMinVolume[0] else 0)
		featureVector.append(1 if ftnMinVolume[1] > thrtyMinVolume[1] else 0)
		featureVector.append(1 if ftnMinVolume[2] > thrtyMinVolume[2] else 0)
		featureVector.append(1 if ftnMinVolume[3] > thrtyMinVolume[3] else 0)
		featureVector.append(1 if ftnMinVolume[4] > thrtyMinVolume[4] else 0)

		featureVector.append(1 if ftnMinValue[0] > twtyMinValue[0] else 0)
		featureVector.append(1 if ftnMinValue[1] > twtyMinValue[1] else 0)
		featureVector.append(1 if ftnMinValue[2] > twtyMinValue[2] else 0)
		featureVector.append(1 if ftnMinValue[3] > twtyMinValue[3] else 0)
		featureVector.append(1 if ftnMinValue[4] > twtyMinValue[4] else 0)

		featureVector.append(1 if ftnMinVolume[0] > twtyMinVolume[0] else 0)
		featureVector.append(1 if ftnMinVolume[1] > twtyMinVolume[1] else 0)
		featureVector.append(1 if ftnMinVolume[2] > twtyMinVolume[2] else 0)
		featureVector.append(1 if ftnMinVolume[3] > twtyMinVolume[3] else 0)
		featureVector.append(1 if ftnMinVolume[4] > twtyMinVolume[4] else 0)

		# twtyMin (20) features
		featureVector.append(1 if twtyMinValue[0] > hrValue[0] else 0)
		featureVector.append(1 if twtyMinValue[1] > hrValue[1] else 0)
		featureVector.append(1 if twtyMinValue[2] > hrValue[2] else 0)
		featureVector.append(1 if twtyMinValue[3] > hrValue[3] else 0)
		featureVector.append(1 if twtyMinValue[4] > hrValue[4] else 0)

		featureVector.append(1 if twtyMinVolume[0] > hrVolume[0] else 0)
		featureVector.append(1 if twtyMinVolume[1] > hrVolume[1] else 0)
		featureVector.append(1 if twtyMinVolume[2] > hrVolume[2] else 0)
		featureVector.append(1 if twtyMinVolume[3] > hrVolume[3] else 0)
		featureVector.append(1 if twtyMinVolume[4] > hrVolume[4] else 0)

		featureVector.append(1 if twtyMinValue[0] > thrtyMinValue[0] else 0)
		featureVector.append(1 if twtyMinValue[1] > thrtyMinValue[1] else 0)
		featureVector.append(1 if twtyMinValue[2] > thrtyMinValue[2] else 0)
		featureVector.append(1 if twtyMinValue[3] > thrtyMinValue[3] else 0)
		featureVector.append(1 if twtyMinValue[4] > thrtyMinValue[4] else 0)

		featureVector.append(1 if twtyMinVolume[0] > thrtyMinVolume[0] else 0)
		featureVector.append(1 if twtyMinVolume[1] > thrtyMinVolume[1] else 0)
		featureVector.append(1 if twtyMinVolume[2] > thrtyMinVolume[2] else 0)
		featureVector.append(1 if twtyMinVolume[3] > thrtyMinVolume[3] else 0)
		featureVector.append(1 if twtyMinVolume[4] > thrtyMinVolume[4] else 0)

		# thrty (30) features
		featureVector.append(1 if thrtyMinValue[0] > hrValue[0] else 0)
		featureVector.append(1 if thrtyMinValue[1] > hrValue[1] else 0)
		featureVector.append(1 if thrtyMinValue[2] > hrValue[2] else 0)
		featureVector.append(1 if thrtyMinValue[3] > hrValue[3] else 0)
		featureVector.append(1 if thrtyMinValue[4] > hrValue[4] else 0)

		featureVector.append(1 if thrtyMinVolume[0] > hrVolume[0] else 0)
		featureVector.append(1 if thrtyMinVolume[1] > hrVolume[1] else 0)
		featureVector.append(1 if thrtyMinVolume[2] > hrVolume[2] else 0)
		featureVector.append(1 if thrtyMinVolume[3] > hrVolume[3] else 0)
		featureVector.append(1 if thrtyMinVolume[4] > hrVolume[4] else 0)

		featureVector.append(1 if thrtyMinValue[0] > twoHrValue[0] else 0)
		featureVector.append(1 if thrtyMinValue[1] > twoHrValue[1] else 0)
		featureVector.append(1 if thrtyMinValue[2] > twoHrValue[2] else 0)
		featureVector.append(1 if thrtyMinValue[3] > twoHrValue[3] else 0)
		featureVector.append(1 if thrtyMinValue[4] > twoHrValue[4] else 0)

		featureVector.append(1 if thrtyMinVolume[0] > twoHrVolume[0] else 0)
		featureVector.append(1 if thrtyMinVolume[1] > twoHrVolume[1] else 0)
		featureVector.append(1 if thrtyMinVolume[2] > twoHrVolume[2] else 0)
		featureVector.append(1 if thrtyMinVolume[3] > twoHrVolume[3] else 0)
		featureVector.append(1 if thrtyMinVolume[4] > twoHrVolume[4] else 0)

		# print ("features:\n", featureVector)

		return featureVector

	def perceptron(self):
		pass