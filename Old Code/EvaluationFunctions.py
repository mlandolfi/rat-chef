import math
from Stocks import Stock
from FileManager import FileManager

########### helper functions ###########

def getDailyMean(stock):
	total = 0
	for time in stock.values:
		total += stock.values[time][0]
	return total / len(stock.values)

def getDailyVolumeInXY(stock):
	xyValues = []
	for time in stock.values:
		xValue = float(time.split(":")[0] + "." + time.split(":")[1])
		xyValues.append((xValue, stock.values[time][1]))
	return xyValues

########### evaluation functions ###########
# These should all try to normalize their values in some way

def dailyValueStandardDeviation(stock):
	dailyMean = getDailyMean(stock)
	numerator = 0.0
	for time in stock.values:
		numerator += (stock.values[time][0]-dailyMean) ** 2
	return (numerator / len(stock.values)) ** (0.5)


def dailyValueRegressionSlope(stock):
	dailyXY = stock.getDailyValuesInXY()
	xSum, xSquaredSum, ySum, xySum = (0.0,0.0,0.0,0.0)
	for point in dailyXY:
		xSum += point[0]
		xSquaredSum += point[0] ** 2
		ySum += point[1]
		xySum += point[0] * point[1]
	return ((len(dailyXY)*xySum)-(xSum*ySum)) / ((len(dailyXY)*xSquaredSum) - (xSum**2))

def dailyValueRange(stock):
	maxY = float("-inf")
	minY = float("inf")
	for time in stock.values:
		if (stock.values[time][0] > maxY):	maxY = stock.values[time][0]
		if (stock.values[time][0] < minY):	minY = stock.values[time][0]
	return maxY - minY

def dailyVolumeRange(stock):
	maxY = float("-inf")
	minY = float("inf")
	for time in stock.values:
		if (stock.values[time][1] > maxY):	maxY = stock.values[time][1]
		if (stock.values[time][1] < minY):	minY = stock.values[time][1]
	return (maxY - minY) / maxY

def dailyVolumeMean(stock):
	total = 0
	for time in stock.values:
		total += stock.values[time][1]
	return total / len(stock.values)

def dailyVolumeRegressionSlope(stock):
	dailyXY = getDailyVolumeInXY(stock)
	xSum, xSquaredSum, ySum, xySum = (0.0,0.0,0.0,0.0)
	for point in dailyXY:
		xSum += point[0]
		xSquaredSum += point[0] ** 2
		ySum += point[1]
		xySum += point[0] * point[1]
	return ((len(dailyXY)*xySum)-(xSum*ySum)) / ((len(dailyXY)*xSquaredSum) - (xSum**2))



ALL_EVALUATION_FUNCTIONS = {
	'dailyValueStandardDeviation': { "key": 'dailyValueStandardDeviation', "func": dailyValueStandardDeviation, "weight": 0 },
	'dailyValueRegressionSlope': { "key": 'dailyValueRegressionSlope', "func": dailyValueRegressionSlope, "weight": 0 },
	'dailyValueRange': { "key": 'dailyValueRange', "func": dailyValueRange, "weight": 0 },
	'dailyVolumeRange': { "key": 'dailyVolumeRange', "func": dailyVolumeRange, "weight": 0 },
	# 'dailyVolumeMean': { "key": 'dailyVolumeMean', "func": dailyVolumeMean, "weight": 0 },
	'dailyVolumeRegressionSlope': { "key": 'dailyVolumeRegressionSlope', "func": dailyVolumeRegressionSlope, "weight": 0 },
}

# testStock = Stock('GOOGL', 'googleValues.txt')
# fileManager = FileManager("../../Dropbox/")
# fileManager.loadValues(testStock)
# for func in ALL_EVALUATION_FUNCTIONS:
# 	print(func["key"])
# 	print(func["func"](testStock))
# 	print("")
