# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 09:15:01 2018

@author: Fadi
"""

import pandas as pd
import numpy as np
df=pd.read_csv("votesSaidaJezzine1.csv", skiprows=0, encoding='utf-8-sig')
RepDistributionMay2018DF= pd.read_csv("RepDistributionMay2018.csv", skiprows=0).replace(np.nan, '', regex=True)
candidatesVotesDf = df[['Candidate Name','Religion','Da2ira Soughra','List','Votes']] # selecting columns into a new df
listExtraVotesDf = df[['ListName','ListExtraVote']].dropna(how='all')   # .dropna() to drop rows with nan, 'all' to drop rows where all values are nan

da2iraKoubra = df.loc[0]['Da2ira']      #get the da2ira koubra name
numberOfSeats = RepDistributionMay2018DF.loc[RepDistributionMay2018DF['الدائرة الكبرى']==da2iraKoubra]['عدد المقاعد']  #we can add .values to get an array instead of series
totalNumberOfSeats = sum(numberOfSeats)

sumCandidatesVotesDf=candidatesVotesDf.groupby(['List']).sum().reset_index() # reset_index to get normal index 0,1,2
sumListExtraVotesDf = listExtraVotesDf.groupby(['ListName']).sum().reset_index()
totalVotes = sumCandidatesVotesDf['Votes'] + sumListExtraVotesDf['ListExtraVote']
totalVotesDf = pd.concat([listExtraVotesDf['ListName'], totalVotes], axis=1, keys=['ListName', 'Total Votes']) # axis=1 to concat along the columns axis not rows, keys are the new column names

hasel =  totalVotesDf['Total Votes'].sum() / totalNumberOfSeats
totalVotesDf = totalVotesDf[~(totalVotesDf['Total Votes'] < hasel)]
newHasel = totalVotesDf['Total Votes'].sum() / totalNumberOfSeats
passed7aselList = totalVotesDf['ListName'].tolist()
votesDf = candidatesVotesDf[candidatesVotesDf['List'].isin(passed7aselList)].reset_index(drop=True) #reset_index(drop=True) so we dont save the old index

#df1Sorted = df1.sort_values('Votes',ascending=False) #sorting, not needed here
