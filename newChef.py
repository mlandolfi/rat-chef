from newDataManager import DataManager, DataBoi

import datetime
from itertools import combinations
import random
import numpy as np
from numpy import exp as npexp, array as nparray, random as nprandom, dot as npdot
import math

# TRAINING_SETS = [
# 	[1, 1, 0, 1, 0, 0, 1],
# 	[0, 1, 0, 1, 0, 1, 0],
# 	[0, 1, 0, 1, 0, 0, 1],
# 	[1, 0, 0, 1, 0, 0, 1],
# 	[1, 1, 1, 1, 1, 0, 1],
# 	[1, 0, 0, 0, 0, 1, 1],
# 	[0, 0, 0, 0, 0, 1, 1],
# ]
# TRAINING_TRUE = [1, 1, 1, 0, 1, 0, 0]

TRAINING_SETS = []
TRAINING_TRUE = []
for i in range(300):
	TRAINING_SETS.append([])
	for j in range(7):
		TRAINING_SETS[i].append(random.randint(0, 1))
	TRAINING_TRUE.append(1 if TRAINING_SETS[i][1] == 1 and TRAINING_SETS[i][4] == 1 and TRAINING_SETS[i][5] == 1 else 0)

TESTING_SETS = []
TESTING_TRUE = []
for i in range(100000):
	TESTING_SETS.append([])
	for j in range(7):
		TESTING_SETS[i].append(random.randint(0, 1))
	TESTING_TRUE.append(1 if TESTING_SETS[i][1] == 1 and TESTING_SETS[i][4] == 1 and TESTING_SETS[i][5] == 1 else 0)

# trues = [0, 1, 0, 0, 1, 0, 0]
testSet = [0, 1, 1, 1, 1, 0, 0]
testTrue = 1

class WeightsLayer(object):

	def __init__(self, numInputs, numWeights):
		self.weights = 2 * nprandom.random((numInputs, numWeights)) - 1
		# print (self.weights)

class Chef(object):

	def __init__(self, dataBoi, midLayerSizes, trainingConstant, predictionDelta, predictionIncrement):
		super(Chef, self).__init__()
		self.dataBoi = dataBoi
		self.layers = []
		# midLayerSizes.insert(0, 7)
		midLayerSizes.insert(0, dataBoi.inputSize())
		midLayerSizes.append(1)	# for the final answer layer
		for index in range(1, len(midLayerSizes)):
			self.layers.append(WeightsLayer(midLayerSizes[index-1], midLayerSizes[index]))
		self.predictionDelta = predictionDelta
		self.predictionIncrement = predictionIncrement
		self.trainingConstant = trainingConstant

	def trainGeneral(self, trainingSets, trainingAnswers, iterations=1):
		print ("TRAINING")
		trainingConstant = self.trainingConstant
		for i in range(iterations):
			for j in range(len(trainingSets)):
				features = nparray([trainingSets[j]])
				outputs = self.think(features)

				# calculate the errors and deltas for the layers going backwards
				errors = [trainingAnswers[j] - outputs[len(outputs)-1]]
				deltas = []
				for index in range(len(self.layers)-1, -1, -1):
					deltas.insert(0, errors[0] * self.sigmoidDerivative(outputs[index]))
					if (index == 0):
						break
					errors.insert(0, deltas[0].dot(self.layers[index].weights.T))

			# calculate the adjustments for each layer 
				adjustments = [features.T.dot(deltas[0])]
				for index in range(1, len(deltas)):
					adjustments.append(outputs[index-1].T.dot(deltas[index]))

				# apply the adjustments to each weight layer
				for index in range(len(adjustments)):
					self.layers[index].weights += (adjustments[index] * trainingConstant)

			trainingConstant = trainingConstant**2

		# --------------- BS testing below --------------- #
		print("TESTING")

		numCorrect = 0
		numTotal = len(TESTING_SETS)
		for i in range(len(TESTING_SETS)):
			features = nparray([TESTING_SETS[i]])
			outputs = self.think(features)
			if (outputs[len(outputs)-1] > 0.5 and TESTING_TRUE[i] > 0.5):
				numCorrect += 1
			elif (outputs[len(outputs)-1] < 0.5 and TESTING_TRUE[i] < 0.5):
				numCorrect += 1
		print (numCorrect / numTotal)



		features = nparray([testSet])
		outputs = self.think(features)
		print (outputs[len(outputs)-1])

		for layer in self.layers:
			print (layer.weights)


	def train(self, startDate, endDate, iterations=1):

		trainingConstant = self.trainingConstant

		for i in range(iterations):
			print ("\nITERATION: "+str(i))
			currentTime = startDate
			while currentTime < endDate:
				# print ("\r"+str(currentTime)+" - "+str(endDate), end="")
				# first ensure we have the current and future value
				currentValue = self.dataBoi.getDataValue(currentTime)
				futureValue = self.dataBoi.getDataValue(currentTime + self.predictionDelta)
				if (not currentValue or not futureValue):
					currentTime = currentTime + datetime.timedelta(minutes=1)
					continue

				# calculate the features to use
				features = self.dataBoi.calcFeatures(currentTime)

				# calculate for layer outputs
				outputs = self.think(features)

				# 1 if it went up otherwise 0
				actualDelta = 1 if futureValue - currentValue > 0 else 0
				# print (actualDelta)

				# calculate the errors and deltas for the layers going backwards
				errors = [actualDelta - outputs[len(outputs)-1]]
				deltas = []
				for index in range(len(self.layers)-1, -1, -1):
					deltas.insert(0, errors[0] * self.sigmoidDerivative(outputs[index]))
					if (index == 0):
						break
					errors.insert(0, deltas[0].dot(self.layers[index].weights.T))
				
				# calculate the adjustments for each layer
				# print ("---------------")
				# print (features)
				# print (deltas[0]) 
				adjustments = [features.T.dot(deltas[0])]
				for index in range(1, len(deltas)):
					adjustments.append(outputs[index-1].T.dot(deltas[index]))

				# apply the adjustments to each weight layer
				for index in range(len(adjustments)):
					self.layers[index].weights += (adjustments[index] * trainingConstant)

				currentTime = currentTime + self.predictionIncrement

			trainingConstant = trainingConstant * trainingConstant

		# output
		for layer in self.layers:
			print (layer.weights)


	def test(self, startDate, endDate):
		currentTime = startDate
		numPredictions = 0
		numCorrectPredictions = 0

		print ()
		while currentTime < endDate:
			# first ensure we have the current and future value
			currentValue = self.dataBoi.getDataValue(currentTime)
			futureValue = self.dataBoi.getDataValue(currentTime + self.predictionDelta)
			if (not currentValue or not futureValue):
				currentTime = currentTime + datetime.timedelta(minutes=1)
				continue

			numPredictions += 1

			# calculate the features to use
			features = self.dataBoi.calcFeatures(currentTime)

			# calculate for layer outputs
			outputs = self.think(features)
			# print (outputs[len(outputs)-1])

			# 1 if went up otherwise 0
			actualDelta = 1 if futureValue - currentValue > 0 else 0

			if (round(outputs[len(outputs)-1][0][0]) == actualDelta):
				numCorrectPredictions += 1
				print (outputs[len(outputs)-1], actualDelta)
			else:
				print ("WRONG: ", outputs[len(outputs)-1], actualDelta)

			print ("\r%.2f"%(100*(numCorrectPredictions/numPredictions)), end="")
			currentTime = currentTime + self.predictionIncrement
		print ()


	def think(self, features):
		outputs = []
		# add the first layer
		outputs.append(self.sigmoid(npdot(features, self.layers[0].weights)))
		for index in range(1, len(self.layers)):
			# calculate all successive output layers
			outputs.append(self.sigmoid(npdot(outputs[len(outputs)-1], self.layers[index].weights)))
		return outputs

	# used to normalize the outputs
	def sigmoid(self, x):
		return (1 / (1 + npexp(-x)))

	# used to adjust weights if wrong
	def sigmoidDerivative(self, x):
		return x * (1 - x)


def main():
	hourIncrements = [1, 2, 4, 6]
	dataBoi = DataManager('BTC-USD', hourIncrements)
	newDataBoi = DataBoi('BTC-USD', hourIncrements)


	# chef = Chef(dataBoi, [5, 5], .99, datetime.timedelta(hours=2), datetime.timedelta(hours=2))
	# chef.trainGeneral(TRAINING_SETS, TRAINING_TRUE, 1000)
	# return
	## chef = Chef(dataBoi, nodesInHiddenLayer, trainingConstant, predictionDelta, predictionIncrement)
	# chef = Chef(newDataBoi, [5, 5], 0.95, datetime.timedelta(hours=1), datetime.timedelta(hours=1))
	chef = Chef(dataBoi, [5,5], 0.95, datetime.timedelta(hours=2), datetime.timedelta(hours=2))

	trainStartDate = datetime.datetime(2018, 2, 4, 8)
	trainEndDate = trainStartDate + datetime.timedelta(weeks=10)
	print ("TRAINING")
	chef.train(trainStartDate, trainEndDate, 5)

	testStartDate = datetime.datetime(2018, 1, 1, 8)
	# testStartDate = trainEndDate
	testEndDate = testStartDate + datetime.timedelta(weeks=16)
	print ("TESTING")
	chef.test(testStartDate, testEndDate)



if __name__ == "__main__":
	main()






# class Chef(object):

# 	def __init__(self, dataBoi, midLayerSize, trainingConstant, predictionDelta, predictionIncrement):
# 		super(Chef, self).__init__()
# 		self.dataBoi = dataBoi
# 		self.firstLayer = WeightsLayer(dataBoi.inputSize(), midLayerSize)
# 		self.secondLayer = WeightsLayer(midLayerSize, 1)
# 		self.predictionDelta = predictionDelta
# 		self.predictionIncrement = predictionIncrement
# 		self.trainingConstant = trainingConstant

# 	def train(self, startDate, endDate, iterations=1):

# 		print (self.firstLayer.weights)
# 		print (self.secondLayer.weights)
# 		print ()
# 		trainingConstant = self.trainingConstant

# 		for i in range(iterations):
# 			print ("\nITERATION: "+str(i))
# 			currentTime = startDate
# 			while currentTime < endDate:
# 				print ("\r"+str(currentTime)+" - "+str(endDate), end="")
# 				# first ensure we have the current and future value
# 				currentValue = self.dataBoi.getDataValue(currentTime)
# 				futureValue = self.dataBoi.getDataValue(currentTime + self.predictionDelta)
# 				if (not currentValue or not futureValue):
# 					currentTime = currentTime + datetime.timedelta(minutes=1)
# 					continue

# 				# calculate the features to use
# 				features = self.dataBoi.calcFeatures(currentTime)

# 				# calculate for layer outputs
# 				firstLayerOutput, secondLayerOutput = self.think(features)
# 				# print ("\n"+str(secondLayerOutput[0]))

# 				# 1 if it went up otherwise 0
# 				actualDelta = 1 if futureValue - currentValue > 0 else 0
# 				# print (actualDelta)
				
# 				# calculate the error for the second layer
# 				secondLayerError = actualDelta - secondLayerOutput[0]
# 				secondLayerDelta = secondLayerError * self.sigmoidDerivative(secondLayerOutput)

# 				# calculate the error for the first layer
# 				firstLayerError = secondLayerDelta.dot(self.secondLayer.weights.T)
# 				firstLayerDelta = firstLayerError * self.sigmoidDerivative(firstLayerOutput)

# 				# calculate the adjustments for the weights
# 				firstLayerAdjustment = features.T.dot(firstLayerDelta)
# 				secondLayerAdjustment = firstLayerOutput.T.dot(secondLayerDelta)

# 				# Adjust the weights.
# 				self.firstLayer.weights += firstLayerAdjustment * trainingConstant
# 				self.secondLayer.weights += secondLayerAdjustment * trainingConstant

# 				currentTime = currentTime + self.predictionIncrement

# 			trainingConstant = trainingConstant * trainingConstant

# 		print ()
# 		print (self.firstLayer.weights)
# 		print (self.secondLayer.weights)

# 	def test(self, startDate, endDate):
# 		currentTime = startDate
# 		numPredictions = 0
# 		numCorrectPredictions = 0

# 		print ()
# 		while currentTime < endDate:
# 			# first ensure we have the current and future value
# 			currentValue = self.dataBoi.getDataValue(currentTime)
# 			futureValue = self.dataBoi.getDataValue(currentTime + self.predictionDelta)
# 			if (not currentValue or not futureValue):
# 				currentTime = currentTime + datetime.timedelta(minutes=1)
# 				continue

# 			numPredictions += 1

# 			# calculate the features to use
# 			features = self.dataBoi.calcFeatures(currentTime)

# 			# calculate for layer outputs
# 			firstLayerOutput, secondLayerOutput = self.think(features)

# 			# 1 if went up otherwise 0
# 			actualDelta = 1 if futureValue - currentValue > 0 else 0
# 			# print (secondLayerOutput[0])

# 			if (round(secondLayerOutput[0][0]) == actualDelta):
# 				numCorrectPredictions += 1

# 			print ("\r%.2f"%(100*(numCorrectPredictions/numPredictions)), end="")
# 			currentTime = currentTime + self.predictionIncrement
# 		print ()


# 	def think(self, features):
# 		firstLayerOutput = self.sigmoid(npdot(features, self.firstLayer.weights))
# 		secondLayerOutput = self.sigmoid(npdot(firstLayerOutput, self.secondLayer.weights))
# 		return firstLayerOutput, secondLayerOutput


# 	# used to normalize the outputs
# 	def sigmoid(self, x):
# 		return (1 / (1 + npexp(-x)))

# 	# used to adjust weights if wrong
# 	def sigmoidDerivative(self, x):
# 		return x * (1 - x)