"""
Scrapes the Vendeeglobe.org website for the latest positions of
the boats competing in the Vendee Globe race 2020 edition. The scraped
data is used to create output files in Expeditions 'scheds'format and
in standard GPX (XML) format.

Works Windows and Linux

Requires chromedriver to be installed

Functions:
    expedition_export
    gpx_export
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import dateutil.parser as dparser
import gpxpy

driver = webdriver.Chrome("chromedriver.exe")
skippers=[]
rankings=[]
latitudes=[]
longitudes=[]

BoatID = {'Yes We Cam!' : 1,
                    'HUGO BOSS' : 2,
                    'OMIA - WATER FAMILY ' : 3,
                    'GROUPE APICIL' : 4,
                    'PRB' : 5,
                    'BUREAU VALLEE 2' : 6,
                    'LinkedOut' : 7,
                    'Maître CoQ IV' : 8,
                    'SEAEXPLORER - YACHT CLUB DE MONACO' : 9,
                    'ARKEA PAPREC' : 10,
                    'APIVIA' : 11,
                    'INITIATIVES-COEUR' : 12,
                    'PURE - Best Western®' : 13,
                    'V and B-MAYENNE' : 14,
                    "CORUM L'EPARGNE" : 15,
                    'MACSF' : 16,
                    'LA FABRIQUE' : 17,
                    'PRYSMIAN GROUP' : 18,
                    'BANQUE POPULAIRE X' : 19,
                    'DMG MORI Global One' : 20,
                    'TIME FOR OCEANS' : 21,
                    'LA MIE CÂLINE - ARTISANS ARTIPÔLE' : 22,
                    'MEDALLIA' : 23,
                    'ONE PLANET ONE OCEAN' : 24,
                    'GROUPE SÉTIN' : 25,
                    'STARK' : 26,
                    'CAMPAGNE DE FRANCE' : 27,
                    'TSE -  4MYPLANET' : 28,
                    "L'OCCITANE EN PROVENCE" : 29,
                    'Compagnie du Lit / Jiliti' : 30,
                    'MERCI' : 31,
                    'NEWREST - ART & FENÊTRES' : 32,
                    'CHARAL' : 33
                    }
# define functions


def expedition_export(df):
    """ creates a scheds file that expedition can read for race tracking """
    # create filename
    file = "Scheds_"+filetime+".csv"
    #  and export to CSV
    with open(file, 'a') as file:
        file.write('EXPEDITION\n')
        df.to_csv(file, header=False, index=False, encoding='ascii', line_terminator='\n')


def gpx_export(df):
    """writes a GPX format XML file containing a list of waypoints"""
    # creat and write to a GPX fromat file (requires gpxpy)
    gpx = gpxpy.gpx.GPX()
    # create some metadata
    gpx.name = 'Vendee'
    gpx.description = filetime

    # invert dictionary for reverse lookup
    inv_BoatID = {v: k for k, v in BoatID.items()}

    # run through the dataframe and extract lat, lon and boat name
    for idx in df.index:
        gpx_wps = gpxpy.gpx.GPXWaypoint()
        gpx_wps.latitude =df.loc[idx, 'latitude']
        gpx_wps.longitude = df.loc[idx, 'longitude']
        gpx_wps.symbol = "Symbol-Spot-Black"
        gpx_wps.name = inv_BoatID[df.loc[idx, 'id']]
        # gpx_wps.description = "for future use"
        gpx.waypoints.append(gpx_wps)

    # create the file and write the gpx data
    with open("Vendee_"+filetime+".gpx", 'w') as f:
        f.write(gpx.to_xml())

# open page in using chromedriver
driver.get("https://www.vendeeglobe.org/en/ranking")
content = driver.page_source
soup = BeautifulSoup(content, "html.parser")

# get time of position of report and do some stuff to make
# sure it is recognised as 24hour clock and UTC
filetime = soup.find('p', class_=('rankings__subtitle'))
# print(filetime)
filetime  = re.sub(r"[h\(\)]+", ' ', filetime.text)
# print(filetime)
filetime = dparser.parse(filetime, fuzzy=True)
# print(filetime)
filetime = filetime.strftime("%y%m%d%H%M")


# find the entries for each boat and interate through them extracting what we want
for a in soup.findAll('div', attrs={'class':'rankings__item'}):
    try:
        # boat name
        name=a.find('span', attrs={'style':'max-width: 140px;'})
        # current postion in fleet
        ranking=a.find('li', attrs={'class':'rankings__number'})
        # the location of lat and lon is not obvious, and nested,
        # so locate by the position of respective LI
        lists = a.findAll('li')[6]
        lat = lists.findAll('span')[1]
        lon = lists.findAll('span')[2]
        # Convert lat and lon to strings and strip  special characters
        lat = re.sub(r"\W+|_", " ", lat.text)
        lon = re.sub(r"[^a-zA-Z0-9]+", ' ', lon.text)
        # covert degrees mins and seconds to decimal degrees
        deg, minutes, seconds, direction =  re.split('[ ]', lat)
        lat = (float(deg) + float(minutes)/60 + float(seconds)/(60*60)) * \
                (-1 if direction in ['W' or 'O', 'S'] else 1)
        lat = round(lat, 4)
        deg, minutes, seconds, direction =  re.split('[ ]', lon)
        lon = (float(deg) + float(minutes)/60 + float(seconds)/(60*60)) * \
                (-1 if direction in ['W' or 'O', 'S'] else 1)
        lon = round(lon, 4)
    # Append the boats numbers to the  list
        skippers.append(name.text)
        rankings.append(ranking.get_text(strip=True))
        latitudes.append(lat)
        longitudes.append(lon)
    except ValueError:
        pass

# create a pandas data frame
df = pd.DataFrame({'id':skippers,'latitude':latitudes,'longitude':longitudes})
# replace boat names with ID for EXPEDITION
df.id = [BoatID[item] for item in df.id]

# export functions :  If you don't want to use a format just comment it out.

expedition_export(df)

gpx_export(df)
