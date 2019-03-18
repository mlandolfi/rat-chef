from alpha_vantage.timeseries import TimeSeries

API_KEY = "878U8SIR8IMVPVQ6"

ts = TimeSeries(key=API_KEY)

data, metaData = ts.get_intraday('GOOGL')

print (data)