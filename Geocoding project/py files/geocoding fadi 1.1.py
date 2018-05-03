# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import googlemaps

#class Geolocation:
#    def getlocation(location_name)

townsGeoLocationDF = pd.read_csv('LebTowns.csv', skiprows=0, nrows=4,encoding='utf-8-sig')
api_key = 'AIzaSyC2ZU5N06KKcSaIML04djtCk8jWmLYe-jI'
gmaps = googlemaps.Client(key=api_key)
city_list = townsGeoLocationDF.Balda + " " + townsGeoLocationDF.RegCasa + " لبنان"

for location in city_list:
    try:
        geocode = gmaps.geocode(location)[0]
        # [0] to get the first result when searching beirut lebanon in google api + error if removed
        place_id = geocode['place_id']
        latlong = geocode['geometry']['location']
    except IndexError: #if google doesn't find a result it sends an empty list with no index  
        place_id = None
        latlong = {'lat': None,
                   'lng': None}
    print (place_id)    
    print (latlong['lat'])
    print (latlong['lng'])
    townsGeoLocationDF.loc[city_list == location,'place_id'] = place_id   #to add the column place_id
    townsGeoLocationDF.loc[city_list == location,'Latitude'] = latlong['lat']   #to add the column Latitute
    townsGeoLocationDF.loc[city_list == location,'Longitude'] = latlong['lng']  #to add the column Longitude
    
print (townsGeoLocationDF)  
townsGeoLocationDF.to_csv("LebTownsGeo.csv", index=False, encoding='utf-8-sig')



#geocode_result
#geocode_result.keys()
#geocode = gmaps.geocode('kahaleh lebanon')[0]
#print(geocode_result['place_id'])
#print(geocode_result['geometry']['location'])
#ChIJ5awuRVW0GBURQgI2VzEfJSE nihaa bekaa
#ChIJAzWOJDU9HxURUjjnOPctWnE kahale
#ChIJf6-TZ521GBURPkqTqq4Jxxg ebleh zahleh 
#townsGeoLocationDF.to_csv("LebTownsGeo.csv", index=False, encoding='utf-8-sig')
#nrows,na_values