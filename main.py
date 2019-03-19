# https://github.com/RomelTorres/alpha_vantage	<--- the docs for alpha vantage wrapper
from alpha_vantage.timeseries import TimeSeries
import time
import datetime

from Stocks import Stock

# Constants
API_KEY = "878U8SIR8IMVPVQ6"


# main function starting point
def main():

	googleStock = Stock('GOOGL', 'googleValues.txt')


	# boiler plate for getting data
	# ts = TimeSeries(key=API_KEY)
	# data, metaData = ts.get_intraday(symbol="GOOGL", interval="1min")
	# for dataKey in data:
	# 	googleStock.addValueToday(dataKey.split(" ")[1], data[dataKey]["4. close"], data[dataKey]["5. volume"])
	# 	# print (dataKey, data[dataKey])
	# googleStock.saveValues()
	googleStock.readValues()
	for key, value in googleStock.values.items():
		print (key, value)


# runs the main() function
if __name__ == "__main__":
	main()



######## Notes ########
"""

Gmail
UN: ratchefbois@gmail.com
PW: ratchef123
DOB: Jan 1, 1990

Twitter
@Chef33732825
PW: ratchef123

Sample output from:
	ts = TimeSeries(key=API_KEY)
	data, metaData = ts.get_intraday(symbol="GOOGL", interval="5min")

{
	'2019-03-18 14:15:00': {
		'1. open': '1189.3900',
		'2. high': '1189.7550',
		'3. low': '1188.7000',
		'4. close': '1189.6600',
		'5. volume': '19597'
	},
	'2019-03-18 14:00:00': {
		'1. open': '1187.8325',
		'2. high': '1189.3900',
		'3. low': '1187.5300',
		'4. close': '1189.1700',
		'5. volume': '14637'
	},
	'2019-03-18 13:45:00': {
		'1. open': '1185.8022',
		'2. high': '1188.2921',
		'3. low': '1185.8022',
		'4. close': '1188.1617',
		'5. volume': '28254'
	}
}



"""