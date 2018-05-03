# -*- coding: utf-8 -*-
"""
Created on Sat Jan 27 17:06:30 2018

@author: Fadi
"""

import pandas as pd
import numpy as np

DF = pd.read_csv("Kes-Jbeiltest3.csv", skiprows=0, encoding='utf-8-sig')
#Add as variable
RepDistributionMay2018DF = pd.read_csv("RepDistributionMay2018.csv", skiprows=0).replace(np.nan, '', regex=True)
#Add as variable
candidatesVotesDF = DF[['Candidate Name','Religion','Da2ira Soughra','List','Votes']] # selecting columns into a new DF
#Add as variable
listExtraVotesDF = DF[['ListName','ListExtraVote']].dropna(how='all')   # .dropna() to drop rows with nan, 'all' to drop rows where all values are nan

# Total number of seats
#Add as variable
da2iraKoubra = DF.loc[0]['Da2ira']      #get the da2ira koubra name
numberOfSeats = RepDistributionMay2018DF.loc[RepDistributionMay2018DF['الدائرة الكبرى']==da2iraKoubra,'عدد المقاعد']  #we can add .values to get an array instead of series
totalNumberOfSeats = sum(numberOfSeats)

#function getResults() bta3te like the original csv +pref votes+W/L

# Total number of votes
sumCandidatesVotesDF=candidatesVotesDF.groupby(['List']).sum() # reset_index to get normal index 0,1,2
sumListExtraVotesDF = listExtraVotesDF.groupby(['ListName']).sum()
totalVotes=pd.concat([sumListExtraVotesDF,sumCandidatesVotesDF['Votes']], axis=1).sum(axis=1).fillna(0)   #Working
#aaa6=pd.merge(sumListExtraVotesDF, sumCandidatesVotesDF,right_index=True, left_index=True,how='outer').sum(axis=1).fillna(0)    #Working
totalVotes=totalVotes.reset_index()
totalVotesDF=totalVotes.rename(columns={'index': 'ListName', 0: 'Total Votes'})


# 7asel
hasel =  totalVotesDF['Total Votes'].sum() / totalNumberOfSeats
haselList = [hasel]
totalVotesNoBlankDF=totalVotesDF.loc[1:,:].reset_index(drop=True)
tempTotalVotesDF=totalVotesNoBlankDF
totalVotesNoBlankDF = totalVotesNoBlankDF[~(totalVotesNoBlankDF['Total Votes'] < hasel)]     # ~ removes the row less than hasel
while totalVotesNoBlankDF.shape != tempTotalVotesDF.shape:
    hasel = (totalVotesNoBlankDF['Total Votes'].sum() + totalVotesDF.loc[0,'Total Votes'])/ totalNumberOfSeats
    tempTotalVotesDF=totalVotesNoBlankDF
    totalVotesNoBlankDF = totalVotesNoBlankDF[~(totalVotesNoBlankDF['Total Votes'] < hasel)]
    haselList.extend([hasel])

totalNumberOfVotes = sum(totalVotesNoBlankDF['Total Votes']) + totalVotesDF.loc[0,'Total Votes']
passed7aselList = totalVotesNoBlankDF['ListName'].tolist()
blankName=totalVotesDF.loc[0,'ListName']
passed7aselWithBlankList = passed7aselList.copy()
passed7aselWithBlankList.extend([blankName])
haselDF = pd.DataFrame(haselList, columns=['Hasel(s)'])

# Candidates Votes DF
votesDF = candidatesVotesDF[candidatesVotesDF['List'].isin(passed7aselList)].reset_index(drop=True) #reset_index(drop=True) so we dont save the old index
listExtraVotesDF = listExtraVotesDF[listExtraVotesDF['ListName'].isin(passed7aselWithBlankList)].reset_index(drop=True) #remove the lists that did not pass the hasel from the listExtraVotesDF

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
seatsDivision = totalVotesNoBlankDF.loc[:,'Total Votes']/totalNumberOfVotes*totalNumberOfSeats
seatsDivisionRounded = (seatsDivision).apply(np.floor)
seatsDivisionDecimal = seatsDivision%1
seatsDivisionDecimalDuplicates = seatsDivisionDecimal.duplicated(keep=False)
seatsRepartitionPerList = pd.concat([totalVotesNoBlankDF['ListName'], seatsDivision, seatsDivisionRounded, seatsDivisionDecimal, seatsDivisionDecimalDuplicates], axis=1, keys=['ListName', 'Seats Division', 'Total Seats', 'Decimal', 'Decimal Duplicates'])
seatsRepartitionPerList3 = seatsRepartitionPerList.copy()   #testing purposes
while totalNumberOfSeats != sum(seatsRepartitionPerList['Total Seats']):
    maxDecimal = max(seatsRepartitionPerList['Decimal'])
    if seatsRepartitionPerList.loc[seatsRepartitionPerList['Decimal']==maxDecimal,'Decimal Duplicates'].values[0]==False:
        seatsRepartitionPerList.loc[seatsRepartitionPerList['Decimal']==maxDecimal,'Total Seats']+=1
        seatsRepartitionPerList.loc[seatsRepartitionPerList['Decimal']==maxDecimal,'Decimal']=0
    elif seatsRepartitionPerList.loc[seatsRepartitionPerList['Decimal']==maxDecimal,'Decimal Duplicates'].values[0]==True:        
        seatsDuplicates = seatsRepartitionPerList.duplicated('Total Seats', keep=False)
        seatsRepartitionPerList = pd.concat([seatsRepartitionPerList,seatsDuplicates], axis=1)
        seatsRepartitionPerList.columns.values[5] = 'Seats Duplicates'
        maxSeats = max(seatsRepartitionPerList.loc[(seatsRepartitionPerList['Decimal']==maxDecimal) & (seatsRepartitionPerList['Decimal Duplicates']==True), 'Total Seats'])
        if seatsRepartitionPerList.loc[(seatsRepartitionPerList['Decimal']==maxDecimal) & (seatsRepartitionPerList['Total Seats']==maxSeats),'Seats Duplicates'].values[0]==False:
            seatsRepartitionPerList.loc[(seatsRepartitionPerList['Decimal']==maxDecimal) & (seatsRepartitionPerList['Total Seats']==maxSeats),'Total Seats']+=1
            seatsRepartitionPerList.loc[(seatsRepartitionPerList['Decimal']==maxDecimal) & (seatsRepartitionPerList['Total Seats']==maxSeats+1),'Decimal']=0
        elif seatsRepartitionPerList.loc[(seatsRepartitionPerList['Decimal']==maxDecimal) & (seatsRepartitionPerList['Total Seats']==maxSeats),'Seats Duplicates'].values[0]==True:
            duplicateSeatsList1=seatsRepartitionPerList.loc[(seatsRepartitionPerList['Decimal']==maxDecimal) & (seatsRepartitionPerList['Total Seats']==maxSeats),'ListName'].values[0]
            duplicateSeatsList2=seatsRepartitionPerList.loc[(seatsRepartitionPerList['Decimal']==maxDecimal) & (seatsRepartitionPerList['Total Seats']==maxSeats),'ListName'].values[1]
            maxCandidate = max(candidatesVotesDF.loc[(candidatesVotesDF['List']==duplicateSeatsList1) | (candidatesVotesDF['List']==duplicateSeatsList2), 'Votes'])
            maxCandidateList = candidatesVotesDF.loc[candidatesVotesDF['Votes']==maxCandidate,'List'].values[0]
            seatsRepartitionPerList.loc[(seatsRepartitionPerList['Decimal']==maxDecimal) & (seatsRepartitionPerList['Total Seats']==maxSeats) & (seatsRepartitionPerList['ListName']==maxCandidateList),'Total Seats']+=1            
            seatsRepartitionPerList.loc[(seatsRepartitionPerList['Decimal']==maxDecimal) & (seatsRepartitionPerList['Total Seats']==maxSeats+1) & (seatsRepartitionPerList['ListName']==maxCandidateList),'Decimal']=0                 
            seatsRepartitionPerList = seatsRepartitionPerList.drop('Seats Duplicates', 1)
        
seatsRepartitionPerList2 = seatsRepartitionPerList.copy()   #copy the current seatsRepartitionPerList to verify the seatsRepartition later

# Preferential Vote percentage  
da2iraSoughraDF= votesDF.groupby('Da2ira Soughra')['Votes'].sum().reset_index()
prefVotes=[]
for index, row in votesDF.iterrows():
    votesPerCandidate=votesDF.loc[index,'Votes']
    votesDFDa2iraSoughra = votesDF.loc[index,'Da2ira Soughra']
    correspondingDa2iraSoughraVotes = da2iraSoughraDF.loc[da2iraSoughraDF['Da2ira Soughra'] == votesDFDa2iraSoughra,'Votes'].values[0] #values attribute to return the values as a np array and then use [0] to get the first value OR we can put the whole expression inside int()
    prefVotesValue=round((votesPerCandidate/correspondingDa2iraSoughraVotes*100),2)
    prefVotes.append(prefVotesValue)
    
votesDF['Pref Votes %']=prefVotes

votesDF = votesDF.sort_values('Pref Votes %',ascending=False).reset_index(drop=True)

# Winners
listOfRitesDF = pd.DataFrame(listOfRites, columns=['Seats','Rites','Da2ira'])
WinLoss=[]

for index, row in votesDF.iterrows():
    for j, row2 in listOfRitesDF.iterrows():
        tempReligion=votesDF.loc[index,'Religion']
        tempDa2ira=votesDF.loc[index,'Da2ira Soughra']
        tempList=votesDF.loc[index,'List']
        tempReligionJ=listOfRitesDF.loc[j,'Rites']
        tempDa2iraJ=listOfRitesDF.loc[j,'Da2ira']
        if seatsRepartitionPerList.loc[seatsRepartitionPerList['ListName']==tempList,'Total Seats'].values[0]>0 and tempReligion==tempReligionJ and tempDa2ira==tempDa2iraJ and listOfRitesDF.loc[j,'Seats']>0:
            seatsRepartitionPerList.loc[seatsRepartitionPerList['ListName']==tempList,'Total Seats']-=1
            listOfRitesDF.loc[j,'Seats']-=1
            WinLossValue='Winner'
            WinLoss.append(WinLossValue)
        elif (seatsRepartitionPerList.loc[seatsRepartitionPerList['ListName']==tempList,'Total Seats'].values[0]<=0 or listOfRitesDF.loc[j,'Seats']<=0)and tempReligion==tempReligionJ and tempDa2ira==tempDa2iraJ :
            WinLossValue='Loser'
            WinLoss.append(WinLossValue)
votesDF['Win/Loss']=WinLoss

emptyDF = pd.DataFrame({'':[]})
votesDF = pd.concat([DF['Da2ira'],emptyDF,listExtraVotesDF['ListName'],listExtraVotesDF['ListExtraVote'], emptyDF, votesDF, emptyDF, totalVotesNoBlankDF, emptyDF, haselDF], axis=1)
     
votesDF.to_csv("votesDF.csv", index=False, encoding='utf-8-sig')


# =============================================================================
#aaa1=pd.merge(sumListExtraVotesDF, sumCandidatesVotesDF,right_index=True, left_index=True,how='outer').fillna(0)
##aaa7=pd.concat([sumListExtraVotesDF,sumCandidatesVotesDF]).groupby(level=0).fillna(0)
#aaa2=pd.concat([sumListExtraVotesDF,sumCandidatesVotesDF]).groupby(level=0).sum().fillna(0)
#aaa3=pd.concat([sumListExtraVotesDF,sumCandidatesVotesDF['Votes']], axis=1).fillna(0)
#aaa5=pd.merge(sumListExtraVotesDF, sumCandidatesVotesDF,right_index=True, left_index=True,how='outer').fillna(0)
# =============================================================================










