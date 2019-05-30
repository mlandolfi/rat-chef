import datetime
import os
import json

class FileManager(object):

	""" initializes a file manager, must pass valid dropbox path """
	def __init__(self, dropboxPath):
		self.dropboxPath = dropboxPath

	""" loads values from the dropbox file into a Stock object, returns True
		if successfully loaded values and False if errored, will print error message """
	def loadValues(self, stock):
		try:
			fullPath = self.dropboxPath + stock.dataFile
			with open(fullPath, "r") as inFile:
				data = json.load(inFile)
			for day, dayValues in data.items():
				# key ex. 2019-24-03, value ex. {  }
				for time, value in dayValues.items():
					stock.addValue(time, float(value[0]), float(value[1]), day)
			return True
		except Exception as e:
			print (e)
			print ("ERROR: failed to load values for %s" % (stock.symbol))
		return False

	""" stores values from Stock object file into dropbox file, returns True
		if successfully stored values and False if errored, will print error message """
	def storeValues(self, stock):
		try:
			fullPath = self.dropboxPath + stock.dataFile
			data = stock.previousValues
			data[datetime.date.today().strftime('%Y-%m-%d')] = stock.values
			with open(fullPath, "w") as outFile:
				json.dump(data, outFile)
			return True
		except Exception as e:
			print ("ERROR: failed to store values for %s" % (stock.symbol))
		return False

	""" checks to see if a given file exists in the dropbox path, returns True
		if one exists and False if not """
	def fileExistsInPath(self, fileName):
		fullPath = self.dropboxPath + fileName
		return os.path.isfile(fullPath)