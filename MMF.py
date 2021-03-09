# -------------------------------------------------------------------------------
# Name:        MMF
# Purpose:     Extract route data from MapMyFitness
#
# Author:      A. Schirck-Matthews
#
# Created:     22/02/2020
# Copyright:   (c) aschirck 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import requests
import csv
import json
import time
import psycopg2

# PostgreSQL login info
 PG_HOST = os.environ.get('PG_HOST')
 PG_PORT = os.environ.get('PG_PORT')
 PG_DBNAME = 'bike_routing'
 PG_USER = os.environ.get('PG_USER')
 PG_PASS = os.environ.get('PG_PASS')

# MMF key and secret
 CLIENT_ID = os.environ.get('MMF_CLIENT_ID')
 CLIENT_SECRET = os.environ.get('MMF_CLIENT_SECRET')


works_fine = True

def get_routes(lat, lon, buff):
    # Get authentication token from MMF api

    global works_fine
    url = 'https://oauth2-api.mapmyapi.com/v7.1/oauth2/access_token/'
    headers = {'Api-Key': CLIENT_ID, 'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'client_credentials', 'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET}
    response = requests.post(url, data=data, headers=headers)
    token = response.json()
    headers = {'api-key': CLIENT_ID, 'authorization': 'Bearer %s' % token['access_token']}

    # Find search results

    try:
        link = 'http://api.mapmyfitness.com/v7.1/route/?order_by=-date_created&close_to_location=' + lat + '%2c' + lon \
               + '&search_radius=' + buff + '&minimum_distance=1000' \
               + '&field_set=detailed&activity_type=11&limit=40'
        page = requests.get(link, headers=headers)
        print(page)
        i = 0
        while page.status_code == 502 or page.status_code == 500:
            i +=40
            link = 'http://api.mapmyfitness.com/v7.1/route/?order_by=-date_created&close_to_location=' + lat + '%2c' + lon \
               + '&search_radius=' + buff + '&minimum_distance=1000' \
               + '&field_set=detailed&activity_type=11&limit=40&offset=' + str(i)
            page = requests.get(link, headers=headers)
            print(page)
            print('Page '+ str(int(i/40)) + ' failed.')
        result = json.loads(page.text)
        count = result['total_count']
        print('{0} routes available'.format(count))
        url_base = 'http://api.mapmyfitness.com'

        # Get first page of results
        url = url_base + result['_links']['self'][0]['href']
      #  url = url_base + '/v7.1/route/?order_by=-date_created&close_to_location=26.651712%2C-80.130939&search_radius=10000&minimum_distance=1000&limit=40&offset=320&field_set=detailed&activity_type=11'
        search_page = requests.get(url, headers=headers)
        print(search_page)
        try:
            load = json.loads(search_page.text)
            print('good so far')
            num_of_next = 1
            get_results(load)
            print('Processed page # {0}'.format(num_of_next))
        except:
            print('Page 1 failed')

        # Get subsequent pages of results
        while 'next' in load['_links']:

            try:
                num_of_next = num_of_next + 1
                time.sleep(5)
                href = load['_links']['next'][0]['href']
                if works_fine:
                    url = url_base + href
                #    print(href)
                else:
                    time.sleep(10)
                    url = 'http://api.mapmyfitness.com/v7.1/route/?order_by=-date_created&close_to_location=' + lat + '%2c' + lon \
                       + '&search_radius=' + buff + '&minimum_distance=' + str(1000) \
                       + '&field_set=detailed&activity_type=11&limit=40&offset=' + str(num_of_next * 40)
                    print("Trying page {0}".format(num_of_next))
                search_page = requests.get(url, headers=headers)
                print(search_page)
                load = json.loads(search_page.text)
                get_results(load)
                print('Processed page # {0}'.format(num_of_next))
                works_fine = True

            except Exception as e:
                print("Except in while")
                print(e)
                print(type(e))
                retry()
                continue

    except Exception as e:
        print("Super except")
        print(e)
        print(type(e))

    print('Done')

def retry():
    global works_fine
    works_fine = False


def get_fake_results(text):
    print('results')


def get_results(text):
    # This function extracts the data from the search page

    try:
        routes = text['_embedded']['routes']

        # Go through list of routes and extract the data
        stored_routes = 0

        for item in routes:

            trip_ID = item['_links']['self'][0]['id']
            user_ID = item['_links']['user'][0]['id']
            activity_type = item['_links']['activity_types'][0]['id']
            total_ascent = item['total_ascent']
            total_descent = item['total_descent']
            max_elevation = item['max_elevation']
            min_elevation = item['min_elevation']
            city = item['city']
            state = item['state']
            country = item['country']
            starting_lat = item['starting_location']['coordinates'][1]
            starting_lon = item['starting_location']['coordinates'][0]
            distance = item['distance']
            item_list = [trip_ID, user_ID, activity_type, total_ascent, total_descent, max_elevation, min_elevation,
                         distance, starting_lat, starting_lon, city, state, country]

            # Write data to CSV file

            with open(r'C:\Users\aschi\Google Drive\Research\Paper2\MMF\mmf_park_bike.csv', 'a', newline='') as wcsvfile:
                writer = csv.writer(wcsvfile, dialect='excel')
                writer.writerow(item_list)
            wcsvfile.close()

            # Get trip points for route item and write to postgreSQL database

            points = item['points']
            trip_id = trip_ID

            point_file = open(r'C:\Users\Public\Documents\MMF\points.csv', 'a', newline='')
            for point in points:
                lat = point['lat']
                lon = point['lng']
                try:
                    dist = point['dis']
                except:
                    dist = -999
                try:
                    elev = point['ele']
                except:
                    elev = -999
                txt = [lat, lon, dist, elev, trip_id]
                writer = csv.writer(point_file, dialect='excel')
                writer.writerow(txt)
            point_file.close()

            stored_routes = stored_routes + 1
            # print('stored routes: {0}'.format(stored_routes))
        # all routes from the pge have been processed
        # write points into the DB
        try:
            conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, dbname=PG_DBNAME, user=PG_USER,
                                    password=PG_PASS)
            cur = conn.cursor()
            sql = "copy points from 'C:\\Users\\Public\\Documents\\MMF\\points.csv' with delimiter AS ',';"
            cur.execute(sql)
            conn.commit()
            # empty and reuse points file
            point_file = open('C:\\Users\\Public\\Documents\\MMF\\points.csv', 'w', newline='')
            # writer = csv.writer(point_file, dialect='excel')
            point_file.close()

        except Exception as e:
            print("Except in get_results: copy to DB")
            print(e)
            print(type(e))

    except Exception as e:
        print(e)
        print(type(e))

    # with open (r'C:/Users/aschi/Google Drive/Research/Paper2/tryJson1.txt', 'w') as result:
    #    result.write(json.dumps(text, indent=2))

def main():
    pass
#latList = [26.686276, 25.923825, 25.462413]
#lonList = [-80.319473, -80.275987, -80.474836]
#bufList = [40000, 40000, 10000]

#for i in range (0,2,1):
    lat = str(27.187977)
    lon = str(-82.457381)
    buff = str(600)  # MMF API documentation says this can be up to 50,000 but I keep getting an error over 10,000...WHY??
    get_routes(lat, lon, buff)

if __name__ == '__main__':
    main()
