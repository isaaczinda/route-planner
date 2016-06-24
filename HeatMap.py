import sys
sys.path.append("./tools")
import numpy as np
from PIL import Image



print "creating blank image"


# store all lon / wind positions in data
MapData = []



SecondsPerReadings = 1
AltitudeMap = Image.new('L', ((3600 / SecondsPerReadings) + 1, (3600 / SecondsPerReadings) + 1))
AltitudeMapPixels = AltitudeMap.load()

print "opening file"
with open("strm-parser/strm-parser/bin/Debug/N48W122.csv", "r") as File:
    Array = File.readlines()

    for i in range(len(Array)):
        Line = Array[i]
        
        Altitude = int(Line.split(",")[2])
        LatitudeSeconds = int(float(Line.split(",")[0]) / SecondsPerReadings) 
        LongitudeSeconds = int(float(Line.split(",")[1]) / SecondsPerReadings)

        if Altitude != -1: # -1 means that there was no altitude location for a certain position
            MapData.append([LatitudeSeconds, LongitudeSeconds, Altitude])
        else:
            MapData.append([LatitudeSeconds, LongitudeSeconds, 0])

        print i, "of", len(Array)


Altitudes = [Item[2] for Item in MapData]
MinAltitude = sorted(Altitudes)[0]
MaxAltitude = sorted(Altitudes, reverse=True)[0]


DeltaAltitude = MaxAltitude - MinAltitude
AltitudeScale = 255 / float(DeltaAltitude)

print "max altitude", MaxAltitude, "min altitude", MinAltitude, "altitude scale", AltitudeScale

# cycle through each altitude and assign it to a pixel
for MapItem in MapData:
    AltitudeMapPixels[MapItem[0], MapItem[1]] = int((MapItem[2] - MinAltitude) * AltitudeScale)

AltitudeMap.show()