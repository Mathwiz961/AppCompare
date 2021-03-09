# AppCompare
Programs and files associated with research on fitness tracker apps
MMF.py is a program designed to download meta-data and gps points associated with cycling trips (or activity of choice) in a particular region.
You need an API key from MapMyFitness in order do download trips that can be aquired at https://developer.underarmour.com/ and access to a postgreSQL database to store GPS trip points.

The program uses the APIs "close-to-location" and you need to supply a (lat, lon, buff) triple (buffer in meters) to the get_routes function in the main program.  
