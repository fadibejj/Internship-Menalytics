# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 09:55:34 2018

@author: Fadi
"""

import googlemaps
gmaps = googlemaps.Client(key='AIzaSyC2ZU5N06KKcSaIML04djtCk8jWmLYe-jI')
loubnan = " لبنان"
location = "مشغره" + " " + "البقاع الغربي" + loubnan
geocode = gmaps.geocode(location)
lat = geocode[0]["geometry"]["location"]["lat"]
lon = geocode[0]["geometry"]["location"]["lng"]
place_id = geocode[0]["place_id"] 

print (place_id)
print (lat,lon)

