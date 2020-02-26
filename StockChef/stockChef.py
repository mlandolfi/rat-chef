import datetime
from stockDataManager import StockDataManager

############################################################################################
#																																													 #
#																			Configurations				 															 #
#																																													 #
############################################################################################

defaultConfig = {
	'trainStartDate': datetime.datetime(2015, 1, 5, 8),
	'trainDuration': datetime.timedelta(days=600),
	'trainingIterations': 1,
	'testStartDate': datetime.datetime(2017, 4, 6, 8),
	'testDuration': datetime.timedelta(days=900),
	'patternDuration': 5,		# basically # of data points to use for a pattern
	'patternDelta': datetime.timedelta(days=1),
	'compressionConstant': 1500,	# what the range of the pattern is compressed to 
	'patternNoise': 1,				# how far off a y index can be from the weighted avg to still match that column, in compressed form
	'patternMatchPercentageMin': 0.9,	# % of mins in the pattern that must be close enough to the average to match totally
	'strongPredictorStrengthMin': 0.6,	# min % of predictions that are for the more likely prediction
	'strongPatternMatchesMin': 10,				# min # of occurrences that must match a pattern for it to be considered strong
	'shouldCleanConstant': 0.005,				# value for cleaning our patterns, if > #matches / #checks then should clean
	'predictionDelta': datetime.timedelta(days=1),	# time predicting in the future
}

# set the configuration to use
CONFIG = defaultConfig

############################################################################################
#																																													 #
#																			Object Declarations		 															 #
#																																													 #
############################################################################################

# class to maintain state for a pattern's prediction
class Predictor(object):

	def __init__(self, initial=0):
		self.numPositive = 1 if initial > 0 else 0
		self.numNegative = 1 if initial < 0 else 0
		self.posTotal = initial if initial > 0 else 0
		self.negTotal = initial if initial < 0 else 0

	# function for adding a new recognized value to the predictor
	def add(self, changeValue):
		if (changeValue > 0):
			self.numPositive += 1
			self.posTotal += changeValue
		else:
			self.numNegative += 1
			self.negTotal += changeValue

	# strength is just the measure of how often the predictor has recorded the changeValue
	#		to be the more likely sign (+ or -)
	def getStrength(self):
		if (self.numPositive > self.numNegative):
			return self.numPositive / (self.numPositive+self.numNegative)
		else:
			return self.numNegative / (self.numPositive+self.numNegative)

	# just prediction based on past
	def prediction(self):
		if (self.numPositive > self.numNegative):
			return 1
		return -1

	def __str__(self):
		denom = self.numPositive+self.numNegative
		if (self.numPositive > self.numNegative):
			return "Predict rise by " + str(self.posTotal/self.numPositive) + " with " + str(self.numPositive / (denom)) + "% strength"
		else:
			return "Predict drop by " + str(self.negTotal/self.numNegative) + " with " + str(self.numNegative / (denom)) + "% strength"
		
# class for maintaining state for a pattern constructed by several occurrences of the pattern in history
class Pattern(object):

	def __init__(self, root):
		self.noise = CONFIG['patternNoise']	# how many indecies either way from the average a pattern can be to match
		self.root = root		# the root 2d array of the pattern
		self.numMatches = 1	# number of occurrences that have been matched to this pattern
		self.predictor = Predictor(0)	# Predictor object to store state about prediction
		self.numChecks = 1	# number of times the Pattern has been chexked against occurrences, for cleaning purposes

	# get what the pattern predicts at its current state
	def getPrediction(self):
		return self.predictor.prediction()

	# calculates the weigthed average of a column, basically the average y value for the pattern given x
	def calcWeightedAvg(self, xIndex):
		total = 0
		count = 0
		for y in range(len(self.root[xIndex])):	# y is the index of the column we're looking for the avg in
			total += y * self.root[xIndex][y]			# self.root[x][y] is the # of times matched occurrences have been at that specific index
			count += self.root[xIndex][y]
		return total / count

	# checks if an occurrence matches this pattern
	def doesMatch(self, possibleMatch):
		self.numChecks += 1

		numIndexesMatched = 0
		for x in range(len(self.root)):
			avg = self.calcWeightedAvg(x)
			# get the y for the possible match
			matchY = 0
			# print(len(possibleMatch), x)
			for y in range(len(possibleMatch[x])):
				if (possibleMatch[x][y] == 1):
					matchY =  y
					break
			# check if this index is within the match
			if (abs(avg - matchY) <= self.noise):
				numIndexesMatched += 1

		# check if it matched the correct percentage of indexes
		return numIndexesMatched / len(self.root) >= CONFIG['patternMatchPercentageMin']

	# calculates and returns the score of a possible match, lower is better because less difference
	def scoreMatch(self, possibleMatch):
		score = 0
		for x in range(len(self.root)):
			avg = self.calcWeightedAvg(x)
			# search for the y for the possible match
			for y in range(len(possibleMatch[x])):
				if (possibleMatch[x][y] == 1):	# found the index
					score += pow(abs(avg - y), 2)	# squared to greater differentiate mismatches?
					break

		return score

	# given an occurrence that matches integrate it into the pattern's root, changeValue is future value
	def integrateMatch(self, match, changeValue):
		self.predictor.add(changeValue)
		self.numMatches += 1
		for x in range(len(self.root)):		# note x and y are indecies not values
			for y in range(len(self.root[x])):
				self.root[x][y] += match[x][y]

	# returns if the pattern should be cleaned out as it's become stagnant
	def shouldClean(self):
		return self.numMatches / self.numChecks < CONFIG['shouldCleanConstant']

	# returns if this pattern is strong by the configurations standards
	def isStrong(self):
		return self.numMatches >= CONFIG['strongPatternMatchesMin'] and self.predictor.getStrength() >= CONFIG['strongPredictorStrengthMin']
		

class LineChef(object):

	def __init__(self):
		self.dataBoi = StockDataManager('APPL_5yr.csv')
		self.patterns = []
		self.patternDuration = CONFIG['patternDuration']
		self.compressionConstant = CONFIG['compressionConstant']
		self.predictionDelta = CONFIG['predictionDelta']

	# function for converting a values array into a compressed onRoot array
	def getOnRoot(self, values):
		onRoot = []
		minVal = min(values)	# minVal serves as 0 index of y values in onRoot
		maxVal = max(values) # maxVal serves as compressionConstant index of y values in onRoot
		# fill in onRoot to create array
		for xIndex in range(len(values)):
			onRoot.append([0] * self.compressionConstant) # number in values is constant * compressionConstant
			denom = maxVal-minVal if maxVal-minVal > 0 else 1
			yIndex = round(((values[xIndex]-minVal)*self.compressionConstant) / (denom)) - 1
			onRoot[xIndex][yIndex] = 1
		return onRoot


	def train(self):
		print ("Training...\n")
		onDate = CONFIG["trainStartDate"]
		endDate = CONFIG["trainStartDate"]+CONFIG["trainDuration"]
		values = []
		cleanTicker = 0

		while (onDate < endDate):
			onDate = onDate + CONFIG["patternDelta"]
			print ("\r"+str(onDate)+" - "+str(endDate), end="")
			# get data point
			onData = self.dataBoi.getVolume(onDate)
			# get current value
			onValue = self.dataBoi.getOpen(onDate)
			#get future value
			futureValue = self.dataBoi.getOpen(onDate + self.predictionDelta)
			if (onValue == None or futureValue == None):
				continue
			# calculate changeValue
			changeValue = futureValue - onValue
			values.append(onValue)	
			if (len(values) < CONFIG["patternDuration"]):	# ensure we have a full pattern to continue
				continue

			onRoot = self.getOnRoot(values)

			foundMatch = False
			for pat in self.patterns:
				if (pat.doesMatch(onRoot)):
					foundMatch = True
				pat.integrateMatch(onRoot, changeValue)
			cleanTicker += 1
			if (not foundMatch):
				self.patterns.append(Pattern(onRoot))

			# clean out the stagnant patterns
			if (cleanTicker > 250):
				print ("\ncleaned: ", len(self.patterns), end="")
				cleanTicker = 0
				newPatterns = []
				for pat in self.patterns:
					if (not pat.shouldClean()):
						newPatterns.append(pat)
				self.patterns = newPatterns
				print ("down to ", len(self.patterns))

			# we don't only want to move one delta forward as that will likely match its predecessor but moving
			#		halfway through should give enough difference while still trying to maximize data usage
			values = values[len(values)//2:]
		print()
		

	def test(self):
		print ("TESTING...\n")
		numCorrect = 0
		numGuesses = 0
		onDate = CONFIG['testStartDate']
		endDate = CONFIG['testStartDate'] + CONFIG['testDuration']
		values = []
		while (onDate < endDate):
			onDate = onDate + CONFIG["patternDelta"]
			print ("\r"+str(onDate)+" - "+str(endDate), end="")
			# get data point
			onData = self.dataBoi.getVolume(onDate)
			# get current value
			onValue = self.dataBoi.getOpen(onDate)
			#get future value
			futureValue = self.dataBoi.getOpen(onDate + self.predictionDelta)
			if (onValue == None or futureValue == None):
				continue
			# calculate changeValue
			changeValue = futureValue - onValue
			values.append(onValue)	
			if (len(values) < CONFIG["patternDuration"]):	# ensure we have a full pattern to continue
				continue

			onRoot = self.getOnRoot(values)

			# check for closest match, this logic could also change to average all matches possible weighting those that are closer
			minScore = float('inf')
			minPattern = None
			for pat in self.patterns:
				if (not pat.isStrong()): continue
				score = pat.scoreMatch(onRoot)
				if (score < minScore):
					minScore = score
					minPattern = pat

			values.pop(0)	# remove the oldest value

			if (minPattern == None):	continue	# if no pattern matched

			numGuesses += 1
			if ((minPattern.getPrediction() > 0 and changeValue > 0) or (minPattern.getPrediction() < 0 and changeValue < 0)):
				numCorrect += 1

		print ("\nPredicted {} / {} or ".format(numCorrect, numGuesses), "{0:0.2f}".format(numCorrect / numGuesses))



def main():
	chef = LineChef()

	chef.train()

	chef.test()





if __name__ == "__main__":
	main()