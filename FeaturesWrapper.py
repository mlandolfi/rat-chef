import datetime
import numpy as np

class FeaturesWrapper(object):
	"""docstring for FeaturesWrapper"""
	def __init__(self, stock):
		super(FeaturesWrapper, self).__init__()
		self.stock = stock
		self.initializeMinuteTimes(5, 120)
		self.initializeHourTimes(2, 12)
		# self.initializeDayTimes(1, 7)

	# breakdown must be 1< 60, it's for the time interval
	def initializeMinuteTimes(self, breakdown, limit):
		self.minuteTimes = []
		for i in range(breakdown, limit, breakdown):
			self.minuteTimes.append(datetime.timedelta(minutes=i))

	def initializeHourTimes(self, breakdown, limit):
		self.hourTimes = []
		for i in range(breakdown, limit, breakdown):
			self.hourTimes.append(datetime.timedelta(hours=i))

	def setValues(self, whenFrom):
		self.values = []	# list of values lists for times
		allTimes = self.minuteTimes + self.hourTimes
		for i in range(len(allTimes)):
			# first for values
			self.values.append(self.stock.getAllSampleValues(0, whenFrom, (allTimes[i].seconds//60)%60, allTimes[i].seconds//3600, allTimes[i].days, 1))
			# also for volume
			# self.values.append(self.stock.getAllSampleValues(1, whenFrom, (allTimes[i].seconds//60)%60, allTimes[i].seconds//3600, allTimes[i].days, 1))

	def getFeatures(self, whenFrom):
		# set the values to use in feature list creation
		self.setValues(whenFrom)

		features = np.zeros(self.getVectorSize())
		ticker = 0
		# for each measurement
		for i in range(5):
			# now for each value
			for j in range(len(self.values)):
				# now compare it to each other value
				for k in range(len(self.values)):
					features[ticker] = 1 if self.values[j][i] > self.values[k][i] else -1
					ticker += 1
					# features.append(1 if self.values[j][i] > self.values[k][i] else -1)

		return features

	def getVectorSize(self):
		return 5 * (1*(len(self.hourTimes)+len(self.minuteTimes))) ** 2


		