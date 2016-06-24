from datetime import datetime

def DatetimeToUnixTime(dt):
	epoch = datetime.utcfromtimestamp(0)
	return (dt - epoch).total_seconds()

def UnixTimeToDatetime(seconds):
	return datetime.utcfromtimestamp(seconds)