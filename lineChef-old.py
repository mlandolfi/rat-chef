import datetime
from newDataManager import DataManager, DataBoi
from simulator import Simulator
from simulator import RepeatPredictor
from Stocks import Stock

class Change(object):

	def __init__(self, initial=0):
		self.numPositive = 1 if initial > 0 else 0
		self.numNegative = 1 if initial < 0 else 0
		self.posTotal = initial if initial > 0 else 0
		self.negTotal = initial if initial < 0 else 0

	def add(self, changeValue):
		if (changeValue > 0):
			self.numPositive += 1
			self.posTotal += changeValue
		else:
			self.numNegative += 1
			self.negTotal += changeValue

	def certainty(self):
		if (self.numPositive > self.numNegative):
			return self.numPositive / (self.numPositive+self.numNegative)
		else:
			return self.numNegative / (self.numPositive+self.numNegative)

	def prediction(self):
		if (self.numPositive > self.numNegative):
			return 1
		return -1

	def __str__(self):
		if (self.numPositive > self.numNegative):
			return "Predict rise by " + str(self.posTotal/self.numPositive) + " with " + str(self.numPositive / (self.numPositive+self.numNegative)) + "% certainty"
		else:
			return "Predict drop by " + str(self.negTotal/self.numNegative) + " with " + str(self.numNegative / (self.numPositive+self.numNegative)) + "% certainty"


class ChangeRay(object):

	def __init__(self, hourIncrements):
		self.hourIncrements = hourIncrements
		self.changes = {}
		for hour in hourIncrements:
			self.changes[hour] = Change(0);

	def addChange(self, hour, changeValue):
		self.changes[hour].add(changeValue)

	def anyStrong(self):
		for inc in self.hourIncrements:
			if (self.changes[inc].certainty() > 0.7):
				return True
		return False

	def getPrediction(self, hourInc):
		return self.changes[hourInc].prediction()

	def __str__(self):
		retStr = ""
		for inc in self.hourIncrements:
			retStr += str(inc) + " hour future: " + str(self.changes[inc]) + "\n"
		retStr += '\n'
		return retStr


class Pattern(object):

	def __init__(self, noise, root, changeHourIncrements):
		self.noise = noise
		self.root = root
		self.numMatches = 1
		self.changeHourIncrements = changeHourIncrements
		self.changes = ChangeRay(changeHourIncrements)
		self.numChecks = 1

	def predict(self, hourInc):
		return self.changes.getPrediction(hourInc)

	def weightedAverage(self, x):
		total = 0
		count = 0
		for y in range(len(self.root[x])):
			total += y * self.root[x][y]
			count += self.root[x][y]
		return total / count

	def doesMatch(self, possibleMatch):
		self.numChecks += 1
		for x in range(len(self.root)):
			avg = self.weightedAverage(x)

			# get the y for the possible match
			matchY = 0
			for y in range(len(possibleMatch[x])):
				if (possibleMatch[x][y] == 1):
					matchY =  y
					break

			# check that it's within the noise for a match and if not return False
			if (not abs(avg - matchY) <= self.noise):
				return False

		# it is a match
		return True

	# lower score is closer match
	def getMatchScore(self, possibleMatch):
		score = 0
		for x in range(len(self.root)):
			avg = self.weightedAverage(x)

			# get the y for the possible match
			matchY = 0
			for y in range(len(possibleMatch[x])):
				if (possibleMatch[x][y] == 1):
					matchY =  y
					break

			score += abs(avg - matchY)

		return score

	def addMatch(self, match, changes):
		for inc in self.changeHourIncrements:
			self.changes.addChange(inc, changes[inc])
		self.numMatches += 1
		for x in range(len(self.root)):
			for y in range(len(self.root[x])):
				self.root[x][y] += match[x][y]

	def shouldClean(self):
		return (self.numMatches+1) / self.numChecks < 0.005

	def isStrong(self):
		return self.numMatches >= 20 and self.changes.anyStrong()

	def __str__(self):
		retStr = ""
		for backwardsY in range(len(self.root[0])-1, -1, -1):
			for x in range(len(self.root)):
				retStr += "{0:4}".format(str(self.root[x][backwardsY]))
				# retStr += str(self.root[x][backwardsY]) + " "
			retStr += "\n"
		return retStr


class LineChef(object):

	def __init__(self, ticker, patternDuration, compressionConstant, changeHourIncrements):
		self.dataBoi = DataBoi(ticker, [])
		self.patterns = []
		self.patternDuration = patternDuration
		self.compressionConstant = compressionConstant
		self.changeHourIncrements = changeHourIncrements

	def getOnRoot(self, values):
		onRoot = []

		minVal = min(values)	# minVal serves as 0 index of y values in onRoot
		maxVal = max(values) # maxVal serves as compressionConstant index of y values in onRoot

		# fill in onRoot to create array
		for xIndex in range(len(values)):
			onRoot.append([0] * self.compressionConstant) # number in values is constant * compressionConstant
			denom = maxVal-minVal if maxVal-minVal > 0 else 1
			yIndex = round(((values[xIndex]-minVal)*self.compressionConstant) / (denom))
			if (yIndex >= len(onRoot[xIndex])):	# if it goes off the array
				onRoot[xIndex][len(onRoot[xIndex])-1] = 1
			else:	# otherwise mark the 1
				onRoot[xIndex][yIndex] = 1

		return onRoot

	def train(self, startDate, endDate, iterations=1):
		for i in range(iterations):
			onDate = startDate
			values = []
			cleanCounter = 0
			while (onDate < endDate):
				# increment time
				onDate = onDate + datetime.timedelta(minutes=1)
				# get current value
				onValue = self.dataBoi.getDataValue(onDate)
				# check for None values
				skip = False
				if (onValue == None):	skip = True
				# get future values
				changeValues = {}
				for inc in self.changeHourIncrements:
					futureValue = self.dataBoi.getDataValue(onDate+datetime.timedelta(hours=inc))
					if (skip or futureValue == None):
						skip = True
						break
					changeValues[inc] = onValue - self.dataBoi.getDataValue(onDate+datetime.timedelta(hours=inc))

				if (skip):
					values = []
					continue

				values.append(onValue)
				# ensure we have a full set of data
				if (len(values) < self.patternDuration):	continue

				onRoot = self.getOnRoot(values)

				# search for matching patterns
				foundMatch = False
				for pat in self.patterns:
					if (pat.doesMatch(onRoot)):
						pat.addMatch(onRoot, changeValues)
						foundMatch = True
						break
				# or adding a new one
				if (not foundMatch):	# if onRoot didn't match any preexisting patterns
					newBoi = Pattern(2, onRoot, self.changeHourIncrements)
					self.patterns.append(newBoi)
					cleanCounter += 1

				# cleaning out of patterns
				if (cleanCounter > 250):
					cleanCounter = 0
					print ("\nCleaning " + str(len(self.patterns)) + " patterns")
					newPatterns = []
					for pat in self.patterns:
						if (not pat.shouldClean()):
							newPatterns.append(pat)
					self.patterns = newPatterns
					print ("Down to " + str(len(self.patterns)) + " patterns")

				# moving half the time forward
				values = values[round(self.patternDuration / 2):]

	def test(self, startDate, endDate, changeHourInc, simBoi):
		onDate = startDate
		values = []
		while (onDate < endDate):
			# increment time
			onDate = onDate + datetime.timedelta(minutes=1)
			# get current value
			onValue = self.dataBoi.getDataValue(onDate)
			# get change value
			changeValue = self.dataBoi.getDataValue(onDate + datetime.timedelta(hours=changeHourInc))
			# check for None values
			if (onValue == None or changeValue == None):
				values = []
				continue

			values.append(onValue)
			# ensure we have a full set of data
			if (len(values) < self.patternDuration):	continue

			onRoot = self.getOnRoot(values)

			minScore = float('inf')
			minPattern = None
			for pat in self.patterns:
				if (not pat.isStrong()): continue
				score = pat.getMatchScore(onRoot)
				if (score < minScore):
					minScore = score
					minPattern = pat

			values.pop(0)	# remove the oldest value

			if (minPattern == None):	continue	# if no pattern matched

			simBoi.processPrediction(minPattern.predict(changeHourInc), onDate)

		simBoi.sellAll(onDate)
						


def main():
	
	chef = LineChef('BTC-USD', 20, 8, [1,2,3,4])

	startDate = datetime.datetime(2018, 2, 4, 8)
	endDate = startDate + datetime.timedelta(days=60)


	chef.train(startDate, endDate)

	strongCount = 0
	for pat in chef.patterns:
		if (pat.isStrong()):
			strongCount += 1
			print ("# Matches: ", pat.numMatches)
			print (pat.changes)
			print (pat)

	print ("STRONG COUNT: ", strongCount)


	testStartDate = endDate
	testEndDate = testStartDate + datetime.timedelta(days=14)
	predictionDelta = 4

	simBoi = RepeatPredictor(5, Stock('BTC-USD'), 1000, 20, testStartDate, datetime.timedelta(hours=predictionDelta))

	chef.test(testStartDate, testEndDate, predictionDelta, simBoi)






if __name__ == "__main__":
	main()