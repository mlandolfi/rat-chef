from cryptoDataCollection import getData

import statistics
from scipy import stats
import datetime
from functools import reduce
import operator as op
from numpy import exp as npexp, array as nparray, random as nprandom, dot as npdot, isnan

def nCr(n, r):
	r = min(r, n-r)
	numer = reduce(op.mul, range(n, n-r, -1), 1)
	denom = reduce(op.mul, range(1, r+1), 1)
	return numer / denom

def sampleRange(sample):
	return max(sample)-min(sample)

def slope(sample):
	slope, intercept, r_value, p_value, std_err = stats.linregress(range(len(sample)), sample)
	return slope

def iqr(sample):
	return stats.iqr(sample, rng=(25,75), interpolation='midpoint')

class DataManager(object):

	def __init__(self, ticker, hourIncrements):
		self.data = getData(ticker)
		self.hourIncrements = hourIncrements
		self.setStats()

	def setStats(self):
		self.stats = [
		('mean', statistics.mean),
		('median', statistics.median),
		('stdev', statistics.stdev),
		('range', sampleRange),
		('slope', slope),
		('iqr', iqr)]

	def getDataValue(self, when, index=0):
		dateKey = when.isoformat().split("T")[0]
		timeKey = when.isoformat().split("T")[1]
		if (not dateKey in self.data.keys() or not timeKey in self.data[dateKey].keys()):
			return None
		return self.data[dateKey][timeKey][index]

	def inputSize(self):
		return (int) (nCr(len(self.hourIncrements), 2)*len(self.stats))

	# divides the data into { n: [price-values] } for n = 1-numHoursBack
	def divideData(self, fromWhen):
		retData = {}
		for hoursBack in self.hourIncrements:
			retData[hoursBack] = []

		currentTime = fromWhen
		while currentTime > (fromWhen - datetime.timedelta(hours=max(self.hourIncrements))):
			y = self.getDataValue(currentTime, 1)
			for hoursBack in self.hourIncrements:
				if (y and (currentTime > (fromWhen - datetime.timedelta(hours=hoursBack)))):
					retData[hoursBack].append(y)
			currentTime = currentTime - datetime.timedelta(minutes=1)

		return retData

	def calcFeatures(self, when):
		dividedData = self.divideData(when)
		values = {}
		for stat, statFunction in self.stats:	# cycle through each statistic
			values[stat] = {}	# set it to dicitonary to use hoursBack as keys
			for hoursBack in self.hourIncrements:	# cycle through hourIncrements
				try:
					values[stat][hoursBack] = statFunction(dividedData[hoursBack])	# set the stat using function
				except Exception as e:
					values[stat][hoursBack] = -1

		features = []
		for smallerHour in self.hourIncrements:	# cycle through all the hours
			for largerHour in range(smallerHour+1, max(self.hourIncrements)+1):	# cycle through all the hours greater than smaller one
				if (not largerHour in self.hourIncrements):
					continue	# if it's not an increment skip it
				for stat, statFunction in self.stats:	# calculate for each statistic
					if (values[stat][smallerHour] == -1 or values[stat][largerHour] == -1):
						features.append(0)
					else:
						features.append(1 if values[stat][smallerHour] > values[stat][largerHour] else -1)

		return nparray([features])




####################################################################################
###																																							 ###
###																																							 ###
###																																							 ###
###																																							 ###
####################################################################################





class DataBoi(object):

	def __init__(self, ticker, hourIncrements):
		self.data = getData(ticker)
		self.hourIncrements = hourIncrements
		self.stats = [
			('slope', slope),
			('stdev', statistics.stdev),
		]

	def getDataValue(self, when, index=0):
		dateKey = when.isoformat().split("T")[0]
		timeKey = when.isoformat().split("T")[1]
		if (not dateKey in self.data.keys() or not timeKey in self.data[dateKey].keys()):
			return None
		return self.data[dateKey][timeKey][index]

	def inputSize(self):
		return (int) (len(self.hourIncrements) * len(self.stats))

	# divides the data into { n: [price-values] } for n = 1-numHoursBack
	def divideData(self, fromWhen, volume=False):
		retData = {}
		for hoursBack in self.hourIncrements:
			retData[hoursBack] = []

		currentTime = fromWhen
		while currentTime > (fromWhen - datetime.timedelta(hours=max(self.hourIncrements))):
			y = self.getDataValue(currentTime, 0 if volume else 1)
			for hoursBack in self.hourIncrements:
				if (y and (currentTime > (fromWhen - datetime.timedelta(hours=hoursBack)))):
					retData[hoursBack].append(y)
			currentTime = currentTime - datetime.timedelta(minutes=1)

		return retData

	def calcFeatures(self, when):
		dividedData = self.divideData(when)

		features = []

		for featureKey, featureFunc in self.stats:
			for hoursBack in self.hourIncrements:
				try:
					features.append(featureFunc(dividedData[hoursBack]))
				except Exception as e:
					features.append(0)
				finally:
					features[len(features)-1] = features[len(features)-1] if not isnan(features[len(features)-1]) else 0

		return nparray([features])










