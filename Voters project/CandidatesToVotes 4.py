# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 09:15:01 2018

@author: Fadi
"""

import pandas as pd
import numpy as np

df = pd.read_csv("Kes-Jbeiltest.csv", skiprows=0, encoding='utf-8-sig')
#Add as variable
RepDistributionMay2018DF = pd.read_csv("RepDistributionMay2018.csv", skiprows=0).replace(np.nan, '', regex=True)
#Add as variable
candidatesVotesDf = df[['Candidate Name','Religion','Da2ira Soughra','List','Votes']] # selecting columns into a new df
#Add as variable
listExtraVotesDf = df[['ListName','ListExtraVote']].dropna(how='all')   # .dropna() to drop rows with nan, 'all' to drop rows where all values are nan

# Total number of seats
#Add as variable
da2iraKoubra = df.loc[0]['Da2ira']      #get the da2ira koubra name
numberOfSeats = RepDistributionMay2018DF.loc[RepDistributionMay2018DF['الدائرة الكبرى']==da2iraKoubra,'عدد المقاعد']  #we can add .values to get an array instead of series
totalNumberOfSeats = sum(numberOfSeats)

#function getResults() bta3te like the original csv +pref votes+W/L

# Total number of votes
sumCandidatesVotesDf=candidatesVotesDf.groupby(['List']).sum().reset_index() # reset_index to get normal index 0,1,2
sumListExtraVotesDf = listExtraVotesDf.groupby(['ListName']).sum().reset_index()
totalVotes = sumCandidatesVotesDf['Votes'] + sumListExtraVotesDf['ListExtraVote']
totalVotesDf = pd.concat([sumListExtraVotesDf['ListName'], totalVotes], axis=1, keys=['ListName', 'Total Votes']) # axis=1 to concat along the columns axis not rows, keys are the new column names

# 7asel
#Add as variable
hasel =  totalVotesDf['Total Votes'].sum() / totalNumberOfSeats
tempTotalVotesDf=totalVotesDf
totalVotesDf = totalVotesDf[~(totalVotesDf['Total Votes'] < hasel)]     # ~ removes the row less than hasel
while totalVotesDf.shape != tempTotalVotesDf.shape:
    hasel = totalVotesDf['Total Votes'].sum() / totalNumberOfSeats
    tempTotalVotesDf=totalVotesDf
    totalVotesDf = totalVotesDf[~(totalVotesDf['Total Votes'] < hasel)]

totalNumberOfVotes = sum(totalVotesDf['Total Votes'])
passed7aselList = totalVotesDf['ListName'].tolist()

# Candidates Votes Df
votesDf = candidatesVotesDf[candidatesVotesDf['List'].isin(passed7aselList)].reset_index(drop=True) #reset_index(drop=True) so we dont save the old index
listExtraVotesDf = listExtraVotesDf[listExtraVotesDf['ListName'].isin(passed7aselList)].reset_index(drop=True) #remove the lists that did not pass the hasel from the listExtraVotesDf

# List of Rites
listOfRites = []
tempLists = []
seatsRepartition = RepDistributionMay2018DF.loc[RepDistributionMay2018DF['الدائرة الكبرى']==da2iraKoubra,['الدائرة الصغرى','سني','شيعي','درزي','علوي','ماروني','روم كاثوليك','روم ارثوذكس','انجيلي','ارمن كاثوليك','ارمن ارثوذكس','اقليات']].set_index('الدائرة الصغرى')  #we can add .values to get an array instead of series
for column in seatsRepartition: 
    for index, row in seatsRepartition.iterrows():
        value=seatsRepartition.get_value(index,column)
        if value != '':
            tempLists=[value,column,index]
            listOfRites.append(tempLists)
            
# Seats Repartition             
seatsDivision = totalVotesDf.loc[:,'Total Votes']/totalNumberOfVotes*totalNumberOfSeats
seatsDivisionRounded = (seatsDivision).apply(np.floor)
seatsDivisionDecimal = seatsDivision%1
seatsRepartitionPerList = pd.concat([totalVotesDf['ListName'], seatsDivisionRounded, seatsDivisionDecimal], axis=1, keys=['ListName', 'Total Seats', 'Decimal'])
while totalNumberOfSeats != sum(seatsRepartitionPerList['Total Seats']):
    maxDecimal = max(seatsRepartitionPerList['Decimal'])
    seatsRepartitionPerList.loc[seatsRepartitionPerList['Decimal']==maxDecimal,'Total Seats']+=1
    seatsRepartitionPerList.loc[seatsRepartitionPerList['Decimal']==maxDecimal,'Decimal']=0
seatsRepartitionPerList2 = seatsRepartitionPerList.copy()   #copy the current seatsRepartitionPerList to verify the seatsRepartition later
seatsRepartitionPerList = seatsRepartitionPerList.drop('Decimal', 1)  # drop the Decimal column on the 1 (or column) axis  

# Preferential Vote percentage  
da2iraSoughraDf= votesDf.groupby('Da2ira Soughra')['Votes'].sum().reset_index()
prefVotes=[]
for index, row in votesDf.iterrows():
    votesPerCandidate=votesDf.loc[index,'Votes']
    votesDfDa2iraSoughra = votesDf.loc[index,'Da2ira Soughra']
    correspondingDa2iraSoughraVotes = da2iraSoughraDf.loc[da2iraSoughraDf['Da2ira Soughra'] == votesDfDa2iraSoughra,'Votes'].values[0] #values attribute to return the values as a np array and then use [0] to get the first value OR we can put the whole expression inside int()
    prefVotesValue=votesPerCandidate/correspondingDa2iraSoughraVotes*100
    prefVotes.append(prefVotesValue)
    
votesDf['Pref Votes %']=prefVotes

votesDf = votesDf.sort_values('Pref Votes %',ascending=False).reset_index(drop=True)

# Winners
listOfRitesDf = pd.DataFrame(listOfRites, columns=['Seats','Rites','Da2ira'])
WinLoss=[]

for index, row in votesDf.iterrows():
    for j, row2 in listOfRitesDf.iterrows():
        tempReligion=votesDf.loc[index,'Religion']
        tempDa2ira=votesDf.loc[index,'Da2ira Soughra']
        tempList=votesDf.loc[index,'List']
        tempReligionJ=listOfRitesDf.loc[j,'Rites']
        tempDa2iraJ=listOfRitesDf.loc[j,'Da2ira']
        if seatsRepartitionPerList.loc[seatsRepartitionPerList['ListName']==tempList,'Total Seats'].values[0]>0 and tempReligion==tempReligionJ and tempDa2ira==tempDa2iraJ and listOfRitesDf.loc[j,'Seats']>0:
            seatsRepartitionPerList.loc[seatsRepartitionPerList['ListName']==tempList,'Total Seats']-=1
            listOfRitesDf.loc[j,'Seats']-=1
            WinLossValue='Winner'
            WinLoss.append(WinLossValue)
        elif (seatsRepartitionPerList.loc[seatsRepartitionPerList['ListName']==tempList,'Total Seats'].values[0]<=0 or listOfRitesDf.loc[j,'Seats']<=0)and tempReligion==tempReligionJ and tempDa2ira==tempDa2iraJ :
            WinLossValue='Loser'
            WinLoss.append(WinLossValue)
votesDf['Win/Loss']=WinLoss
votesDf = pd.concat([df['Da2ira'],listExtraVotesDf['ListName'],listExtraVotesDf['ListExtraVote'], votesDf], axis=1)
     
votesDf.to_csv("votesDf.csv", index=False, encoding='utf-8-sig')




















# =============================================================================
# #Draft
# sum values in a column that match a given condition
# df.loc[df['a'] == 1, 'b'].sum()
# or
# df.groupby('a')['b'].sum()[1]
# #Alternative lines of code
# numberOfSeats = RepDistributionMay2018DF.loc[RepDistributionMay2018DF['الدائرة الكبرى']==da2iraKoubra]['عدد المقاعد']  #we can add .values to get an array instead of series
#     idx1=seatsRepartitionPerList.index[seatsRepartitionPerList['Decimal']==maxDecimal].tolist()[0] #alternative method 1
#     idx2=seatsRepartitionPerList.Decimal[seatsRepartitionPerList.Decimal==maxDecimal].index.tolist()[0] #alternative method 2
#     seatsRepartitionPerList.loc[idx1,'Total Seats']+=1
# #['سني','شيعي','درزي','علوي','ماروني','روم كاثوليك','روم ارثوذكس','انجيلي','ارمن كاثوليك','ارمن ارثوذكس','اقليات']
# #['الدائرة الصغرى','سني','شيعي','درزي','علوي','ماروني','روم كاثوليك','روم ارثوذكس','انجيلي','ارمن كاثوليك','ارمن ارثوذكس','اقليات']
# 
# =============================================================================









