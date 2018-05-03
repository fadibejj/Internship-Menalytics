# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import googlemaps

class geoLocation:
    def __init__(self, api_key=None):       # key constructor, defaultis None
        self.setKey = api_key
    def getLocation(self, csvFile):         # gelocation function, requires csv file input
        key=self.setKey
        gmaps = googlemaps.Client(key)      # request to google api, requires api key
        townsGeoLocationDF = pd.read_csv(csvFile, skiprows=0, encoding='utf-8-sig')     # read csv into dataframe
        city_list = townsGeoLocationDF.Balda + " " + townsGeoLocationDF.RegCasa + " لبنان"  # location naming to search for coordinates
        for location in city_list:
            try:
                geocode = gmaps.geocode(location)[0]    # [0] get the first result in google api & gives error if removed
                place_id = geocode['place_id']          # get the place_id key  
                latlong = geocode['geometry']['location'] # get the latitude and logitude keys
            except IndexError:              # if google doesn't find a result it sends an empty list with no index  
                place_id = None             # variable is nothing, empty
                latlong = {'lat': None,
                           'lng': None}    
#            print (place_id)               # print results of geocode for testing purposes
#            print (latlong['lat'])
#            print (latlong['lng'])
            townsGeoLocationDF.loc[city_list == location,'place_id'] = place_id   # add the column place_id
            townsGeoLocationDF.loc[city_list == location,'Latitude'] = latlong['lat']   # add the column Latitute
            townsGeoLocationDF.loc[city_list == location,'Longitude'] = latlong['lng']  # add the column Longitude
    
#        print (townsGeoLocationDF)  
        townsGeoLocationDF.to_csv("LebTownsGeo.csv", index=False, encoding='utf-8-sig')
    def splitCsv(self, csvFile):
        df = pd.read_csv(csvFile, skiprows=0, encoding='utf-8-sig')
        IncompleteDF=df[df['place_id'].isnull()]
        #IncompleteDF=df[df.isnull().any(axis=1)]   # if we want to check all columns for null
#        print (IncompleteDF)   # print for testing 
        IncompleteDF.to_csv("IncompleteDF.csv", index=False, encoding='utf-8-sig')
        CompleteDF=df[df['place_id'].notnull()]
#        print (CompleteDF)     # print for testing
        CompleteDF.to_csv("CompleteDF.csv", index=False, encoding='utf-8-sig')


#geoLocation("AIzaSyC2ZU5N06KKcSaIML04djtCk8jWmLYe-jI").getLocation("LebTowns.csv")
geoLocation().splitCsv("LebTownsGeo.csv")
print('finish')

#Scratch:
#api_key = 'AIzaSyC2ZU5N06KKcSaIML04djtCk8jWmLYe-jI'
#geocode_result
#geocode_result.keys()
#geocode = gmaps.geocode('kahaleh lebanon')[0]
#print(geocode_result['place_id'])
#print(geocode_result['geometry']['location'])
#ChIJ5awuRVW0GBURQgI2VzEfJSE nihaa bekaa
#ChIJAzWOJDU9HxURUjjnOPctWnE kahale
#ChIJf6-TZ521GBURPkqTqq4Jxxg ebleh zahleh 
#nrows=4,na_values
#CompleteDF=df[df[~colName]isnull))]
#IncompleteDF=df[df[colName]isnull))]