import csv

class StockDataManager(object):

	def __init__(self, fileName):
		self.data = {}
		self.initializeLocalStats()
		print ("Reading in {}".format(fileName))
		with open(fileName, mode="r") as inFile:
			csvReader = csv.DictReader(inFile)
			firstLine = True
			for row in csvReader:
				if (firstLine):
					firstLine = False
					continue	# column names
				# construct the dict for the days data
				dailyData = {}
				dailyData["open"] = float(row[" Open"].strip(" $"))
				dailyData["close"] = float(row[" Close/Last"].strip(" $"))
				dailyData["volume"] = int(row[" Volume"].strip(" $"))
				# put days data under the date
				self.data[row["Date"]] = dailyData
				self.updateLocalStats(dailyData)
		print ("Local Stats:")
		print ("\tVolume Min: {}".format(self.volumeMin))
		print ("\tVolume Max: {}".format(self.volumeMax))
		print ("\tValue Min: {}".format(self.valueMin))
		print ("\tValue Max: {}".format(self.valueMax))

	def initializeLocalStats(self):
		self.volumeMin = float("inf")
		self.volumeMax = float("-inf")
		self.valueMin = float("inf")
		self.valueMax = float("-inf")

	def updateLocalStats(self, data):
		if (data["volume"] > self.volumeMax):
			self.volumeMax = data["volume"]
		if (data["volume"] < self.volumeMin):
			self.volumeMin = data["volume"]
		if (data["open"] > self.valueMax):
			self.valueMax = data["open"]
		if (data["open"] < self.valueMin):
			self.valueMin = data["open"]
		if (data["close"] > self.valueMax):
			self.valueMax = data["close"]
		if (data["close"] < self.valueMin):
			self.valueMin = data["close"]

	def getData(self, date):
		if (not date.strftime("%m/%d/%Y") in self.data):
			return None
		return self.data[date.strftime("%m/%d/%Y")]

	def getOpen(self, date):
		if (not date.strftime("%m/%d/%Y") in self.data):
			return None
		return self.data[date.strftime("%m/%d/%Y")]["open"]

	def getClose(self, date):
		if (not date.strftime("%m/%d/%Y") in self.data):
			return None
		return self.data[date.strftime("%m/%d/%Y")]["close"]

	def getVolume(self, date):
		if (not date.strftime("%m/%d/%Y") in self.data):
			return None
		return self.data[date.strftime("%m/%d/%Y")]["volume"]


def main():
	db = StockDataManager("APPL_5yr.csv")

if __name__ == "__main__":
	main()