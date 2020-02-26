import datetime
import random

class Order(object):

	def __init__(self, orderId, timePlaced, exitTime, orderType, side, productId, enterAmount, startPrice):
		self.id = orderId
		self.timePlaced = timePlaced
		self.exitTime = exitTime
		self.type = orderType
		self.side = side
		self.productId = productId
		self.enterAmount = enterAmount
		self.size = enterAmount / startPrice
		self.lowerSellPrice = 0
		self.upperSellPrice = 1000000

	def setPriceBounds(self, currentPrice, spread, bullPrediction=1, bearPrediction=1):
		self.lowerSellPrice = currentPrice - (bearPrediction * spread)
		self.upperSellPrice = currentPrice + (bullPrediction * spread)

	def getProfits(self, exitPrice):
		return self.enterAmount - self.size*exitPrice

	def getWorth(self, exitPrice):
		return self.size*exitPrice

	def shouldExit(self, currentPrice, currentTime):
		if (currentTime >= self.exitTime):
			return True
		if (currentPrice >= self.upperSellPrice):
			return True
		# if (currentPrice <= self.lowerSellPrice):
		# 	return True
		return False


class Simulator(object):

	def __init__(self, stock, startAmount, buyAmount, startDate, predictionTimeDelta):
		self.stock = stock
		self.orderPool = []
		self.currentDate = startDate
		self.cash = startAmount
		self.buyAmount = buyAmount
		self.exitDelta = predictionTimeDelta
		# variables
		self.volatility = 0.05
		self.orderTotalAtLastBuy = 0
		# report vars
		self.prevTotal = 0
		self.prevCash = 0
		self.prevOrderCount = 0

	def placeBuyOrder(self):
		if (self.buyAmount > self.cash):
			return False
		order = Order(random.randint(1, 1000000), self.currentDate, self.currentDate+self.exitDelta,'limit', 'buy', 'BTC-USD', self.buyAmount, self.stock.getValue(self.currentDate))
		currentPrice = self.stock.getValue(self.currentDate)
		order.setPriceBounds(currentPrice, self.volatility*currentPrice)
		self.orderPool.append(order)
		self.cash -= self.buyAmount
		print ("Simulator: placed BUY order for ${}".format(self.buyAmount))
		self.orderTotalAtLastBuy = self.countOrders()
		# print ("Simulator: ${} in cash".format(self.cash))
		return True

	def placeSellOrder(self, orderId):
		for i in range(len(self.orderPool)):
			if (self.orderPool[i].id == orderId):
				soldOrder = self.orderPool.pop(i)
				self.cash += soldOrder.getWorth(self.stock.getValue(self.currentDate))
				print ("Simulator: placed SELL order for {}".format(soldOrder.id))
				# print ("Simulator: ${} in cash".format(self.cash))
				return True
		return False

	def ordersUpSinceBuy(self, offset=1):
		total = 0
		for order in self.orderPool:
			total += order.getWorth(self.stock.getValue(self.currentDate))
		return total > self.orderTotalAtLastBuy+offset

	def exitOrders(self, numOrders):
		for i in range(numOrders):
			self.placeSellOrder(self.orderPool[i].id)

	def scanOrders(self):
		total = 0
		for order in self.orderPool:
			if (order.shouldExit(self.stock.getValue(self.currentDate), self.currentDate)):
				self.placeSellOrder(order.id)
			else:
				total += order.getWorth(self.stock.getValue(self.currentDate))
		# if (self.ordersUpSinceBuy(3)):
		# 	self.exitOrders(len(self.orderPool)//3)
		# print ("Simulator: scanned orders and counted ${} + ${} in cash = ${}".format(total, self.cash, total+self.cash))

	def countOrders(self):
		total = 0
		for order in self.orderPool:
			total += order.getWorth(self.stock.getValue(self.currentDate))
		return total

	def processPrediction(self, prediction, currentDate):
		self.currentDate = currentDate
		# print (currentDate)
		if (prediction > 0):
			self.placeBuyOrder()
		self.scanOrders()

	def sellAll(self, currentDate):
		total = 0
		for order in self.orderPool:
			total += order.getWorth(self.stock.getValue(currentDate))
		print ("Simulator: sold all active orders for ${} + ${} in cash = ${}".format(total, self.cash, total+self.cash))

	def report(self):
		ordersCount = self.countOrders()
		totalAssets = ordersCount + self.cash
		# if (ordersCount == self.prevOrderCount or totalAssets == self.prevTotal or self.cash == self.prevCash):
		# 	return
		print ("\nTOTAL:  {0:12.2f} {1}".format(totalAssets, '|'*100))
		ordersBars = int(round(ordersCount / totalAssets, 2) * 100)
		cashBars = int(round(self.cash / totalAssets, 2) * 100)
		print ("CASH:   {0:12.2f} {1}".format(self.cash, '|'*cashBars))
		print ("ORDERS: {0:12.2f} {1}".format(ordersCount, '|'*ordersBars))
		self.prevOrderCount = ordersCount
		self.prevCash = self.cash
		self.prevTotal = totalAssets



class RepeatPredictor(Simulator):

	def __init__(self, numRepeats, *args):
		super(RepeatPredictor, self).__init__(*args)
		self.numRepeats = numRepeats
		self.repeatCount = 0
		# exit variables
		self.sellOnUp = False

	def processPrediction(self, prediction, currentDate):
		self.currentDate = currentDate
		self.scanOrders()
		self.report()
		if (prediction <= 0):
			self.repeatCount = 0
			return
		self.repeatCount += 1
		if (self.repeatCount >= self.numRepeats):
			self.placeBuyOrder()



class PMAPredictor(Simulator):

	def __init__(self, *args):
		super(PMAPredictor, self).__init__(*args)
		self.numPosPredictions = 0
		self.predictionPosTotal = 0
		self.pma = 0

	def processPrediction(self, prediction, currentDate):
		self.currentDate = currentDate
		self.scanOrders()
		self.report()
		if (prediction < 0):
			return
		if (prediction > self.pma):
			self.placeBuyOrder()
			self.placeBuyOrder()
			self.placeBuyOrder()
		else:
			self.placeBuyOrder()
		self.numPosPredictions += 1
		self.predictionPosTotal += prediction
		self.pma = self.predictionPosTotal // self.numPosPredictions





		