import sys
sys.path.append("./tools")

import matplotlib as mlp
import Visualization

# globals

Nodes = {} # id, latitude, longitude
References = {} # source id, destination id, weight

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

MinLatitide = sorted([Nodes[Key][0] for Key in Nodes])[0]
MaxLatitide = sorted([Nodes[Key][0] for Key in Nodes], reverse=True)[0]
MinLongitude = sorted([Nodes[Key][1] for Key in Nodes])[0]
MaxLontitude = sorted([Nodes[Key][1] for Key in Nodes], reverse=True)[0]

Graphic = Visualization.Chart(LatitudeBounds=[MinLatitide, MaxLatitide], LongitudeBounds=[MinLongitude, MaxLontitude])

# draw a dot on the map for each node
for Key in Nodes:
	Graphic.DrawCircle(Nodes[Key][0], Nodes[Key][1])

MinWeight = sorted([References[Key] for Key in References])[0]
MaxWeight = sorted([References[Key] for Key in References], reverse=True)[0]

Normalize = mlp.colors.Normalize(vmin=MinWeight,vmax=MaxWeight)

# draw a line on the map for each reference
for Key in References:
	Weight = References[Key]
	Graphic.DrawLine(Nodes[Key[0]], Nodes[Key[1]], Normalize(Weight))

Graphic.Show()