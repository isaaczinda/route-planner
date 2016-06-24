import math
import numpy as np

def DifferenceBetweenDegrees(One, Two):
    Difference = abs(One - Two)

    if Difference <= 180:
        return Difference
    else:
        return abs(Difference - 360)

# always returns an angle less than pi radians
def AngleBetweenLines(LineOne, LineTwo):
	LengthOne = np.linalg.norm(np.array(LineOne))
	LengthTwo = np.linalg.norm(np.array(LineTwo))

	# normalize the vectors
	LineOne = np.array(LineOne) / LengthOne
	LineTwo = np.array(LineTwo) / LengthTwo

	# no need to divide by sum of lengths because these are both 1
	CosTheta = np.dot(np.array(LineOne), np.array(LineTwo))

	# can be one of two different things.
	ThetaValues = [math.acos(CosTheta), math.pi - math.acos(CosTheta)]

	# use the sum of normalized vectors to determine if the angle is less than or greater than 90 
	# if the angle if less than 90, we return something greater than 90
	if np.linalg.norm(LineOne + LineTwo) < math.sqrt(2):
		# return the larger of the two theta values
		return sorted(ThetaValues)[1]
	# if the angle is greater than 90, we return something less than 90
	else:
		# return the smaller of the two theta values
		return sorted(ThetaValues)[0]

# vector points towards PointTwo 
def PointsToVector(PointOne, PointTwo):
	return [PointTwo[0] - PointOne[0], PointTwo[1] - PointOne[1]]

# angle in radians
def BearingToVector(Bearing, Strength=1):
	# convert bearing to angle 
	return [math.cos(Bearing) * Strength, math.sin(Bearing) * Strength]

# returns bearing in radians
def AngleToBearing(Angle):
	# add 90 degrees to the angle
	AddedAngle = Angle + math.pi / 2.0

	# flip the x component of the angle
	RawAngle = math.atan2(math.sin(AddedAngle), -math.cos(AddedAngle))

	return RawAngle % (math.pi * 2) 

# takes bearing in radians returns degree in radians
def BearingToAngle(Bearing):
	FlippedAngle = math.atan2(math.sin(Bearing), -math.cos(Bearing))

	# add 90 degrees to the angle
	AddedAngle = FlippedAngle - math.pi / 2.0

	# flip the x component of the angle
	return AddedAngle % (math.pi * 2)

def VectorFromSpeedBearing(Speed, Bearing):
	x = math.cos(math.radians(Bearing)) * Speed
	y = math.sin(math.radians(Bearing)) * Speed

	return [x, y]

# all angles in degrees
# wind bearing is the direction that the wind is blowing not where it is coming from
def SolveWindTriangle(WindBearing, WindStrength, Airspeed, PlaneBearing):
	# make sure that we don't allow any vectors with length 0
	# if there is no wind, the airspeed is the actual speed
	if WindStrength == 0:
		return Airspeed

	GroundVector = BearingToVector(math.radians(PlaneBearing))
	WindVector = BearingToVector(math.radians(WindBearing), Strength=WindStrength)

	GroundWindAngle = AngleBetweenLines(GroundVector, WindVector) # checked and good

	if WindStrength > Airspeed:
		raise ValueError("WindStrength must always be less than Airspeed")

	# this is SSA congruence; it works because the side opposite the known angle is always larger than the other side.  
	AirGroundAngle = math.asin(WindStrength * math.sin(GroundWindAngle) / float(Airspeed))

	# print "air ground", AirGroundAngle

	AirWindAngle = math.pi - (AirGroundAngle + GroundWindAngle)

	# assumed
	GroundLength = (math.sin(AirWindAngle) * Airspeed) / math.sin(GroundWindAngle)

	return GroundLength