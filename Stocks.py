# file to hold stocks class to store stock data
import json
import datetime
import statistics

class Stock(object):

	def __init__(self, symbol, dataFile):
		self.symbol = symbol
		self.volatility = 5	# 0-10
		self.values = {}	# key is time (second part of time), value is (value, volume)
		self.dataFile = dataFile
		self.lastValueRecorded = ()
		self.previousValues = {}	# key is date, value is value {} ^^
		self.volumeDeviationPercentage = 0 #most recent volume compared to all previous volumes
		# functions to execute on instantiation
		self.readValues()

	""" adds a time and value into self.values if it isn't already in there,
		also sets the self.lastValueRecorded to a tuple of (time, value, volume)
		if it's from a previous day it adds it to the previous day """
	def addValue(self, time, value, volume, day):
		if (day == datetime.date.today().strftime('%Y-%m-%d')):	# today so add it to self.values
			if (not time in self.values.keys()):
				self.lastValueRecorded = (time, value, volume)
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

	def updateVolatility(self):
		pass

	"""Function to calculate the percent difference between two values, used for
	calculating self.volumeDeviationPercentage using the stdDev of all previous volumes
	and the latest recorded volume """
	def getChange(self, current, previous):
		if current == previous:
			return 0
		try:
			return (abs(current - previous) / previous) * 100.0
		except ZeroDivisionError:
			return 0 #Not sure if this is the best way to handle division by 0, probably is

	"""Calculates volumeDeviationPercentage using the std dev of all previous volumes
	and the last recorded volume"""
	def updateVolumeDeviationPercentage(self):
		tempList = []
		#going through all of today's recorded volumes
		for time, valueTuple in self.values.items():
			tempList.append(valueTuple[1]) #append volume
		#going through all of our past day recorded volumes
		for day, dayValues in self.previousValues.items(): 	
			for time, valueTuple in dayValues.items():
				tempList.append(valueTuple[1]) #appending volume
		stdDev = statistics.stdev(tempList) #standard deviation of all volumes (what is normal)
		self.volumeDeviationPercentage = self.getChange(self.lastValueRecorded[2], stdDev)

	def __str__(self):
		return self.symbol