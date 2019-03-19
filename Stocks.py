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
		self.previousValues = {}	# key is date, value is value {} ^^
		self.volumeDeviationPercentage = 0
		# functions to execute on instantiation
		self.readValues()

	""" adds a time and value into self.values if it isn't already in there,
		also sets the self.lastValueRecorded to a tuple of (time, value, volume) """
	def addValueToday(self, time, value, volume):
		if (not time in self.values.keys()):
			self.lastValueRecorded = (time, value, volume)
			self.values[time] = (value, volume)

	""" adds a time and value into self.values[day], won't add duplicates """
	def addPreviousValues(self, day, time, value, volume):
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
			if (day == datetime.date.today().strftime('%Y-%m-%d')):
				# first if it's today value
				for time, value in dayValues.items():
					self.addValueToday(time, value[0], int(value[1]))
			else:
				# now if it's a previous day
				self.previousValues[day] = {}
				for time, value in dayValues.items():
					self.addPreviousValues(day, time, value[0], int(value[1]))

	def updateVolatility(self):
		pass

	"""Calculates volumeDeviationPercentage using volumes from today and the past"""
	def updateVolumeDeviationPercentage(self):
		# key is time (second part of time), value is (value, volume)
		tempList = []
		for time, valueTuple in self.values.items():
			tempList.append(valueTuple[1]) #append volume
		#self.previousValues = {}	# key is date, value is value {} ^^
		for day, dayValues in self.previousValues.items():
			for time, value in dayValues.items():
				tempList.append(value[1]) #appending volume
		stdDev = statistics.stdev(tempList)
		print(stdDev)

	def __str__(self):
		return self.symbol