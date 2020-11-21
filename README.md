# vendee-scraper
web scraper for vendee globe 2020 - output file for Expedition software

Requires ChromeDriver to be installed. ( https://chromedriver.chromium.org/ )

creates Scheds_YYMMDDHHMM.csv file which Expedition will read in the directory that it is run in. BoatID.csv needs to be in the same directory and Expedition set up so that the Scheduler monitors the directory for updates. 
## Changes
### 22 November 2020 - added GPX waypoints export
Moved exports to functions and added a GPX waypoints file export. This can be used with almost any app that can read GPX format such as [OpenCPN](https://github.com/OpenCPN/OpenCPN) etc. 
