import datetime
from Stocks import Stock
import numpy as np
from FeaturesWrapper import FeaturesWrapper
from Tracer import Tracer
from simulator import Simulator
from simulator import RepeatPredictor
from simulator import PMAPredictor

class RatBoi(object):

	def __init__(self, stock):
		self.stock = stock
		self.featuresWrapper = FeaturesWrapper(self.stock)
		self.initializeTimeDenoms(120, 130)
		self.learningRate = 0.75	# just a default

	def initializeTimeDenoms(self, breakdown, limit):
		self.timeDenoms = []
		self.tracers = []
		for i in range(breakdown, limit, breakdown):
			self.timeDenoms.append(datetime.timedelta(minutes=i))
			self.tracers.append(Tracer(str(datetime.timedelta(minutes=i))))

	def initializeWeights(self):
		self.weights = np.zeros((len(self.timeDenoms), self.featuresWrapper.getVectorSize()))

	def train(self, startDate, endDate, iterations, learningRate):
		self.initializeWeights()
		self.learningRate = learningRate
		for iteration in range(iterations):
			self.run(startDate, endDate, testing=False)
			self.learningRate *= self.learningRate

	def test(self, startDate, endDate):
		self.run(startDate, endDate, testing=True)

	# this function should never be called directly, use train() or test() instead
	def run(self, startDate, endDate, testing=False):
		print ("running for {} from {} to {}".format(self.stock.ticker, startDate, endDate))
		currentTime = startDate
		while currentTime < endDate:
			print ("\r{}".format(currentTime), end="")
			# ensuring we have a value for the currentTime
			if (self.stock.getValue(currentTime) == None):
				currentTime += datetime.timedelta(minutes=1)
				continue

			# loading in the feature vector
			features = self.featuresWrapper.getFeatures(currentTime)
			# getting currentValue here to save time
			currentValue = self.stock.getValue(currentTime)

			# cycling through time denominations
			for i in range(len(self.timeDenoms)):
				nextTime = currentTime + self.timeDenoms[i]
				if (self.stock.getValue(nextTime) == None):
					continue
				predicted = np.dot(features, self.weights[i])
				# print (predicted)
				actual = self.stock.getValue(nextTime) - currentValue
				if (testing):					
					self.tracers[i].trace(predicted, actual, str(currentTime))
				else:
					# conditionals for incorrect predictions, and updating weights
					if (predicted <= 0 and actual > 0):
						self.weights[i] = np.add(self.weights[i], self.learningRate*features)
						# self.weights[i] = np.add(self.weights[i], features)
					elif (predicted >= 0 and actual < 0):
						self.weights[i] = np.subtract(self.weights[i], self.learningRate*features)
						# self.weights[i] = np.subtract(self.weights[i], features)

			currentTime += datetime.timedelta(minutes=1)

		if (testing):
			for i in range(len(self.timeDenoms)):
				self.tracers[i].print()

	def simulate(self, startDate, endDate, timeDenomIndex):
		simBoi = RepeatPredictor(5, self.stock, 1000, 30, startDate, self.timeDenoms[timeDenomIndex])
		# simBoi = PMAPredictor(self.stock, 1000, 30, startDate, self.timeDenoms[timeDenomIndex])
		print ("simulating for {} from {} to {}".format(self.stock.ticker, startDate, endDate))
		currentTime = startDate
		while currentTime < endDate:
			# ensuring we have a value for the currentTime
			if (self.stock.getValue(currentTime) == None):
				currentTime += datetime.timedelta(minutes=1)
				continue

			# loading in the feature vector
			features = self.featuresWrapper.getFeatures(currentTime)
			# getting currentValue here to save time
			currentValue = self.stock.getValue(currentTime)

			nextTime = currentTime + self.timeDenoms[timeDenomIndex]
			if (self.stock.getValue(nextTime) == None):
				continue

			predicted = np.dot(features, self.weights[timeDenomIndex])

			simBoi.processPrediction(predicted, currentTime)

			currentTime += datetime.timedelta(minutes=1)

		simBoi.sellAll(currentTime)
				