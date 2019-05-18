import requests
from datetime import datetime
from datetime import timedelta
import time

# timeframe is just a string "date1#date2"; data is a list of strings
def addData(ticker, startTime, endTime, data):
	print ("Writing Data...")
	with open("{}.txt".format(ticker), 'a') as outFile:
		outFile.write("TIMEFRAME,{}#{}\n".format(startTime, endTime))
		for dataPoint in data:
			outFile.write("{}\n".format(dataPoint))

# startDate and endDate are iso strings YYYY-MM-DD
# NOTE: doesn't include endDate
def getData(ticker, startDate=None, endDate=None):
	print ("Reading Data...")
	data = {}
	with open("{}.txt".format(ticker), 'r') as inFile:
		line = inFile.readline()
		while (line):
			if (line.split(",")[0] == "TIMEFRAME"):
				line = inFile.readline()
				continue
			splitLine = line.replace("\n", "").split(",")
			# print ("Reading: {}".format(line))
			fullTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(splitLine[0])))
			dateKey = fullTime.split(" ")[0]
			# keeps the data within the date range
			if ((startDate and dateKey < startDate) or (endDate and dateKey >= endDate)):
				line = inFile.readline()
				continue
			timeKey = fullTime.split(" ")[1]
			if (not dateKey in data):
				data[dateKey] = {}
			value = (float(splitLine[1]) + float(splitLine[2]))/2	# avg out the low and high
			data[dateKey][timeKey] = (value, float(splitLine[len(splitLine)-1]))
			line = inFile.readline()	# read in the next line
	return data

# returns the datetime of the newest data we have saved
def newestData(ticker):
	newestTime = 0
	with open("{}.txt".format(ticker), 'r') as inFile:
		line = inFile.readline()
		while (line):
			if (line.split(",")[0] == "TIMEFRAME"):
				# if it's never been set then set it
				lineTime = line.split("#")[1].replace("\n", "")
				if (newestTime == 0):
					newestTime = lineTime
				elif (lineTime > newestTime):
					newestTime = lineTime
			# read in the next line
			line = inFile.readline()
	return newestTime

def earliestData(ticker):
	earliestTime = 0
	with open("{}.txt".format(ticker), 'r') as inFile:
		line = inFile.readline()
		while (line):
			if (line.split(",")[0] == "TIMEFRAME"):
				# if it's never been set then set it
				lineTime = line.split("#")[1].replace("\n", "")
				if (earliestTime == 0):
					earliestTime = lineTime
				elif (lineTime < earliestTime):
					earliestTime = lineTime
			# read in the next line
			line = inFile.readline()
	return earliestTime

def checkAllDays(ticker):
	data = getData(ticker)
	fixedData = []
	count = 0
	currentTime = datetime(2018, 1, 1, 0, 0, 0)
	endTime = currentTime + timedelta(days=365)
	print ("Checking Times...")
	while (currentTime < endTime and count < 5000):
		dateKey = currentTime.isoformat().split("T")[0]
		timeKey = currentTime.isoformat().split("T")[1]
		if (not dateKey in data or not timeKey in data[dateKey]):
			print ("Missing: {}".format(currentTime))
			count += 1
	# 		response = requests.get("https://api.pro.coinbase.com/products/{}/candles".format(ticker),
	# 			params={ 'start': currentTime.isoformat(), 'end': currentTime.isoformat(), 'granularity': 60 })
	# 		temp = response.text.replace("[[", "").replace("]]", "")
	# 		fixedData.append(temp)
	# 		time.sleep(1.5)
		currentTime += timedelta(minutes=1)
	# print ("Filling {} holes".format(len(fixedData)))
	# addData(ticker, "MIXED", "MIXED", fixedData)
	print (count)

def main():
	# need a double hash map date --> time -> (value, volume)
	#	value is avg(low, high)
	ticker = "BTC-USD"

	checkAllDays(ticker)
	return

	# checkAllDays(ticker)
	# return

	# datetime(year, month, day, hour, min, sec, microsec)
	# startDate = datetime(2018, 1, 1, 0, 0, 0)
	startDate = datetime.strptime(newestData(ticker), "%Y-%m-%d %H:%M:%S")
	endDate = startDate + timedelta(hours=6)

	# setting up variables
	currentTime = startDate
	nextTime = currentTime + timedelta(hours=5)
	data = []
	while (currentTime < endDate):
		print ("Waiting...")
		time.sleep(1.5)
		# make the request for data over a 5 hour range
		print ("requesting data from {} to {}".format(currentTime, nextTime))
		response = requests.get("https://api.pro.coinbase.com/products/{}/candles".format(ticker),
			params={ 'start': currentTime.isoformat(), 'end': nextTime.isoformat(), 'granularity': 60 })

		# parse the data for each group of values
		for dataPoint in response.text.split("],["):
			# clean up the data for edge cases, first and last dataPoints
			cleanData = dataPoint.replace("[", "")
			cleanData = cleanData.replace("]", "")
			data.append(cleanData)

		addData(ticker, currentTime, nextTime, data)
		data = []

		# increase the times for the next request
		currentTime = nextTime
		nextTime = nextTime + timedelta(hours=5)

if __name__ == "__main__":
	main()