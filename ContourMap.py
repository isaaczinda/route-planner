import sys
sys.path.append("./tools")

import matplotlib as mpl
import Visualization

# globals

Nodes = {} # id, latitude, longitude
References = {} # source id, destination id, weight
ChosenPath = []

# read nodes into dictionary
with open("openstreetmap\\openstreetmap\\bin\\Debug\\nodes.csv", "r") as reader:
	Lines = reader.readlines()

	for Line in Lines:
		Items = Line.split(",")
		Nodes[int(Items[0])] = [float(Items[1]), float(Items[2])] 

# read nodes into dictionary
with open("openstreetmap\\openstreetmap\\bin\\Debug\\edges.csv", "r") as reader:
	Lines = reader.readlines()

	for Line in Lines:
		Items = Line.split(",")
		References[int(Items[0]), int(Items[1])] = float(Items[2])

# read the chosen path nodes
with open("openstreetmap\\openstreetmap\\bin\\Debug\\chosenpath.csv", "r") as reader:
	ChosenPath = [int(temp) for temp in reader.read().split(",")] # convert to integers

MinLatitide = sorted([Nodes[Key][0] for Key in Nodes])[0]
MaxLatitide = sorted([Nodes[Key][0] for Key in Nodes], reverse=True)[0]
MinLongitude = sorted([Nodes[Key][1] for Key in Nodes])[0]
MaxLontitude = sorted([Nodes[Key][1] for Key in Nodes], reverse=True)[0]

Graphic = Visualization.Chart(LatitudeBounds=[MinLatitide, MaxLatitide], LongitudeBounds=[MinLongitude, MaxLontitude])

# draw a dot on the map for each node
for Key in Nodes:
	if Key in ChosenPath:
		Graphic.DrawCircle(Nodes[Key][0], Nodes[Key][1], Color="red")
		print "red"
	else: 
		Graphic.DrawCircle(Nodes[Key][0], Nodes[Key][1], Color="blue")

MinWeight = sorted([References[Key] for Key in References])[0]
MaxWeight = sorted([References[Key] for Key in References], reverse=True)[0]

# normalize  color values to be in [0, 1]
Normalize = mpl.colors.Normalize(vmin=MinWeight,vmax=MaxWeight)

# generate class that can map an array of floats to color objects
Colors = mpl.cm.ScalarMappable(norm=None, cmap="Blues")

# map all weights to color objects
ColorArray = Colors.to_rgba([Normalize(References[Key]) for Key in References])

#print ColorArray

# draw a line on the map for each reference
for Index, Key in enumerate(References):


	Weight = References[Key]
	Graphic.DrawLine(Nodes[Key[0]], Nodes[Key[1]], ColorArray[Index]) # use predetermined color

Graphic.Show()