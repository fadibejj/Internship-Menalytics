# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 12:21:14 2018

@author: Fadi
"""

import pandas as pd
#Split incomplete words with 7ayy and remove 7ayy+whatComesAfter then remove duplicate entries
df = pd.read_csv('LebTownGeocodedIncompleteDF.csv', skiprows=0, encoding='utf-8-sig')
df['Balda']=df['Balda'].str.split('حي ').str[0]  # split method to split on 'حي' string; [0] grabs the first item in each split list
df=df.drop_duplicates(subset=['Balda', 'RegCasa']) # drop duplicates, parameter keep='first' by default
df.to_csv("BaldaAdjustedDF.csv", index=False, encoding='utf-8-sig')
