from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import sys
import Wind
import numpy as np
import json
import Geometry
import math

def float_range(Start, End, Step):
    List = []
    i = Start

    while i <= End:
        i = round(i, 2)
        List.append(i)
        i += Step
    return List

class Chart:
    def __init__(self, LatitudeBounds=[25, 49.5], LongitudeBounds=[-125, -67.5]):
        # set the bounds of the map
        self.LatitudeBounds = LatitudeBounds
        self.LongitudeBounds = LongitudeBounds        

        self.map = Basemap(projection='tmerc', 
                  lat_0=(LatitudeBounds[0] + LatitudeBounds[1]) / 2.0, lon_0=(LongitudeBounds[0] + LongitudeBounds[1]) / 2.0,
                  llcrnrlon=LongitudeBounds[0], 
                  llcrnrlat=LatitudeBounds[0], 
                  urcrnrlon=LongitudeBounds[1], 
                  urcrnrlat=LatitudeBounds[1],
                  resolution='l')

        # setup all of the points that will be graphed on this map
        self.XPoints = []
        self.YPoints = []
        self.PointColors = []

        #self.map.shadedrelief()
        #self.map.drawcountries()
        #self.map.drawstates()
        #self.map.shadedrelief()

    def DrawCircle(self, Latitude, Longitude, Color="black"):
        x, y = self.map([Longitude], [Latitude])
        self.PointColors.append(Color)
        self.XPoints.append(x)
        self.YPoints.append(y)

    def DrawLine(self, StartPosition, EndPosition, Color):
        Latitudes = [StartPosition[0], EndPosition[0]]
        Longitudes = [StartPosition[1], EndPosition[1]]

        x, y = self.map(Longitudes, Latitudes)

        self.map.plot(x, y, marker=None, color=Color)


    def ArrowsOnMap(self, Positions, Vectors, MaxLength=80000.0):
        LongestVector = sorted([np.linalg.norm(Vector) for Vector in Vectors], reverse=True)[0]

        k = MaxLength / LongestVector

        X, Y = self.map([Position[1] for Position in Positions], [Position[0] for Position in Positions]) # lon, lat

        for i in range(len(Positions)):
            DX = Vectors[i][0] * k
            DY = Vectors[i][1] * k

            plt.arrow(X[i], Y[i], DX, DY, width=MaxLength/10, head_width=MaxLength / 2, head_length=MaxLength / 2, color="black")
        
    def Scatter(self, Points):
        # convert to map coords 
        ProjectedX, ProjectedY = self.map([Point[1] for Point in Points], [Point[0] for Point in Points]) # lon, lat
        self.map.scatter(ProjectedX, ProjectedY, s=50, c=[1 for color in range(len(ProjectedX))])

    def Contour(self, DataMatrix):
        # get the gradiant of lats and lons
        LongitudeShape =  DataMatrix.shape[1]
        LatitudeShape = DataMatrix.shape[0]
        LongitudeGradiant = np.linspace(self.LongitudeBounds[0], self.LongitudeBounds[1], LongitudeShape)
        LatitudeGradiant = np.linspace(self.LatitudeBounds[0], self.LatitudeBounds[1], LatitudeShape)

        # convert to two matrices
        LongitudeMatrix, LatitudeMatrix = np.meshgrid(LongitudeGradiant, LatitudeGradiant)

        # convert lat lon to map coordinates
        for i in range(len(LatitudeMatrix)):
            for j in range(len(LatitudeMatrix[0])):
                x, y = self.map([LongitudeMatrix[i][j]], [LatitudeMatrix[i][j]])
                LongitudeMatrix[i][j] = x[0]
                LatitudeMatrix[i][j] = y[0]

        levels = [i for i in range(0, 3500, 50)]

        # draw the actual contours
        contour = self.map.contourf(LongitudeMatrix, LatitudeMatrix, DataMatrix, levels, alpha=.35)
        plt.colorbar(contour)


    def Show(self):
        # create size array
        Size = [10]*len(self.XPoints)

        # graph all of the points
        plt.scatter(self.XPoints, self.YPoints, Size, marker='D', c=self.PointColors)

        plt.show()