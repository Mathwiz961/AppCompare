# AppCompare
Programs and files associated with research on fitness tracker apps
MMF.py is a program designed to download meta-data and gps points associated with cycling trips (or activity of choice) in a particular region.
You need an API key from MapMyFitness in order do download trips that can be aquired at https://developer.underarmour.com/ and access to a postgreSQL database to store GPS trip points.

The program uses the APIs "close-to-location" and you need to supply a (lat, lon, buff) triple (buffer in meters) to the get_routes function in the main program.  

Bikemap.py is a html parser that scrapes data from bikemap webpage.  You will need a CSV file with a list of trip IDs you want to download (find appropriate IDs on bikemap web site for your project).  The meta data is saved to a CSV file and the GPS points are stored as GPX files.  Use GPXtoPoint.py to convert the GPX files to point features in a postgreSQL database.
