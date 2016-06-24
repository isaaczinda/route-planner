import sys
import os
from collections import defaultdict
import math
import os
import Array
import re
import Time
import Geography
import Geometry
from datetime import datetime
import time
import json

class Map:
	def __init__(self, Filename):
		# deal with the filepath
		self.ModuleDirectory = os.path.dirname(os.path.abspath(__file__))

		self.Filepath = os.path.join(self.ModuleDirectory, Filename)
	

		Lines = []

		with open(self.Filepath) as f:
		    Lines = f.readlines()

		self.Data = defaultdict(list)

		for Line in Lines:

			# remove newline characters
			Line = Line.replace("\n", "")

			# split the line about the commas
			Values = Line.split(",")

			try:
				# make all of the indexes integers
				LatLonAlt = (round(float(Values[0]) * 2), round(float(Values[1]) * 2), int(Values[2]))

				WindDirection = float(Values[3])
				WindSpeed = float(Values[4])

				self.Data[LatLonAlt] = [WindDirection, WindSpeed]
			except:
				# if there isn't complete data for a line, write zeroes
				self.Data[LatLonAlt] = [0.0, 0.0]
				print "incomplete recorded data at", LatLonAlt


	def RoundPosition(self, Position):
		# scale the input points
		DoubleLatitude = Position[0] * 2
		DoubleLongitude = Position[1] * 2

		# rounds to the nearest .5
		RoundedLatitude = round(DoubleLatitude)

		# rounds to the nearest .5
		RoundedLongitude = round(DoubleLongitude)

		return [int(RoundedLatitude), int(RoundedLongitude)]



	# rounds an altitude to one of the accepted ones
	def RoundAltitude(self, InputAltitude):
		PossibleAltitudes = [6000, 9000, 12000, 18000, 24000, 30000, 34000, 39000]
		Differences = []

		for i in range(0, len(PossibleAltitudes)):
			PossibleAltitude = PossibleAltitudes[i]

			Differences.append([abs(PossibleAltitude - InputAltitude), i])

		ClosestAltitudeIndex = sorted(Differences, key=Array.itemgetter(0))[0][1]
		
		return PossibleAltitudes[ClosestAltitudeIndex]


	def WindAtPosition(self, Position, Altitude):
		Position = self.RoundPosition(Position)
		Altitude = self.RoundAltitude(Altitude)
		
		# convert data from tuple to array
		WindData = self.Data[(Position[0], Position[1], Altitude)]
		
		# if it is a list, has length 2, and is an int
		if isinstance(WindData, list):
			if len(WindData) == 2:
				if isinstance(WindData[0], float) and isinstance(WindData[1], float):
					return WindData

		# if nothing is returned, the position data was incorrect 
		raise LookupError("Lat/Lon position out of range.")


class Report:
	def __init__(self):
		self.ModuleDirectory = os.path.dirname(os.path.abspath(__file__))
		self.FlightAccessPath = os.environ.get("FLIGHTACCESSPATH")

		WindReportsPath = os.path.join(self.ModuleDirectory, "..", "wind-reports")
	
		# create a global waypoint array
		self.Waypoints = self.__Parse(WindReportsPath, os.listdir(WindReportsPath))
		self.Waypoints.extend(self.WaypointsFromFile(os.path.join(self.FlightAccessPath, "wind-reports.json")))

	def WaypointsFromFile(self, Filepath):
		with open(Filepath, 'r') as f:
			return json.loads(f.read())

	def __RoundPosition(self, Position):
		Step = .5
		return (int(Position[0] / Step) * Step, int(Position[1] / Step) * Step)

	def GroupWaypoints(self, Waypoints):
		WaypointDictionary = {}

		Overlap = 0
		New = 0

		# round all positions to the nearest step 
		for Waypoint in Waypoints:
			RoundedPosition = self.__RoundPosition(Waypoint["Position"])

			if RoundedPosition not in WaypointDictionary:
				WaypointDictionary[RoundedPosition] = Waypoint
				New += 1
			else:
				Overlap += 1			

		ReturnWaypoints = []

		for Key in WaypointDictionary:
			ReturnWaypoints.append(WaypointDictionary[Key])

		return ReturnWaypoints

	def SurroundingRegion(self, Point, UTCTimestamp, MaxDistanceDifference=100, Above25000=True):
		Return = []

		for Waypoint in self.Waypoints:
			DistanceToWaypointKilometers = Geography.DistanceBetweenPoints(Waypoint["Position"], Point)

			# if the time difference is < 1 hour, the distance is < 50, and the altitude is > 25000
			if ((Above25000 and Waypoint["Altitude"] > 25000) or (not Above25000 and Waypoint["Altitude"] < 25000)) and DistanceToWaypointKilometers <= MaxDistanceDifference and abs(UTCTimestamp - Waypoint["Timestamp"]) < 3600:
				WindVector = Geometry.VectorFromSpeedBearing(Waypoint["WindSpeed"], Waypoint["WindDirection"])
				Return.append(WindVector)

		return Return

	def TimeFrame(self, TargetDatetime):
		Return = []

		TargetSecond = Time.DatetimeToUnixTime(TargetDatetime)

		for Waypoint in self.Waypoints: # makes sure that none of the waypoints are too close
			# converts the timestamp to a PST timestamp 
			PSTSecond = Waypoint["Timestamp"] - (7 * 3600)

			if TargetSecond - PSTSecond <= 3600 and TargetSecond - PSTSecond >= 0:
				Return.append(Waypoint)

		return Return # no longer call self.GroupWaypoints()

	def LowSpeedReadings(self):
		FlightNumbers = []

		# get every waypoint with certain unexpected characteristics
		for Waypoint in self.Waypoints:
			if int(Waypoint["Altitude"]) > 30000 and Waypoint["WindSpeed"] < 10:
				FlightNumbers.append(Waypoint["FlightNumber"])

		# remove preceeding zeroes
		FlightNumbers = [str(int(i)) for i in FlightNumbers]

		return set(FlightNumbers)


	def __Parse(self, BaseFilepath, Files):
		WindObjects = []

		for DataFile in Files:
			# read all lines into an array 
			Lines = []
			with open(os.path.join(BaseFilepath, DataFile), 'r') as WindspeedFile:
				Lines = WindspeedFile.readlines()

			# different modes for the state machine
			Mode = "meta"
			Index = 0
			FlightObject = {}


			for i in range(0, len(Lines)):
				Line = Lines[i].replace("\n", "")

				# always add 1 to the index
				Index += 1

				# changes in the state machine occur here
				if "CPYXXXX" in Line:
					Mode = "meta"
					Index = 0
					FlightObject = {}

				if Mode == "meta" and "-  " in Line:
					Mode = "specs"
					Index = 0

				if Mode == "specs" and Index == 1:
					Mode = "wind"
					Index = 0

				if Line == "":
					Mode = "wait"
					Index = 0


				# change different variables based on the state
				if Mode == "meta" and Index == 3:
					LineArray = Line.split(" ")
					FlightObject["Aircraft"] = LineArray[2]
					FlightObject["FlightNumber"] = LineArray[1][2:].replace("/AN", "")

				if Mode == "specs":
					if "WT" in Line:
						FlightObject["Day"] = int(Line[9:11])
						FlightObject["Hour"] = int(Line[11:13])
					elif "FE" in Line:
						DateString = Line.split("FE")[1]
						FlightObject["Day"] = int(DateString[0:2])
						FlightObject["Hour"] = int(DateString[5:7])
					else:
						Mode = "wait"
						# set the mode to "wait" so that nothing happens until the next clump of data

				if Mode == "wind":
					FormattedLine = Line.replace("/", "")
					LettersInLine = re.search('[a-zA-Z]', FormattedLine)

					# set all of the vars to none
					HHMMSS, Latitude, Longitude, Altitude, StaticAirTemperature, WindDirection, WindSpeedKnots, Rolf, DataSource = [None for i in range(0, 9)]

					if len(FormattedLine) == 33:
						HHMMSS = FormattedLine[0:6]
						Latitude = FormattedLine[7:9] + "." + FormattedLine[9:11]

						# make the longitude negative here because we are removing the W 
						Longitude = "-" + FormattedLine[12:15] + "." + FormattedLine[15:17]
						Altitude = FormattedLine[17:22]
						StaticAirTemperature = FormattedLine[22:25] + "." + FormattedLine[25]
						WindDirection = FormattedLine[26:29]
						WindSpeedKnots = FormattedLine[29:32]
						Rolf = FormattedLine[32]
						DataSource = "boeing"
					
					elif len(FormattedLine) == 38 and LettersInLine == None:
						HHMMSS = FormattedLine[0:6]
						Latitude = FormattedLine[6:9] + "." + FormattedLine[9:13]
						Longitude = FormattedLine[13:17] + "." + FormattedLine[17:21]

						Altitude = FormattedLine[21:27]
						StaticAirTemperature = FormattedLine[27:30] + "." + FormattedLine[30]
						WindDirection = FormattedLine[31:34]
						WindSpeedKnots = FormattedLine[34:37]
						Rolf = FormattedLine[37]
						DataSource = "airbus"
					else:
						pass
						#print "didn't know what to do with this line: " + FormattedLine

					if HHMMSS != None:
						# do time conversions
						Days = FlightObject["Day"]
						Hours = HHMMSS[0:2]
						Minutes = HHMMSS[2:4]
						Seconds = HHMMSS[4:6]
						DateTimeString = str(Days) + "/04/16 " + Hours + ":" + Minutes + ":" + Seconds
						date_object = datetime.strptime(DateTimeString, '%d/%m/%y %H:%M:%S')

						try:
							WindObjects.append({"AircraftId": FlightObject["Aircraft"], "Raw": Line, "Timestamp": float(str(Time.DatetimeToUnixTime(date_object))), "FlightNumber": FlightObject["FlightNumber"], "Position": [float(Latitude), float(Longitude)], "Altitude": int(Altitude), "Temperature": float(StaticAirTemperature), "WindDirection": int(WindDirection), "WindSpeed": int(WindSpeedKnots)})					
						except Exception, e:
							print e
							pass

		return WindObjects