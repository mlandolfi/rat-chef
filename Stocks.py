# file to hold stocks class to store stock data
import json

class Stock(object):

	def __init__(self, symbol):
		self.symbol = symbol
		self.volatility = 5	# 0-10
		self.values = {}	# key is time, value is (value, volume)
		self.previousValues = {}	# key is date, value is value {} ^^
		# functions to execute on instantiation
		# self.readValues()

	def addValue(self, time, value, volume):
		# with open("values")
		pass

	def saveValues(self):
		pass
		data = {}
		data["people"] = []
		data["people"].append(("Frank", "Jill"))
		with open("values.txt", "w") as outFile:
			json.dump(data, outFile)
		# writes values to file

	def readValues(self):
		pass
		# reads in previous and current day values

