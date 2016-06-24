using QuickGraph;
using QuickGraph.Algorithms.Observers;
using QuickGraph.Algorithms.ShortestPath;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using QuickGraph.Graphviz;
using QuickGraph.Graphviz.Dot;
using System.IO;
using System.Device.Location;
using QuickGraph.Algorithms;

namespace openstreetmap
{
    /// <summary>
    /// Convert to Radians.
    /// </summary>
    /// <param name="val">The value to convert to radians</param>
    /// <returns>The value in radians</returns>
    public static class NumericExtensions
    {
        public static double ToRadians(this double val)
        {
            return (Math.PI / 180) * val;
        }
    }

    //edge class that can be used for keys
    class CompEdge : Edge<int>
    {
        // call the base constructor
        public CompEdge(int source, int target) : base(source, target)
        {
        }

        //converts a list of compedges to edges
        public static List<Edge<int>> ToEdge(List<CompEdge> Input)
        {
            List<Edge<int>> Return = new List<Edge<int>>();

            foreach (CompEdge Edge in Input)
                Return.Add(new Edge<int>(Edge.Source, Edge.Target));

            return Return;
        }

        public bool Equals(CompEdge p)
        {
            // If parameter is null return false:
            if ((object)p == null)
            {
                return false;
            }

            // Return true if the fields match:
            return (base.Target == p.Target) && (base.Source == p.Source);
        }

        public override bool Equals(System.Object obj)
        {
            // If parameter is null return false.
            if (obj == null)
            {
                return false;
            }

            // If parameter cannot be cast to Point return false.
            CompEdge p = obj as CompEdge;
            if ((System.Object)p == null)
            {
                return false;
            }

            // Return true if the fields match:
            return (base.Source == p.Source) && (base.Target == p.Target);
        }

        public override int GetHashCode()
        {
            return base.Source ^ base.Target;
        }
    }

    public class FileDotEngine : IDotEngine
    {
        public string Run(GraphvizImageType imageType, string dot, string outputFileName)
        {
            using (StreamWriter writer = new StreamWriter(outputFileName))
            {
                writer.Write(dot);
            }

            return System.IO.Path.GetFileName(outputFileName);
        }
    }

    class Path
    {
        static Dictionary<int, int> NodeAltitudes = new Dictionary<int, int>();

        static Dictionary<CompEdge, double> Distances = new Dictionary<CompEdge, double>(); //dictionary that contains distance data between edges
        static Dictionary<CompEdge, double> AltitudeChange = new Dictionary<CompEdge, double>();

        //returns distance in kilometers
        private static double DistanceBetweenPlaces(GeoCoordinate First, GeoCoordinate Second)
        {
            double R = 6371; // km

            double sLat1 = Math.Sin(NumericExtensions.ToRadians(First.Latitude));
            double sLat2 = Math.Sin(NumericExtensions.ToRadians(Second.Latitude));
            double cLat1 = Math.Cos(NumericExtensions.ToRadians(First.Latitude));
            double cLat2 = Math.Cos(NumericExtensions.ToRadians(Second.Latitude));
            double cLon = Math.Cos(NumericExtensions.ToRadians(First.Longitude) - NumericExtensions.ToRadians(Second.Longitude));

            double cosD = sLat1 * sLat2 + cLat1 * cLat2 * cLon;

            double d = Math.Acos(cosD);

            double dist = R * d;

            return dist;
        }

        public static void Create(List<Node> Nodes, List<Way> Ways)
        {
            //create the graph
            var Graph = new BidirectionalGraph<int, CompEdge>();

            //add each node referenced by a way
            foreach (Way Path in Ways)
            {
                for (int i = 0; i < Path.References.Count; i++)
                {
                    int Id = (int)Path.References[i].Id;

                    // make sure the node was not already added
                    if (!Graph.Vertices.Contains(Id))
                    {
                        Graph.AddVertex(Id);

                        short Altitude = AltitudeMap.AltitudeAtPosition(Path.References[i].Location);

                        NodeAltitudes.Add(Id, (int)Altitude);
                    }
                }
            }

            foreach (Way Path in Ways)
            {
                //add all of the edges
                for (int i = 1; i < Path.References.Count; i++)
                {
                    Node FirstNode = Path.References[i - 1];
                    Node SecondNode = Path.References[i];

                    //add the edge
                    Graph.AddEdge(new CompEdge((int)FirstNode.Id, (int)SecondNode.Id));
                    Graph.AddEdge(new CompEdge((int)SecondNode.Id, (int)FirstNode.Id));

                    //add the distance edge
                    double Distance = DistanceBetweenPlaces(FirstNode.Location, SecondNode.Location);

                    //add both distances
                    Distances.Add(new CompEdge((int)FirstNode.Id, (int)SecondNode.Id), Distance);
                    Distances.Add(new CompEdge((int)SecondNode.Id, (int)FirstNode.Id), Distance);

                    //get the altitudes
                    double FirstNodeAltitude = NodeAltitudes[(int)FirstNode.Id];
                    double SecondNodeAltitude = NodeAltitudes[(int)SecondNode.Id];

                    //if we don't know either of the altitudes, assume 0 change
                    if (FirstNodeAltitude != -1 || SecondNodeAltitude != -1)
                    {
                        AltitudeChange.Add(new CompEdge((int)FirstNode.Id, (int)SecondNode.Id), FirstNodeAltitude - SecondNodeAltitude);
                        AltitudeChange.Add(new CompEdge((int)SecondNode.Id, (int)FirstNode.Id), SecondNodeAltitude - FirstNodeAltitude);
                    }
                    else
                    {
                        AltitudeChange.Add(new CompEdge((int)FirstNode.Id, (int)SecondNode.Id), 0);
                        AltitudeChange.Add(new CompEdge((int)SecondNode.Id, (int)FirstNode.Id), 0);
                    }
                }
            }

            //calcuate costs for each edge
            var Costs = new Dictionary<CompEdge, double>();

            //cycle through each edge and calcualte its cost
            foreach (Edge<int> Edge in Graph.Edges)
            {
                CompEdge Key = new CompEdge(Edge.Source, Edge.Target);

                double DistanceCost = Distances[Key] * 1000; //convert to meters
                double AltitudeCost = Math.Pow(AltitudeChange[Key], 2); //square the altitude (in meters)
                double Weight = DistanceCost + AltitudeCost;
                Costs.Add(Key, Weight);
            }


            //create arrays that the data will be stored in
            string[] NodeLines = new string[Graph.Vertices.Count()];
            string[] EdgeLines = new string[Graph.Edges.Count()];

            //save nodes to a .csv file
            for (int i = 0; i < Graph.Vertices.Count(); i++)
            {
                int Id = Graph.Vertices.ElementAt(i);

                NodeLines[i] = Id + "," + Node.GetById(Id).Location.Latitude + "," + Node.GetById(Id).Location.Longitude;
            }
            //save edges to a .csv file
            for (int i = 0; i < Graph.Edges.Count(); i++)
            {
                int Source = Graph.Edges.ElementAt(i).Source;
                int Target = Graph.Edges.ElementAt(i).Target;
                
                EdgeLines[i] = Source + "," + Target + "," + Costs[new CompEdge(Source, Target)];
            }

            File.WriteAllLines("nodes.csv", NodeLines);
            File.WriteAllLines("edges.csv", EdgeLines);


            int From = 0;
            int To = 5;

            
            var CostIndexer = AlgorithmExtensions.GetIndexer(Costs);
            var tryGetPath = Graph.ShortestPathsDijkstra(CostIndexer, From);

            IEnumerable<CompEdge> path;
            if (tryGetPath(To, out path))
            {
                
            }

            //create a visualizer for the graph
            GraphvizAlgorithm<int, CompEdge> graphviz = new GraphvizAlgorithm<int, CompEdge>(Graph);
            string output = "output.dot";
            graphviz.Generate(new FileDotEngine(), output);

            // assumes dot.exe is on the path:
            var args = string.Format(@"{0} -Tjpg -O", output);
            System.Diagnostics.Process.Start(@"C:\Program Files (x86)\Graphviz2.38\bin\dot.exe", args);
        }
    }
}
