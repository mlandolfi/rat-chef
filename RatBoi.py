import datetime
from Stocks import Stock
import numpy as np
from FeaturesWrapper import FeaturesWrapper

class RatBoi(object):

	def __init__(self, stock):
		self.stock = stock
		self.featuresWrapper = FeaturesWrapper(self.stock)
		self.initializeTimeDenoms(30, 600)
		self.learningRate = 0.01	# just a default
		# self.initializeConfidence()

	def initializeTimeDenoms(self, breakdown, limit):
		self.timeDenoms = []
		for i in range(breakdown, limit, breakdown):
			self.timeDenoms.append(datetime.timedelta(minutes=i))

	def initializeWeights(self):
		self.weights = np.zeros((len(self.timeDenoms), self.featuresWrapper.getVectorSize()))

	def initializeConfidence(self):
		# self.positivePredictions = []
		# self.negativePredictions = []
		# for i in range(len(self.timeDenoms)):
		# 	self.positivePredictions[i].append([])
		# 	self.negativePredictions[i].append([])
		self.positiveTracer = []
		self.negativeTracer = []
		for i in range(len(self.timeDenoms)):
			self.positiveTracer.append({ 'total': 0, 'num': 0, 'avg': 0 })
			self.negativeTracer.append({ 'total': 0, 'num': 0, 'avg': 0 })


	def traceConfidence(self, i, predicted):
		if (predicted > 0):
			self.positiveTracer[i]['total'] += predicted
			self.positiveTracer[i]['num'] += 1
			self.positiveTracer[i]['avg'] = self.positiveTracer[i]['total'] // self.positiveTracer[i]['num']
		else:
			self.negativeTracer[i]['total'] += predicted
			self.negativeTracer[i]['num'] += 1
			self.negativeTracer[i]['avg'] = self.negativeTracer[i]['total'] // self.negativeTracer[i]['num']

	def getConfidence(self, i, predicted):
		if (predicted > 0):
			return 1 if predicted > self.positiveTracer[i]['avg'] else 0
		else:
			return 1 if predicted < self.negativeTracer[i]['avg'] else 0

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
		correctGuesses = [0] * len(self.timeDenoms)
		guesses = [0] * len(self.timeDenoms)
		negPredicts = [0] * len(self.timeDenoms)
		correctNegPredicts = [0] * len(self.timeDenoms)
		posPredicts = [0] * len(self.timeDenoms)
		correctPosPredicts = [0] * len(self.timeDenoms)
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
					if (predicted > 0):	posPredicts[i] += 1
					else:	negPredicts[i] += 1

					if (predicted < 0 and actual < 0):
						correctGuesses[i] += 1
						correctNegPredicts[i] += 1
					elif (predicted > 0 and actual > 0):
						correctGuesses[i] += 1
						correctPosPredicts[i] += 1
					guesses[i] += 1
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
			print()
			for i in range(len(self.timeDenoms)):
				print ("{}\n{}/{} overall".format(self.timeDenoms[i], correctGuesses[i], guesses[i]))
				print ("{}/{} positive predictions".format(correctPosPredicts[i], posPredicts[i]))
				print ("{}/{} negative predictions".format(correctNegPredicts[i], negPredicts[i]))
				# print ("{}: {}/{} ==> {}".format(self.timeDenoms[i], correctGuesses[i], guesses[i],
				# 	correctGuesses[i]/guesses[i]))
				# print ("{}/{} positive predictions ==> {}".format(correctPosPredicts[i], posPredicts[i],
				# 	correctPosPredicts[i]/posPredicts[i]))
				# print ("{}/{} negative predictions ==> {}".format(correctNegPredicts[i], negPredicts[i],
				# 	correctNegPredicts[i]/negPredicts[i]))

