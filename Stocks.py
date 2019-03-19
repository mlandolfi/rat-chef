# file to hold stocks class to store stock data
import json
import datetime


class Stock(object):

	def __init__(self, symbol, dataFile):
		self.symbol = symbol
		self.volatility = 5	# 0-10
		self.values = {}	# key is time, value is (value, volume)
		self.dataFile = dataFile
		self.previousValues = {}	# key is date, value is value {} ^^
		self.volumeDeviationPercentage = 0
		# functions to execute on instantiation
		# self.readValues()

	def addValueToday(self, time, value, volume):
		if (not time in self.values.keys()):
			self.values[time] = (value, volume)

	def addPreviousValues(self, day, time, value, volume):
		if (not day in self.previousValues.keys()):
			self.previousValues[day] = {}
		if (not time in self.previousValues[day].keys()):
			self.previousValues[day][time] = (value, volume)

	def saveValues(self):
		data = self.previousValues
		data[datetime.date.today().strftime('%Y-%m-%d')] = self.values
		with open(self.dataFile, "w") as outFile:
			json.dump(data, outFile)

	def readValues(self):
		with open(self.dataFile) as inFile:
			data = json.load(inFile)
		for day, dayValues in data.items():
			# key ex. 2019-24-03, value ex. {  }
			if (day == datetime.date.today().strftime('%Y-%m-%d')):
				# first if it's today value
				for time, value in dayValues.items():
					self.addValueToday(time, value[0], value[1])
			else:
				# now if it's a previous day
				self.previousValues[day] = {}
				for time, value in dayValues.items():
					self.addPreviousValues(day, time, value[0], value[1])

	def updateVolatility():
		pass

	def updateVolumeDeviationPercentage():
		tempList = []
		for time in self.values:
			tempList.append(time[1])

	