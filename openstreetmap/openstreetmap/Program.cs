using System;
using System.Collections.Generic;
using System.Device.Location;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using System.Xml;

namespace openstreetmap
{
    class Node
    {
        public static List<Node> Items = new List<Node>();

        public GeoCoordinate Location;
        public long Id;
        public List<Way> References = new List<Way>();

        public void AddReference(Way ToAdd)
        {
            //add the reference
            References.Add(ToAdd);
        }

        static public Node GetById(int Id)
        {
            return Items.Find(item => item.Id == Id);
        }

        //recreate all of the node Ids so that they start from 0
        static public void Reindex()
        {
            for(int i = 0; i < Items.Count; i++)
            {
                Items[i].Id = i; //reset the id to the index number
            }
        }

        public Node(GeoCoordinate Location, long Id)
        {
            this.Location = Location;
            this.Id = Id;
            Items.Add(this); //add this node to the static node list
        }
    }

    class Way
    {
        public string Highway = "unclassified"; //defualt highway types
        public bool Sidewalk = false;
        public long Id;
        public List<Tag> Tags = new List<Tag>();
        public List<Node> References = new List<Node>();

        public Way(long Id)
        {
            this.Id = Id;
        }

        public void AddReference(long Reference)
        {
            //find a node whose id is equal to reference
            Node Temp = Node.Items.Find(item => item.Id == Reference);
            //add a reference to this node
            References.Add(Temp);
            //make this node reference us
            Temp.AddReference(this);

        }

        public void AddTag(string Key, string Value)
        {
            Tags.Add(new Tag(Key, Value));
        }
    }

    class Tag
    {
        string Key;
        string Value;

        public Tag(string Key, string Value)
        {
            this.Key = Key;
            this.Value = Value;
        }
    }

    class Program
    {
        public static GeoCoordinate LowerBound;
        public static GeoCoordinate UpperBound;

        static void Main(string[] args)
        {
            Path Test = new Path();

            LowerBound = new GeoCoordinate(47.9806, -122.2113);
            UpperBound = new GeoCoordinate(47.9956, -122.1963);

            //float StartLongitude = 
            WebClient WC = new WebClient();
            string RequestString = "http://api.openstreetmap.org/api/0.6/map?bbox=" + LowerBound.Longitude + "," + LowerBound.Latitude + "," + UpperBound.Longitude + "," + UpperBound.Latitude;
            Console.WriteLine(RequestString);
            string Response = WC.DownloadString(RequestString);

            //information that will be extracted from the XML document
            List<Node> Nodes = new List<Node>();
            List<Way> Ways = new List<Way>();

            //setup the reader
            XmlReader reader = XmlReader.Create(new StringReader(Response));
            XmlDocument doc = new XmlDocument();

            //read until we are on the osm tag
            while (reader.NodeType != XmlNodeType.Element && reader.Name != "osm")
            {
                reader.Read();
            }

            //create a basenode that is the OSM tag
            XmlNode basenode = doc.ReadNode(reader);

            foreach (XmlNode Node in basenode.ChildNodes)
            {
                //if it is a descriptor node
                if (Node.Name == "node")
                {
                    long Id = Convert.ToInt64(Node.Attributes.GetNamedItem("id").Value);
                    double Latitude = Convert.ToDouble(Node.Attributes.GetNamedItem("lat").Value);
                    double Longitude = Convert.ToDouble(Node.Attributes.GetNamedItem("lon").Value);

                    Nodes.Add(new Node(new GeoCoordinate(Latitude, Longitude), Id));
                }

                if (Node.Name == "way")
                {
                    long Id = Convert.ToInt64(Node.Attributes.GetNamedItem("id").Value);

                    //create that way object that we will add to
                    Way CurrentWay = new Way(Id);

                    foreach(XmlNode ChildNode in Node.ChildNodes)
                    {

                        if (ChildNode.Name == "nd")
                        {
                            //add the reference to the node object
                            CurrentWay.AddReference(Convert.ToInt64(ChildNode.Attributes.GetNamedItem("ref").Value));
                        }

                        if (ChildNode.Name == "tag")
                        {
                            string Key = ChildNode.Attributes.GetNamedItem("k").Value;
                            string Value = ChildNode.Attributes.GetNamedItem("v").Value;

                            if (Key == "highway")
                                CurrentWay.Highway = Value;
                            else if (Key == "sidewalk")
                                CurrentWay.Sidewalk = true;
                            else
                                CurrentWay.AddTag(Key, Value);
                        }
                    }

                    Ways.Add(CurrentWay);
                }
            }

            // remove each way that doesn't have the highway tag
            Ways = Ways.FindAll(Route => Route.Highway != "unclassified");

            Node.Reindex(); //reindex so that the Id's fit into ints

            Path.Create(Nodes, Ways);
        }
    }
}