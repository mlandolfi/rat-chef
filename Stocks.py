# file to hold stocks class to store stock data
import json
import datetime
import statistics

""" notes
One would have to divide the standard deviation by the closing price to directly compare volatility for the two securities.
https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:standard_deviation_volatility
https://stattrek.com/statistics/dictionary.aspx?definition=z_score
"""

class Stock(object):

	def __init__(self, symbol, dataFile):
		self.symbol = symbol
		self.volatility = 5	# 0-10
		self.values = {}	# key is time (second part of time), value is (value, volume)
		self.dataFile = dataFile
		self.lastValueRecorded = ()
		self.previousValues = {}	# key is date, value is value {} ^^
		self.populationMeans = () #(volatility, volume) -> means of all recorded volatilities and volumes, including today
		self.stdDevs = () #(volatility, volume) -> numerical value used to indicate how widely individuals in a group vary. If individual observations vary greatly from the group mean, the standard deviation is big; and vice versa.
		self.zScores = () #(volatility, volume) -> z-score indicates how many standard deviations an element is from the mean, see website in notes for more info
		# functions to execute on instantiation
		self.readValues()

	""" ############################ Functions that work with our data files ############################ """

	""" adds a time and value into self.values if it isn't already in there,
		also sets the self.lastValueRecorded to a tuple of (time, value, volume)
		if it's from a previous day it adds it to the previous day """
	def addValue(self, time, value, volume, day):
		if (day == datetime.date.today().strftime('%Y-%m-%d')):	# today so add it to self.values
			if (not time in self.values.keys()):
				self.lastValueRecorded = (value, volume, time)
				self.values[time] = (value, volume)
		else:	# not today so previous value
			if (not day in self.previousValues.keys()):
				self.previousValues[day] = {}
			if (not time in self.previousValues[day].keys()):
				self.previousValues[day][time] = (value, volume)

	""" combines previous values and the current days values and saves
		them to a self.dataFile """
	def saveValues(self):
		data = self.previousValues
		data[datetime.date.today().strftime('%Y-%m-%d')] = self.values
		with open(self.dataFile, "w") as outFile:
			json.dump(data, outFile)

	""" reads in values from self.dataFile and populates self.values
		and self.previousValues properly """
	def readValues(self):
		with open(self.dataFile) as inFile:
			data = json.load(inFile)
		for day, dayValues in data.items():
			# key ex. 2019-24-03, value ex. {  }
			for time, value in dayValues.items():
				self.addValue(time, float(value[0]), float(value[1]), day)

	""" ############################ Helper functions for update functions ############################ """

	""" returns a list containing all recorded values for this stock if index is 0, 
		or all recorded volumes for this stock if index is 1"""
	def collectRecordedValues(self, index):
		retList = []
		#going through all of today's recorded values if index is 0 or volumes if index 1
		for time, valueTuple in self.values.items():
			retList.append(valueTuple[index]) 
		#going through all of our past day recorded volumes
		for day, dayValues in self.previousValues.items(): 	
			for time, valueTuple in dayValues.items():
				retList.append(valueTuple[index]) 
		return retList

	"""Calculates z-score for this stock. Requires that self.populationMeans and self.stdDevs 
		have been set and updated.
		index is 0 if we are finding z-score of values (for volatility), 1 if z-score of volumes"""
	def zScore(self, index):
		#z = (X - μ) / σ, where X is latest recorded value, μ is the population mean, and σ is the standard deviation
		return (self.lastValueRecorded[index] - self.populationMeans[index]) / self.stdDevs[index]

	""" ############################ Update stock functions ############################ """

	"""Updates the population mean (all recorded items, from today and past). index 0 for values, 1 for volumes
		currenList is obtained from collectRecordedValuesFunction, which has the same index 0/1 rules."""
	def updatePopulationMean(self, index, currentList):
		self.populationMeans[index] = statistics.mean(currentList)

	"""Updates the stdDev (all recorded items, from today and past). index 0 for values, 1 for volumes"""
	def updateStdDev(self, index, currentList):
		self.stdDevs[index] = statistics.stddev(currentList)

	"""Requires that updatePopulationMeans/updateStdDev have both been called, in that order.
		Updates z-score for this stock. 
		index is 0 if we are finding z-score of values (for volatility), 1 if z-score of volumes"""
	def updateZScore(self, index, currentList):
		self.zScores[index] = zScore(index)

	def __str__(self):
		return self.symbol