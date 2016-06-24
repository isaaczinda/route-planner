from geographiclib.geodesic import Geodesic
import json
import os
import math
import Array
import time
# import numpy as np

# store where this module is actually located
ModuleDirectory = os.path.dirname(os.path.abspath(__file__))

# import the airport data from its json file
AirportData = []

def BearingBetweenWaypoints(pointA, pointB):
    pointA = (pointA[0], pointA[1])
    pointB = (pointB[0], pointB[1])

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180 to + 180 which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

def KilometersToMiles(Kilometers):
	return 0.621371 * Kilometers

def WaypointObjectToArray(Obejct):
	return [Obejct["Lat"], Obejct["Lon"]]

# returns [Latitude, Longitude]
def AirportLocation(Name):
	global AirportData

	if AirportData == []:
		with open(os.path.join(ModuleDirectory, '../Data/AirportLocations.json'), 'r') as file_:
			AirportData = json.loads(file_.read())	

	for Element in AirportData:
		if Element["Name"] == Name:
			return [Element["Latitude"], Element["Longitude"]]

	return None

# the waypoints will always be less than 'Spacing' km apart
# the WaypointObjects need to be in order from start to finish for the interpolations to make sense
def InterpolateWaypoints(WaypointObjects, Spacing=5):
	# an array of latlon arrays will be returned
	ReturnArray = []

	# check the distance between each two flight waypoints
	for i in range(0, len(WaypointObjects) - 1):
		FirstWaypoint = WaypointObjectToArray(WaypointObjects[i])
		SecondWaypoint = WaypointObjectToArray(WaypointObjects[i + 1])

		# create a line object from two gps points
		InterpolationLine = Geodesic.WGS84.InverseLine(FirstWaypoint[0], FirstWaypoint[1], SecondWaypoint[0], SecondWaypoint[1])
		# gets the distance between the two endpoints of the line
		LineLengthMeters = InterpolationLine.s13
		LineLengthKilometers = LineLengthMeters / 1000.0

		# calculate the number of points we need based on the spacing
		SpacingMeters = Spacing * 1000
		NumberOfPoints = int((LineLengthMeters + (SpacingMeters - LineLengthMeters % SpacingMeters)) / SpacingMeters)

		for s in range(0, NumberOfPoints * SpacingMeters, SpacingMeters):
			# creates a line whose first point is the same as InterpolationLine's first point and whose second point in a set distance down InterpolationLine
			NewLineSegment = InterpolationLine.Position(s)
			ReturnArray.append([NewLineSegment["lat2"], NewLineSegment["lon2"]])

	return ReturnArray

# return the index where the TargetPoint is, not the actual point itself
def FindClosestPoint(PointArray, TargetPoint):
	# check to make sure that all of the parameters are correct
	# if len(np.array(TargetPoint).shape) != 1 or len(TargetPoint) != 2:
	# 	raise Exception("TargetPoint was in an illegal format")
	# if len(np.array(PointArray).shape) != 2:
	# 	raise Exception("PointArray was in an illegal format")

	PositionDistanceArray = []

	for CurrentPoint in PointArray:
		Distance = DistanceBetweenPoints(TargetPoint, CurrentPoint)

		# add distance from target point, currentpoint, and index to this array
		Index = len(PositionDistanceArray)
		PositionDistanceArray.append([CurrentPoint, Distance, Index])

	# sort the array and find the index in the array that signifies the point with the shortest Distance to the TargetPoint
	return sorted(PositionDistanceArray, key=Array.itemgetter(1))[0][2]

# computes distance in kilometers
def DistanceBetweenPoints(PointOne, PointTwo):
	Line = Geodesic.WGS84.Inverse(PointOne[0], PointOne[1], PointTwo[0], PointTwo[1])
	return Line["s12"] / 1000.0