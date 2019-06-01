import time

class Tracer(object):

	def __init__(self, keyString):
		self.initializeValues()
		self.keyString = keyString

	def initializeValues(self):
		self.startTime = None
		self.lastTime = None

		self.predictions = []
		self.actual = []

		self.posPredictions = 0
		self.posCorrectPredictions = 0
		self.posActual = 0
		self.negPredictions = 0
		self.negCorrectPredicitons = 0
		self.negActual = 0

	# timeStamp should be a string
	def trace(self, predicted, actual, timeStamp):
		if (self.startTime == None):	self.startTime = timeStamp
		self.lastTime = timeStamp

		self.predictions.append(predicted)
		self.actual.append(actual)

		self.posPredictions += 1 if predicted > 0 else 0
		self.negPredictions += 1 if predicted < 0 else 0

		self.posActual += 1 if actual > 0 else 0
		self.negActual += 1 if actual < 0 else 0

		if (predicted > 0 and actual > 0):
			self.posCorrectPredictions += 1
		if (predicted < 0 and actual < 0):
			self.negCorrectPredicitons += 1

	def print(self):
		print ('#'*45+'\n')

		print ('Results for: {}'.format(self.keyString))
		print ('From {} - {}\n'.format(self.startTime, self.lastTime))

		print ('{0:25}{1:10}'.format('total Guesses:', self.posPredictions+self.negPredictions))
		print ('{0:25}{1:10}\n'.format('total correct guesses', self.negCorrectPredicitons+self.posCorrectPredictions))

		print ('+'*25+'>0+'+'+'*25)
		print ('{0:25}{1:10}'.format('correct predictions:', self.posCorrectPredictions))
		print ('{0:25}{1:10}'.format('predictions:', self.posPredictions))
		print ('{0:25}{1:10}'.format('actual:', self.posActual))
		print ('+'*25+'>0+'+'+'*25+'\n')
		
		print ('-'*25+'<0+'+'-'*25)
		print ('{0:25}{1:10}'.format('correct predictions:', self.negCorrectPredicitons))
		print ('{0:25}{1:10}'.format('predictions:', self.negPredictions))
		print ('{0:25}{1:10}'.format('actual:', self.negActual))
		print ('-'*25+'<0'+'-'*25+'\n')

