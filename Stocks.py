# file to hold stocks class to store stock data
import json
import datetime
import statistics
import math
import numpy as np
from cryptoDataCollection import getData
from fractions import Fraction
from scipy.stats import iqr

#TODO: stop using statistics class for calculations, maybe pass currentList for populations?
""" notes
Skewness:
https://brownmath.com/stat/shape.htm
when the plot is extended towards the right side more, it denotes positive skewness, wherein mode < median < mean. 
On the other hand, when the plot is stretched more towards the left direction, 
then it is called as negative skewness and so, mean < median < mode.

any symmetric data should have a skewness near zero. 
Negative values for the skewness indicate data that are skewed left (longer tail on left side of graph)
and positive values for the skewness indicate data that are skewed right. (longer tail on right side of graph)

Kurtosis: Measure of the peak of the graph
sample: https://en.wikipedia.org/wiki/Kurtosis#Sample_kurtosis
population: https://www.itl.nist.gov/div898/handbook/eda/section3/eda35b.htm

"""

class Stock(object):

	def __init__(self, ticker):
		self.ticker = ticker
		self.record = getData(self.ticker)	# key is date, value is {key = time, value (value, volume) }
		self.lastValueRecorded = 0#tuple of (value, volume, time)
		self.dailyValuesInXY = False

		#POPULATION fields
		self.populationLists = [[],[]] #first list is all recorded values, second list is all recorded volumes (same as record, different data structure used in statistics class)
		self.doesPopListNeedToBeUpdated = True #True when an entry has been added and the populationLists need to be updated bc of that entry
		self.popMeans = [0.0, 0.0] #(volatility, volume) -> means of all recorded volatilities and volumes, including today
		self.popStdDevs = [0.0, 0.0] #(volatility, volume) -> numerical value used to indicate how widely individuals in a group vary. If individual observations vary greatly from the group mean, the standard deviation is big; and vice versa.
		self.popZScores = [0.0, 0.0] #(volatility, volume) -> z-score indicates how many standard deviations an element is from the mean, see website in notes for more info
		self.popSkewness = [0.0, 0.0] #(volatility, volume) skewness is a measure of the asymmetry of the probability distribution of a real-valued random variable about its mean
		self.popKurtosis = [0.0, 0.0] #(volatility, volume) the sharpness of the peak of a frequency-distribution curve.
		self.popRange = [0.0, 0.0] #(volatility, volume) the lowest number in the data set subtracted by the highest
		self.popIQR = [0.0, 0.0]
		self.popCorrCoeff = 0.0  #correlation coefficient between values and volumes
	""" ############################ Functions that work with our data files ############################ """
	
	""" adds a time and value into self.record if it isn't already in there,
		also sets the self.lastValueRecorded to a tuple of (value, volume, time)
		if it's from a previous day it adds it to the previous day
		Untested """
	def addValue(self, time, value, volume, day):
		if (not day in self.record.keys()):
			self.record[day] = {}
		if (not time in self.record[day].keys()):
			self.record[day][time] = (value, volume)
		self.lastValueRecorded = (value, volume, time)
		self.doesPopListNeedToBeUpdated = True

	def getValue(self, when, index=0):
		dateKey = when.isoformat().split("T")[0]
		timeKey = when.isoformat().split("T")[1]
		if (not dateKey in self.record.keys() or not timeKey in self.record[dateKey].keys()):
			return None
		return self.record[dateKey][timeKey][index]

	""" returns a list of the daily values in (x,y) format where x is time ex. 9.55
		and y is the value of the stock at that time
		if this hasn't been called yet then it'll set self.dailyValuesInXY so it
		won't have to recalculate it next time
		Untested """
	def getDailyValuesInXY(self):
		if (self.dailyValuesInXY):	return self.dailyValuesInXY
		xyValues = []

		today = datetime.datetime.today()
		#making the seconds and microseconds 0 bc we don't use those
		today = datetime.datetime(today.year, today.month, today.day, today.hour, today.minute, 0, 0)

		if self.record.get(today) != None:
			for time in self.record[today]:
				xValue = float(time.split(":")[0] + "." + time.split(":")[1])
				xyValues.append((xValue, self.record[today][time][0]))
			self.dailyValuesInXY = xyValues
			return xyValues
		else:
			return (0,0)
		

	""" ############################ Helper functions for update functions ############################ """

	"""Given an endDate (datetime.datetime object), we calculate the startDate by
		going back (numMinutes + numHours + numDays) amount of time.

		Returns startDate, ie, 3-14-2019 4:32:00, where endDate would be a later date, such as 3-15-2019 4:32:00
		Tested
		"""
	def calculateStartDate(self, endDate, numMinutes, numHours, numDays):
		#Ensuring the seconds and microseconds are 0 for endDate because we store them like this in record
		endDate = datetime.datetime(endDate.year, endDate.month, endDate.day, endDate.hour, endDate.minute, 0, 0)
		minutes = datetime.timedelta(minutes=numMinutes)
		hours = datetime.timedelta(hours=numHours)
		days = datetime.timedelta(days=numDays)

		startDate = endDate - days - hours - minutes

		return startDate


	"""Starting at a given date, goes back numMinutes + numHours + numDays amount of time, 
		then returns the data for values (if index is 0) or data for volumes (if index is 1)
		
		endDate (datetime.datetime object), the date we want to start going back from (for current time, pass
		in #today = datetime.datetime.today())
		interval (int), is how often we want to collect data, ie, interval = 5 means get a data point
		once every 5 minutes

		***Note: if there is no data point, we will not attempt to go further back in time to add more data,
		we simply collect everything we can going back numMinutes + numHours + numDays amt of time
		***
		Tested
		"""
	def getSampleList(self, index, startDate, endDate, interval):
		retList = []
	
		tempEndDate = endDate + datetime.timedelta(minutes=0) - datetime.timedelta(minutes=0)
		timeDecrement = datetime.timedelta(minutes=interval)

		if tempEndDate < startDate:
			print("Error: endDate < startDate in getSampleList")
			return None
		else:
			while tempEndDate >= startDate:
				currentDate = tempEndDate.strftime('%Y-%m-%d') #year - month - date 
				if self.record.get(currentDate) != None:
					currentTimeStamp = tempEndDate.strftime('%H:%M:00') #Hour: Minute: 00
					if self.record.get(currentDate).get(currentTimeStamp) != None:
						retList.append(self.record[currentDate][currentTimeStamp][index])
				tempEndDate = tempEndDate - timeDecrement

		return retList

	""" returns a list containing all recorded values for this stock if index is 0, 
		or all recorded volumes for this stock if index is 1
		Tested
		"""
	def getPopulationList(self, index):
		retList = []
		#going through all of our past day recorded volumes
		for day in self.record:
			for time in self.record[day]:
				retList.append(self.record[day][time][index])

		return retList

	""" ############################ Update stock functions ############################ """

	""" ############## Sample Calculations ############# """

	"""Returns the sample mean from current time back to (numMinutes + numHours + numDays), with
		data collected every (interval) number of minutes. 
		index 0 for values, 1 for volumes
		sampleList (list of values or list of volumes), obtained from getPopulationList(index)
		Tested
		"""
	def getSampleMean(self, sampleList):
		return statistics.mean(sampleList)

	"""Returns the sample std dev, same logic as getSampleMean
		index 0 for values, 1 for volumes
		sampleList (list of values or list of volumes), obtained from getPopulationList(index)
		Tested
		"""
	def getSampleStdDev(self, sampleList):
		return statistics.stdev(sampleList)

	"""Returns sample zScore for x, where x is passed in as an argument. x will
		typically be the current value or current volume, but doesn't need to be.
		index 0 for values, 1 for volumes
		sampleList (list of values or list of volumes), obtained from getPopulationList(index)
		sampleMean and sampleStdDev obtained from getSampleMean() and getSampleStdDev()
		Tested
		"""
	def getSampleZScore(self, x, sampleList, sampleMean, sampleStdDev):
		if sampleStdDev == 0:
			print("Error: sampleStdDev is 0 in getSampleZScore")
			return 0
		else:
			return ((x - sampleMean) / float(sampleStdDev))

	#From brownMath
	def getSampleSkewness(self, sampleList, sampleMean, sampleStdDev):
		n = len(sampleList)
		s = sampleStdDev
		if (s == 0):	return 0
		x_bar = sampleMean

		m_3Num = 0.0
		for x in sampleList:
			m_3temp = x - x_bar # x - x_bar
			m_3temp **= 3 #(x - x_bar)^3
			m_3Num += m_3temp #sigma (x - x_bar)^3
		m3 = m_3Num / n
		m2 = s ** 2 #m2 = stdDev^2
		m2 **= Fraction('3/2')
		#skewness is m3/m2
		g_1 =  m3 / m2
		multVar = (n*(n-1))**0.5
		multVar /= (n-2)
		g_1 *= multVar
		return g_1


	"""From brownMath"""
	def getSampleKurtosis(self, sampleList, sampleMean, sampleStdDev):
		n = len(sampleList)
		m2 = sampleStdDev ** 4
		if (m2 == 0):	return 0
		
		m4 = 0.0
		for x in sampleList:
			tempM4 = x - sampleMean
			tempM4 **= 4
			m4 += tempM4
		m4 /= n
		g2 = float(m4/m2) - 3

		multVar = (n-1)/((n-2)*(n-3))
		retVal = multVar*(((n+1)*g2) + 6)
		return retVal

	#From endDate, goes back until it finds the most recent data point 
	def obtainXForZScore(self, index, startDate, endDate, interval):
		retVal = 0

		timeDecrement = datetime.timedelta(minutes=interval)
		tempEndDate = endDate + datetime.timedelta(minutes=1) - datetime.timedelta(minutes=1)

		if tempEndDate < startDate:
			print("Error: in obtainXForZScore, endDate<startDate")
		else:
			while tempEndDate >= startDate:
				currentDate = tempEndDate.strftime('%Y-%m-%d') #year - month - date 
				if self.record.get(currentDate) != None:
					currentTimeStamp = tempEndDate.strftime('%H:%M:00') #Hour: Minute: 00
					if self.record.get(currentDate).get(currentTimeStamp) != None:
						return self.record[currentDate][currentTimeStamp][index]
				tempEndDate = tempEndDate - timeDecrement
		return retVal

	#Get the range from
	def getSampleRange(self, sampleList):
		lowest = math.inf
		highest = -math.inf
		for x in sampleList:
			if x < lowest:
				lowest = x
			if x > highest:
				highest = x
		if lowest == math.inf or highest == math.inf:
			return 0.0
		else:
			return (highest - lowest)

	#IQR is the difference between the 75th and 25th percentiles of data
	def getSampleIQR(self, sampleList):
		if len(sampleList) == 0:
			return 0
		
		x = np.array(sampleList)
		return iqr(x, rng=(25,75), interpolation='midpoint')

	#Generic function to return correlation coefficient between two sets of data, (ex, volume and volatility)
	def getSampleCorrCoef(self, sampleListOne, sampleListTwo):
		if len(sampleListOne) == 0 or len(sampleListTwo) == 0:
			return 0

		x = np.array(sampleListOne)
		y = np.array(sampleListTwo)
		corrCoef = np.corrcoef(x, y)[1,0] #corrCoef returns a matrix
		return corrCoef

	def getAllSampleValues(self, index, endDate, numMinutes, numHours, numDays, interval):
		retList = []
		startDate = self.calculateStartDate(endDate, numMinutes, numHours, numDays)
		sampleList = self.getSampleList(index, startDate, endDate, interval)
		otherList = self.getSampleList(0, startDate, endDate, interval) if index == 1 else self.getSampleList(1, startDate, endDate, interval)

		if len(sampleList) is 0:
			return [0, 0, 0, 0, 0, 0, 0, 0]
		
		mean = self.getSampleMean(sampleList)
		stdDev = self.getSampleStdDev(sampleList)
		#getting z-scores from last recorded value, returns 0 if theres no data
		x = self.obtainXForZScore(index, startDate, endDate, interval)
		zScore = self.getSampleZScore(x, sampleList, mean, stdDev)
		skewness = self.getSampleSkewness(sampleList, mean, stdDev)
		kurtosis = self.getSampleKurtosis(sampleList, mean, stdDev)
		rng = self.getSampleRange(sampleList)
		iqr = self.getSampleIQR(sampleList)
		corrCoef = self.getSampleCorrCoef(sampleList, otherList)

		retList.append(mean)
		retList.append(stdDev)
		retList.append(zScore)
		retList.append(skewness)
		retList.append(kurtosis)
		retList.append(rng)
		retList.append(iqr)
		retList.append(corrCoef)

		return retList

	""" ############## Population Calculations ############# """

	"""updates the list of all values and the list of all volumes used in all population calculations
		if an entry has been added
		Tested
		 """
	def updatePopList(self):
		if self.doesPopListNeedToBeUpdated is True:
			self.doesPopListNeedToBeUpdated = False
			self.populationLists[0] = self.getPopulationList(0)
			self.populationLists[1] = self.getPopulationList(1)

	"""Updates the population mean (all recorded items, from today and past). index 0 for values, 1 for volumes"""
	def updatePopMean(self, index):
		self.updatePopList()
		self.popMeans[index] = statistics.mean(self.populationLists[index])

	"""Updates the population std dev (all recorded items, from today and past). index 0 for values, 1 for volumes"""
	def updatePopStdDev(self, index):
		self.updatePopList()
		self.popStdDevs[index] = statistics.pstdev(self.populationLists[index])

	"""Requires that updateMeans/updatePopStdDev have both been called, in that order, and that
		lastValueRecorded has values.
		Updates the population z-score for this stock. 

		x is the value we want to compute the zscore for, ie, x = self.lastValueRecorded[index] gives us the
		zscore for the most current entry compared against all time

		index is 0 if we are finding z-score of values (for volatility), 1 if z-score of volumes"""
	def updatePopZScore(self, index, x):
		#z = (X - μ) / σ, where X is latest recorded value, μ is the population mean, and σ is the standard deviation
		self.updatePopList()
		if self.popStdDevs[index] is 0:
			print("Error: dividing by 0 using stdDevs[", index, "]")
			self.popZScores[index] = 0
		else:
			self.popZScores[index] = (x - self.popMeans[index]) / self.popStdDevs[index]

	"""Requires that updateMeans/updatePopStdDev have both been called
		skewness of a normal distribution is 0
		negative values for skewness indicate that the data is skewed left
		positive values for skewness indicate that the data is skewed right
		index is 0 if calculating for volatility, 1 if calculating for volume"""
	def updatePopSkewness(self, index):
		#skewness = m_3 / (m_2)^(3/2) ***m2 is just std deviation squared
		#m_3 = sigma [ (x - x_bar)^3 ] / n
		self.updatePopList()
		m_3Num = 0.0
		m_3Denom = len(self.populationLists[index])
		for x in self.populationLists[index]:
			m_3temp = x - self.popMeans[index] # x - x_bar
			m_3temp **= 3 #(x - x_bar)^3
			m_3Num += m_3temp #sigma (x - x_bar)^3
		m3 = m_3Num / m_3Denom
		m2 = self.popStdDevs[index] ** 2 #m2 = stdDev^2
		m2 **= Fraction('3/2')
		#skewness is m3/m2

		self.popSkewness[index] =  m3 / m2

	"""Requires that updateMeans/updatePopStdDev have both been called
	standard normal distribution has a kurtosis of 0
	positive kurtosis indicates a 'heavy-tailed' distribution and
	negative kurtosis indicates a 'light-tailed' distribution
	index is 0 if calculating for volatility, 1 if calc for volume"""
	def updatePopKurtosis(self, index):
		#Need to obtain the list of values for either volatility or volume for calcs
		self.updatePopList()
		num = 0.0 #sigma [(x - x_bar)^4] / n
		for x in self.populationLists[index]:
			num_temp = x - self.popMeans[index]
			num_temp **= 4
			num += num_temp
		num /= len(self.populationLists[index])
		denom = self.popStdDevs[index] ** 4  ## denom = stdDev^4
		self.popKurtosis[index] = (num / denom) - 3 #the 3 is so perfect normal distr = 0


	def updatePopRange(self, index):
		self.updatePopList()
		lowest = math.inf
		highest = -math.inf
		for x in self.populationLists[index]:
			if x < lowest:
				lowest = x
			if x > highest:
				highest = x
		if lowest == math.inf or highest == math.inf:
			self.popRange[index] = 0.0
		else:
			self.popRange[index] = highest - lowest

	#very slow
	def updatePopIQR(self, index):
		self.updatePopList()
		
		x = np.array(self.populationLists[index])
		self.popIQR[index] = iqr(x, rng=(25,75), interpolation='midpoint')

	#very slow
	def updatePopCorrCoef(self):
		self.updatePopList()

		x = np.array(self.populationLists[0])
		y = np.array(self.populationLists[1])
		corrCoef = np.corrcoef(x, y)
		self.popCorrCoeff = corrCoef

	def __str__(self):
		return self.ticker