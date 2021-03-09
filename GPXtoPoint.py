#-------------------------------------------------------------------------------
# Name:        GPX to Points
# Purpose:     Convert gpx files to a point geometry and write to sql
#
# Author:      A. Schirck
#
# Created:     27/02/2020
# Copyright:   (c) aschirck 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import psycopg2
import os
from bs4 import BeautifulSoup as BS
import lxml

# PostgreSQL login info
PG_HOST = os.environ.get('PG_HOST')
PG_PORT = os.environ.get('PG_PORT')
PG_DBNAME = 'bike_routing'
PG_USER = os.environ.get('PG_USER')
PG_PASS = os.environ.get('PG_PASS')



def get_args():
    import argparse
    p = argparse.ArgumentParser(description="Convert GPX files stored in folder to postgres database.")
    p.add_argument('-i', '--in_folder', help='Folder were input files are stored')
    p.add_argument('-t', '--type', help='Type of input: Bikemap/MMF/Endomondo (saved in postgres)')
    p.add_argument('-l', '--loc', help='Location of trip points: FL/SFL/AMS')
    return p.parse_args()

def write_PG(trip_id, lat, lon, elev, osql):

    try:
        conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, dbname=PG_DBNAME, user=PG_USER, password=PG_PASS)
        cur = conn.cursor()
        sql ='INSERT INTO ' + osql + ' (trip_id, elev, geom) values(%s,%s,ST_SetSRID(ST_MakePoint(%s,%s), 4326))'
        cur.execute(sql, (str(trip_id), str(elev), str(lon), str(lat) ))
        conn.commit()

    except(Exception) as e:
        print(e)
        print(type(e))
       # break

def main():
    pass
    args = vars(get_args())
    in_folder = args['in_folder']
    type = args['type']
    loc = args['loc']
    osql = type + '_' + loc

    trips = os.listdir(in_folder)

    for trip in trips:
        trip_id = trip.split('.gpx')[0]
        try:
            trip_file = open (os.path.join(in_folder, trip), 'r')
            content = trip_file.read()
            soup = BS(content, "lxml")
            trk_pts = soup.find_all('trkpt')
            elevs = soup.find_all('ele')
            i=0

            for trk_pt in trk_pts:

                lat = trk_pt.get('lat')
                lon = trk_pt.get('lon')
                elev = trk_pt.find('ele').text
                write_PG(trip_id, lat, lon, elev, osql)

        except (Exception) as e:
            print(e)
            print(type(e))
            continue


if __name__ == '__main__':
    main()
