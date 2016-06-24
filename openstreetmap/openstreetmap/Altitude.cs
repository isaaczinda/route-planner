using System;
using System.Collections.Generic;
using System.Device.Location;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace openstreetmap
{
    class AltitudeMap
    {
        static int TileLatitude, TileLongitude;
        static int XEntries, YEntries;
        static int SecondsPerEntry;
        static BinaryReader AltitudeFileReader;
        static FileStream AltitudeFile;

        static private Tuple<int, int> GetAltitudeExtremes()
        {
            int GreatestAltitude = 0;
            int SmallestAltitude = 0;

            for (int y = 0; y < YEntries; y++)
            {
                for (int x = 0; x < XEntries; x++)
                {
                    short Altitude = Extract(y, x);

                    if (Altitude > GreatestAltitude)
                        GreatestAltitude = Altitude;
                    else if (Altitude < SmallestAltitude)
                        SmallestAltitude = Altitude;

                }

                Console.WriteLine(y);
            }

            return new Tuple<int, int>(GreatestAltitude, SmallestAltitude);
        }

        static public void SaveToImage()
        {
            //load a certain map to save
            LoadSpecificMap(48, 122, 1);

            //get biggest and smallest altitude for scaling
            Tuple<int, int> Extremes = GetAltitudeExtremes();
            int GreatestAltitude = Extremes.Item1;
            int SmallestAltitude = Extremes.Item2;

            Bitmap AltitudeImage = new Bitmap(XEntries, YEntries, System.Drawing.Imaging.PixelFormat.Format24bppRgb);

            double Scale = 255d / Math.Abs(GreatestAltitude - SmallestAltitude);

            for (int y = 0; y < YEntries; y++)
            {
                for (int x = 0; x < XEntries; x++)
                {
                    short Altitude = Extract(y, x);

                    if (Altitude != short.MinValue)
                    {
                        double ScaledValue = ((Altitude - SmallestAltitude) * Scale);
                        //Console.WriteLine(y + " of " + YEntries + ", " + ScaledValue);

                        byte ColorByte = Convert.ToByte(Convert.ToInt16(ScaledValue));
                        AltitudeImage.SetPixel(x, y, Color.FromArgb(ColorByte, ColorByte, ColorByte));
                    }
                    else
                    {

                    }
                }
                Console.WriteLine(y);
            }

            // setup the bitmap that all of the data will be saved to
            AltitudeImage.Save("AltitudeImage.bmp");
        }


        static private string IntToString(int Number, int NumberOfCharacters)
        {
            string Return = Convert.ToString(Number);

            //prepend zeroes until length is the target
            while (Return.Length < NumberOfCharacters)
            {
                Return = "0" + Return;
            }

            return Return;
        }

        static private short Extract(int LatitudeSeconds, int LongitudeSeconds)
        {
            //go to the appropriate place in the file
            AltitudeFile.Seek(((((XEntries - 1) - LatitudeSeconds) * YEntries) + ((YEntries - 1) - LongitudeSeconds)) * 2, SeekOrigin.Begin);

            // extract altitude from the file
            byte[] LittleEndianAltitudeArray = AltitudeFileReader.ReadBytes(2); //byte 0 is most significant
            short Altitude = (short)((LittleEndianAltitudeArray[0] << 8) | (LittleEndianAltitudeArray[1]));


            //handle lack of information cases
            if (Altitude == short.MaxValue || Altitude == short.MinValue)
                return -1;
            else
                return Altitude;
        }

        static public short AltitudeAtPosition(GeoCoordinate Input)
        {
            // make sure that we have loaded the correct square
            int LatitudeSquare = (int)Math.Floor(Input.Latitude);
            int LongitudeSquare = (int)Math.Floor(Math.Abs(Input.Longitude)) + 1;

            //if the correct square isn't currently loaded, load it
            if (LatitudeSquare != TileLatitude && LongitudeSquare != TileLongitude)
            {
                LoadSpecificMap(LatitudeSquare, LongitudeSquare, 1);
            }

            //fetch the actual position
            int LatitudeSeconds = (int) ((Input.Latitude - Math.Floor(Input.Latitude)) * 3600);
            int LongitudeSeconds = (int) ((Math.Abs(Input.Longitude) - Math.Floor(Math.Abs(Input.Longitude))) * 3600);

            return Extract(LatitudeSeconds, LongitudeSeconds);
        }

        static private void LoadSpecificMap(int TileLatitude, int TileLongitude, int SecondsPerEntry)
        {
            AltitudeMap.SecondsPerEntry = SecondsPerEntry;
            AltitudeMap.TileLongitude = TileLongitude;
            AltitudeMap.TileLatitude = TileLatitude;

            //open the file whose name corresponds to the lower left corner
            //raw altitude move from right to left in rows
            AltitudeFile = new FileStream("./N" + IntToString(TileLatitude, 2) + "W" + IntToString(TileLongitude, 3) + ".hgt", FileMode.Open);
            AltitudeFileReader = new BinaryReader(AltitudeFile);

            //calculate the number of entires in the file
            XEntries = (3600 / SecondsPerEntry) + 1;
            YEntries = (3600 / SecondsPerEntry) + 1;
            long TargetFileLength = XEntries * YEntries * 2;

            // throw an exception if the file is the wrong size
            if (TargetFileLength != AltitudeFile.Length)
            {
                throw new IOException("file had the wrong number of entries.");
            }
        }
    }
}
