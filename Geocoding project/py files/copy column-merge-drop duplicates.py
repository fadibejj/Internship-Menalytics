# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 12:34:16 2018

@author: Fadi
"""

import pandas as pd

#Copy Balda Column into Balda_Adj
df = pd.read_csv('LebTownsGeocodedCompleteDF.csv', skiprows=0, encoding='utf-8-sig')
df['Balda_Adj'] = df['Balda'] # copy balda column into a new Balda_Adj column
df.to_csv("LebTownsGeocodedCompleteDF + BaldaAdj.csv", index=False, encoding='utf-8-sig')

#Delete Balda Column
df = pd.read_csv('BaldaAdjustedDFgeocodedCompleteDF2 + BaldaAdj.csv', skiprows=0, encoding='utf-8-sig')
df['Balda'] = None
df.to_csv('BaldaAdjustedDFgeocodedCompleteDF2 + BaldaAdj 2.csv', index=False, encoding='utf-8-sig')

#concat/append 2 DF and drop duplicates, gave same results in this case
df1=pd.read_csv('LebTownsGeocodedCompleteDF + BaldaAdj.csv', skiprows=0, encoding='utf-8-sig')
df2=pd.read_csv('BaldaAdjustedDFgeocodedCompleteDF2 + BaldaAdj 2.csv', skiprows=0, encoding='utf-8-sig')
bigDF1 = df1.append(df2, ignore_index=True)         # Append method 
bigDF1=bigDF1.drop_duplicates(subset=['place_id'])
bigDF2 = pd.concat([df1, df2], ignore_index=True)   # Concat method
bigDF2=bigDF2.drop_duplicates(subset=['place_id'])
bigDF1.to_csv("CompleteDF + BaldaAdj1.csv", index=False, encoding='utf-8-sig')
bigDF2.to_csv("CompleteDF + BaldaAdj2.csv", index=False, encoding='utf-8-sig')
