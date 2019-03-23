# file to hold stocks class to store stock data
import json
import datetime
import statistics
from fractions import Fraction

""" notes
One would have to divide the standard deviation by the closing price to directly compare volatility for the two securities.
https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:standard_deviation_volatility
https://stattrek.com/statistics/dictionary.aspx?definition=z_score

Skewness:
https://brownmath.com/stat/shape.htm
when the plot is extended towards the right side more, it denotes positive skewness, wherein mode < median < mean. 
On the other hand, when the plot is stretched more towards the left direction, 
then it is called as negative skewness and so, mean < median < mode.

any symmetric data should have a skewness near zero. 
Negative values for the skewness indicate data that are skewed left (longer tail on left side of graph)
and positive values for the skewness indicate data that are skewed right. (longer tail on right side of graph)

Kurtosis: Measure of the peak of the graph
https://www.itl.nist.gov/div898/handbook/eda/section3/eda35b.htm

"""

class Stock(object):

	def __init__(self, symbol, dataFile):
		self.symbol = symbol
		self.volatility = 5	# 0-10
		self.dataFile = dataFile
		self.dailyValuesInXY = False
		self.values = {}	# key is time (second part of time), value is (value, volume)
		self.previousValues = {}	# key is date, value is value {} ^^
		self.lastValueRecorded = 0#tuple of (value, volume, time)
		#mean, stdDev, zScore, skewness, kurtosis are all POPULATION calculations, not SAMPLE
		self.means = [0.0, 0.0] #(volatility, volume) -> means of all recorded volatilities and volumes, including today
		self.stdDevs = [0.0, 0.0] #(volatility, volume) -> numerical value used to indicate how widely individuals in a group vary. If individual observations vary greatly from the group mean, the standard deviation is big; and vice versa.
		self.zScores = [0.0, 0.0] #(volatility, volume) -> z-score indicates how many standard deviations an element is from the mean, see website in notes for more info
		self.skewness = [0.0, 0.0] #(volatility, volume) skewness is a measure of the asymmetry of the probability distribution of a real-valued random variable about its mean
		self.kurtosis = [0.0, 0.0] #(volatility, volume) the sharpness of the peak of a frequency-distribution curve.
		# functions to execute on instantiation

	""" ############################ Functions that work with our data files ############################ """
	
	""" adds a time and value into self.values if it isn't already in there,
		also sets the self.lastValueRecorded to a tuple of (value, volume, time)
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

	""" returns a list of the daily values in (x,y) format where x is time ex. 9.55
		and y is the value of the stock at that time
		if this hasn't been called yet then it'll set self.dailyValuesInXY so it
		won't have to recalculate it next time """
	def getDailyValuesInXY(self):
		if (self.dailyValuesInXY):	return self.dailyValuesInXY
		xyValues = []
		for time in self.values:
			xValue = float(time.split(":")[0] + "." + time.split(":")[1])
			xyValues.append((xValue, self.values[time][0]))
		self.dailyValuesInXY = xyValues
		return xyValues

	""" ############################ Helper functions for update functions ############################ """

	""" returns a list containing all recorded values for this stock if index is 0, 
		or all recorded volumes for this stock if index is 1"""
	def collectRecordedValues(self, index):
		retList = []
		#going through all of today's recorded values if index is 0 or volumes if index 1
		for time in self.values:
			retList.append(self.values[time][index]) 
		#going through all of our past day recorded volumes
		for day in self.previousValues:
			for time in self.previousValues[day]:
				retList.append(self.previousValues[day][time][index])

		return retList

	"""Calculates z-score for this stock. Requires that self.means and self.stdDevs 
		have been set and updated.
		index is 0 if we are finding z-score of values (for volatility), 1 if z-score of volumes"""
	def zScore(self, index):
		#z = (X - μ) / σ, where X is latest recorded value, μ is the population mean, and σ is the standard deviation
		print("lastRecorded: ", self.lastValueRecorded)
		return (self.lastValueRecorded[index] - self.means[index]) / self.stdDevs[index]

	""" ############################ Update stock functions ############################ """

	"""Updates the population mean (all recorded items, from today and past). index 0 for values, 1 for volumes
		currenList is obtained from collectRecordedValuesFunction, which has the same index 0/1 rules."""
	def updateMean(self, index, currentList):
		self.means[index] = statistics.mean(currentList)

	"""Updates the population std dev (all recorded items, from today and past). index 0 for values, 1 for volumes"""
	def updateStdDev(self, index, currentList):
		self.stdDevs[index] = statistics.pstdev(currentList)

	"""Requires that updateMeans/updateStdDev have both been called, in that order, and that
		lastValueRecorded has values.
		Updates the population z-score for this stock. 
		index is 0 if we are finding z-score of values (for volatility), 1 if z-score of volumes"""
	def updateZScore(self, index, currentList):
		self.zScores[index] = self.zScore(index)

	"""skewness of a normal distribution is 0
		negative values for skewness indicate that the data is skewed left
		positive values for skewness indicate that the data is skewed right
		index is 0 if caluclating for volatility, 1 if calculating for volume"""
	def updateSkewness(self, index):
		currentList = self.collectRecordedValues(index)
		self.updateMean(index, currentList)
		self.updateStdDev(index, currentList)

		#skewness = m_3 / (m_2)^(3/2) ***m2 is just std deviation squared
		#m_3 = sigma [ (x - x_bar)^3 ] / n
		m_3Num = 0.0
		m_3Denom = len(currentList)
		for x in currentList:
			m_3temp = x - self.means[index] # x - x_bar
			m_3temp **= 3 #(x - x_bar)^3
			m_3Num += m_3temp #sigma (x - x_bar)^3
		m3 = m_3Num / m_3Denom
		m2 = self.stdDevs[index] ** 2 #m2 = stdDev^2
		m2 **= Fraction('3/2')
		#skewness is m3/m2
		self.skewness[index] =  m3 / m2

	"""standard normal distribution has a kurtosis of 0
	positive kurtosis indicates a 'heavy-tailed' distribution and
	negative kurtosis indicates a 'light-tailed' distrubution
	index is 0 if calculating for volatility, 1 if calc for volume"""
	def updateKurtosis(self, index):
		#Need to obtain the list of values for either volatility or volume for calcs
		currentList = self.collectRecordedValues(index)
		#Need to update our mean and stdDev
		self.updateMean(index, currentList)
		self.updateStdDev(index, currentList)

		num = 0.0 #sigma [(x - x_bar)^4] / n
		for x in currentList:
			num_temp = x - self.means[index]
			num_temp **= 4
			num += num_temp
		num /= len(currentList)
		denom = self.stdDevs[index] ** 4  ## denom = stdDev^4
		self.kurtosis[index] = num / denom

	def __str__(self):
		return self.symbol