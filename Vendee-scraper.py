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

# driver = webdriver.Chrome("chromedriver.exe")
driver = webdriver.Chrome(executable_path=r'chromedriver.exe')
skippers=[]
rankings=[]
latitudes=[]
longitudes=[]
reportTimes=[]

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

BoatID_clean = {'Yes We Cam!' : 1,
                    'HUGO BOSS' : 2,
                    'OMIA' : 3,
                    'GROUPE APICIL' : 4,
                    'PRB' : 5,
                    'BUREAU VALLEE 2' : 6,
                    'LinkedOut' : 7,
                    'Maitre CoQ IV' : 8,
                    'SEAEXPLORER' : 9,
                    'ARKEA PAPREC' : 10,
                    'APIVIA' : 11,
                    'INITIATIVES-COEUR' : 12,
                    'PURE' : 13,
                    'V and B' : 14,
                    "CORUM" : 15,
                    'MACSF' : 16,
                    'LA FABRIQUE' : 17,
                    'PRYSMIAN GROUP' : 18,
                    'BANQUE POPULAIRE X' : 19,
                    'DMG MORI Global One' : 20,
                    'TIME FOR OCEANS' : 21,
                    'LA MIE CALINE' : 22,
                    'MEDALLIA' : 23,
                    'ONE PLANET ONE OCEAN' : 24,
                    'GROUPE SETIN' : 25,
                    'STARK' : 26,
                    'CAMPAGNE DE FRANCE' : 27,
                    'TSE' : 28,
                    "L'OCCITANE EN PROVENCE" : 29,
                    'Compagnie du Lit' : 30,
                    'MERCI' : 31,
                    'NEWREST - ART & FENETRES' : 32,
                    'CHARAL' : 33
                    }
# define functions


def expedition_export(df):
    """ creates a scheds file that expedition can read for race tracking """
    # create filename
    file = "Scheds_"+fileNameStamp+".csv"
    #  and export to CSV
    with open(file, 'w') as file:
        file.write('EXPEDITION\n')
        df.to_csv(file, header=False, index=False, encoding='ascii', line_terminator='\n')


def gpx_export(df):
    """writes a GPX format XML file containing a list of waypoints (requires gpxpy)"""
    pin_colours = ['Black', 'Blue', 'Green', 'Magenta', 'Orange', 'Red', 'White', 'Yellow']
    gpx = gpxpy.gpx.GPX()
    # create some metadata
    gpx.name = 'Vendee'
    gpx.description = fileNameStamp

    # invert dictionary for reverse lookup
    inv_BoatID = {v: k for k, v in BoatID_clean.items()}

    # run through the dataframe and extract lat, lon, time, boat name and give the marker a colour
    for idx in df.index:
        gpx_wps = gpxpy.gpx.GPXWaypoint()
        gpx_wps.latitude = df.loc[idx, 'latitude']
        gpx_wps.longitude = df.loc[idx, 'longitude']
        gpx_wps.time = df.loc[idx, 'time']
        gpx_wps.symbol = "Symbol-Pin-{col}".format(col = pin_colours[(idx) % len(pin_colours)])
        gpx_wps.name = inv_BoatID[df.loc[idx, 'id']]
        # gpx_wps.description = "for future use"
        gpx.waypoints.append(gpx_wps)

    # create the file and write the gpx data
    with open("Vendee_"+fileNameStamp+".gpx", 'w') as f:
        f.write(gpx.to_xml())

# open page in using chromedriver
driver.get("https://www.vendeeglobe.org/en/ranking")
content = driver.page_source
soup = BeautifulSoup(content, "html.parser")
# print(soup.prettify())
# get time of position of report and do some stuff to make
# sure it is recognised as 24hour clock and UTC
filetime = soup.find('p', class_=('rankings__subtitle'))
filetime  = re.sub(r"[h\(\)]+", ' ', filetime.text)
filetime = dparser.parse(filetime, fuzzy=True)
fileNameStamp = filetime.strftime("%y%m%d%H%M")

# find the entries for each boat and interate through them extracting what we want
# for a in soup.findAll('div', attrs={'class':'rankings__item'}):
for a in soup.findAll("tr", class_="ranking-row rankings__item"):

    try:
        # boat name
        name=a.find("td", class_="row-skipper")
        name = name.find('div')
        # current postion in fleet
        ranking=a.find("td", class_="row-number m--firstline")

        latlon = a.find("td", class_="row-layout row-gps")
        lon = latlon.find('span')
        lon.extract()
        lat = latlon

        # Convert lat and lon to strings and strip  special characters
        lat = re.sub(r"\W+|_", " ", lat.text)
        lon = re.sub(r"[^a-zA-Z0-9]+", ' ', lon.text)
        # covert degrees mins and seconds to decimal degrees
        deg, minutes, seconds, direction = str.split(lat)
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
        reportTimes.append(filetime)
    except:
        pass

# create a pandas data frame
df = pd.DataFrame({'id':skippers,'latitude':latitudes,'longitude':longitudes,'time':reportTimes})
# replace boat names with ID for EXPEDITION
df.id = [BoatID[item] for item in df.id]
# export functions :  If you don't want to use a format just comment it out.

expedition_export(df)

gpx_export(df)
