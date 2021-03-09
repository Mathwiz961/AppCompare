#-------------------------------------------------------------------------------
# Name:  Bikemap Scraper
# Purpose:
#
# Author:      A. Schirck
#
# Created:     08/02/2020
# Copyright:   (c) aschirck 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from bs4 import BeautifulSoup as bs
import re
import csv
import requests
from requests.auth import HTTPBasicAuth

Email = yourbikemapemail
Password = yourbikemappassword

def get_search_page(url):

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

    try:
        page = requests.get(url, headers = headers, auth = HTTPBasicAuth(Email, Password))
        page.raise_for_status()

    except Exception:
        raise requests.HTTPError(Exception)

    if page.status_code == 200:
        return page
    else:
        return -1

def get_gpx_page(url, ID):

    headers = {'Host': 'maptoolkit.net',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'DNT': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
                    'Sec-Fetch-User': '?1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Sec-Fetch-Site': 'cross-site',
                    'Sec-Fetch-Mode': 'navigate',
                    'Referer': 'https://www.bikemap.net/en/r/' + str(ID) + '/',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cookie': 'session=92f9895a0e9f5e042c1320f51fa5996e'
    }

    try:
        page = requests.get(url, headers = headers, auth=HTTPBasicAuth(Email, Password))
        page.raise_for_status()

    except Exception:
        raise requests.HTTPError(Exception)

    if page.status_code == 200:
        return page
    else:
        return -1

def get_stats(url):
#Get data from selected trip

    results = get_search_page(url)
    soup = bs(results.content,'html.parser')

    name = soup.find('h1').text.strip()
    dist = soup.find('span', id ='route-distance').text.strip().split()[0]
    ascent = soup.find('span', id ='route-ascent').text.strip().split()[0]
    descent = soup.find('span', id = 'route-descent').text.strip().split()[0]
    user = soup.find('div', class_='title-author').a.text.strip()
    tripID = url.split('/')[-1]

    location = soup.find('span', class_='location')

    city = location.select('a')[0].text
    state = location.select('a')[1].text
    country = location.select('a')[2].text

    with open (r"C:/Users/aschi/Google Drive/Research/Paper2/NH_BikemapData.csv", 'a', newline ='') as csvfile:
        writer = csv.writer(csvfile, dialect = 'excel')
        writer.writerow([tripID, name, user, city, state, country,  ascent, descent, dist])
    csvfile.close()

def get_gpx (url):
# Gets the GPX data for trip and writes to a file
    end = url.split('/')[-1]
    tripId = end.split('.')[0]

    results = get_gpx_page(url, tripId)

    gpx = open(r'C:/Users/aschi/Google Drive/Research/Paper2/NH_GPX_Bikemap/' + str(tripId) + '.gpx', 'w')
    gpx.write(results.text)
    gpx.close()

def main():
    pass

    head = ['Trip ID', 'Trip Name', 'user', 'City', 'State', 'Country', 'Elevation Ascent in m', 'Elevation Descent in m', 'Distance in km']
    with open (r"C:/Users/aschi/Google Drive/Research/Paper2/NH_BikemapData.csv", 'a', newline ='') as csvfile:
       writer = csv.writer(csvfile, dialect = 'excel')
       writer.writerow(head)
    csvfile.close()

# Trip IDs of trips to be extracted are in CSV file 
    with open (r"C:/Users/aschi/Google Drive/Research/Paper2/NH_Bikemap.csv", 'r') as rcsvfile:
        reader = csv.DictReader(rcsvfile)
        for row in reader:
            try:
                Trip_id = str(row["Trip_id"])
    #for Trip_id in range (900001, 999999, 1):
    #    try:
                URL = 'https://www.bikemap.net/en/r/' + str(Trip_id)
                gpxURL ='https://maptoolkit.net/export/outdoorish_bikemap_routes/' + Trip_id + '.gpx?cache_buster=93379716'
                get_stats(URL)
                get_gpx(gpxURL)

            except (Exception) as e:
                print(e)
                print (type(e))
                continue

    rcsvfile.close()

#   URL ='https://www.bikemap.net/en/r/4775862'
#   gpxURL = 'https://maptoolkit.net/export/outdoorish_bikemap_routes/235193.gpx?cache_buster=93379716'

if __name__ == '__main__':
    main()
