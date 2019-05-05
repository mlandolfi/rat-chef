import random
import statistics

class WeightTrainer(object):

	def __init__(self, evaluationFunctions, stock, iterations):
		self.weights = {}
		self.conclusions = []
		self.iterations = iterations
		self.evaluationFunctions = evaluationFunctions
		self.stock = stock
		self.randomizeWeights()

	def normalizeAttempt(self, num):
		factor = 1
		if (num > 100):	factor = 5
		if (num > 1000):	factor = 40
		if (num > 3000):	factor = 100
		if (num > 5000):	facor = 200
		return num / (num+factor)

	def randomizeWeights(self):
		for key, func in self.evaluationFunctions.items():
			self.weights[func["key"]] = []
			for i in range(self.iterations):
				self.weights[func["key"]].append(random.random() * random.choice([-1,1]))

	def predictConclusions(self):
		for i in range(self.iterations):
			conclusion = 0
			for key, func in self.evaluationFunctions.items():
				conclusion += self.normalizeAttempt(func["func"](self.stock)) * self.weights[func["key"]][i]
			self.conclusions.append(conclusion)

	def storeConclusions(self):
		with open('conclusions.txt', 'w') as outFile:
			outFile.write("Evaluations for stock: %s\n" % (self.stock))
			outFile.write("%d iterations\n" % self.iterations)
			# for i in range(self.iterations):
			# 	outFile.write("\nIteration #%s\n" % (i))
			# 	for func in self.weights:
			# 		outFile.write("%s: %s\n" % (func, self.weights[func][i]))
			# 	outFile.write("Conclusion: %s\n" % self.conclusions[i])

			outFile.write("\n###############################################\n")
			outFile.write("\nPOSITIVE CONCLUSIONS\n")
			for key, func in self.evaluationFunctions.items():
				outFile.write('{:<30}'.format(key))
				weights = self.getPositiveConclusionWeights(key)
				outFile.write('{:<16}'.format("Mean: %.3f" % statistics.mean(weights)))
				outFile.write('{:<16}'.format("Median: %.3f" % statistics.median(weights)))
				outFile.write("\n")

			outFile.write("\nNEGATIVE CONCLUSIONS:\n")
			for key, func in self.evaluationFunctions.items():
				outFile.write('{:<30}'.format(key))
				weights = self.getNegativeConclusionWeights(key)
				outFile.write('{:<16}'.format("Mean: %.3f" % statistics.mean(weights)))
				outFile.write('{:<16}'.format("Median: %.3f" % statistics.median(weights)))
				outFile.write("\n")


	def getPositiveConclusionWeights(self, functionKey):
		weights = []
		for i in  range(self.iterations):
			if (self.conclusions[i] > 0):
				weights.append(self.weights[functionKey][i])
		return weights

	def getNegativeConclusionWeights(self, functionKey):
		weights = []
		for i in  range(self.iterations):
			if (self.conclusions[i] < 0):
				weights.append(self.weights[functionKey][i])
		return weights