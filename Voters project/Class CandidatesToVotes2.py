# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 13:22:21 2018

@author: Fadi
"""

import pandas as pd
import numpy as np

class electionResultsGen:
# =============================================================================
#     Generates the results of a Lebanese election using a votes results file
# =============================================================================
    RepDistributionMay2018File = "RepDistributionMay2018.csv"
    RepDistributionMay2018DF = pd.DataFrame([])
    votesResultsDF = pd.DataFrame([])
    candidatesVotesDF = pd.DataFrame([])
    listExtraVotesDF = pd.DataFrame([])
    da2iraKoubra = ''
    hasel = int
    
    def __init__(self, votesResultsFile):
#        Load the RepDistribution and votes results file as DFs
        self.RepDistributionMay2018DF = pd.read_csv(self.RepDistributionMay2018File, skiprows=0).replace(np.nan, '', regex=True)
        self.votesResultsDF = pd.read_csv(votesResultsFile, skiprows=0, encoding='utf-8-sig')
       
    def getResults(self):
#        Take the candidates part of the table and the Lists part of the table as seperate DFs
        candidatesVotesDF = self.votesResultsDF[['Candidate Name','Religion','Da2ira Soughra','List','Votes']] # selecting candidates columns into a new DF
        listExtraVotesDF = self.votesResultsDF[['ListName','ListExtraVote']].dropna(how='all') # Selecting List columns  # .dropna() to drop rows with nan, 'all' to drop rows where all values are nan 
        
        # Total number of seats in the Da2ira koubra
        da2iraKoubra = self.votesResultsDF.loc[0]['Da2ira']      #Get the da2ira koubra name
        numberOfSeats = self.RepDistributionMay2018DF.loc[self.RepDistributionMay2018DF['الدائرة الكبرى']==da2iraKoubra,'عدد المقاعد'] # Get the number of seats column values in the da2ira koubra #we can add .values to get an array instead of series
        totalNumberOfSeats = sum(numberOfSeats)
        
        # Total number of votes
        sumCandidatesVotesDF=candidatesVotesDF.groupby(['List']).sum().reset_index() #Total number of votes per list (sorted (lists 1,2,3)) in the candidates votes DF # reset_index to get normal index 0,1,2
        sumListExtraVotesDF = listExtraVotesDF.groupby(['ListName']).sum().reset_index() #Total number of extra votes per list, note: here votes are already sorted by lists but needed in case lists are not sorted in order
        totalVotes = sumCandidatesVotesDF['Votes'] + sumListExtraVotesDF['ListExtraVote'] #Total number of votes per list
        totalVotesDF = pd.concat([sumListExtraVotesDF['ListName'], totalVotes], axis=1, keys=['ListName', 'Total Votes']) #add the list names to the total number of votes per list # axis=1 to concat along the columns axis not rows, keys are the new column names
        
        # 7asel calculation (to remove the lists and their candidates)
        hasel =  totalVotesDF['Total Votes'].sum() / totalNumberOfSeats     #7asel= total # of votes / # of seats
        tempTotalVotesDF=totalVotesDF   #create a copy of the original totalVotesDF to compare the shape with
        totalVotesDF = totalVotesDF[~(totalVotesDF['Total Votes'] < hasel)]     # ~ removes the row (list) less than hasel
        while totalVotesDF.shape != tempTotalVotesDF.shape:     #while the shape of the tempDF doesnt match the shape of the original DF, another list must be removed
            hasel = totalVotesDF['Total Votes'].sum() / totalNumberOfSeats
            tempTotalVotesDF=totalVotesDF
            totalVotesDF = totalVotesDF[~(totalVotesDF['Total Votes'] < hasel)]
        
        totalNumberOfVotes = sum(totalVotesDF['Total Votes'])  #final total number of votes after 7asel
        passed7aselList = totalVotesDF['ListName'].tolist()     #create a list of the lists that passed the 7asel
        listExtraVotesDF = listExtraVotesDF[listExtraVotesDF['ListName'].isin(passed7aselList)].reset_index(drop=True) #remove the lists that did not pass the hasel from the listExtraVotesDF

        # Candidates Votes DF after 7asel
        votesDF = candidatesVotesDF[candidatesVotesDF['List'].isin(passed7aselList)].reset_index(drop=True) #update the candidates list and votes after hasel #reset_index(drop=True) so we dont save the old index
        
        # List of rites and region for the number of seats
        listOfRites = []
        tempLists = []
        seatsRepartition = self.RepDistributionMay2018DF.loc[self.RepDistributionMay2018DF['الدائرة الكبرى']==da2iraKoubra,['الدائرة الصغرى','سني','شيعي','درزي','علوي','ماروني','روم كاثوليك','روم ارثوذكس','انجيلي','ارمن كاثوليك','ارمن ارثوذكس','اقليات']].set_index('الدائرة الصغرى')  #seats repartition table as dataframe #we can add .values to get an array instead of series
        for column in seatsRepartition:         # get rites and region for the number of seats using a list # nested loops used to go through all rites and dawa2er soghra
            for index, row in seatsRepartition.iterrows():
                value=seatsRepartition.get_value(index,column)
                if value != '':     #if there exists a value, append it to the list
                    tempLists=[value,column,index]
                    listOfRites.append(tempLists)
                    
        # Seats Repartition per List            
        seatsDivision = totalVotesDF.loc[:,'Total Votes']/totalNumberOfVotes*totalNumberOfSeats     #SeatsDivision=NumberOfTotalVotesPerList/TotalNumberOfVotes*TotalNumberOfSeats
        seatsDivisionRounded = (seatsDivision).apply(np.floor)  #Seats Division rounded down to get exact number of seats per list
        seatsDivisionDecimal = seatsDivision%1      #Get decimal part of the division, biggest decimal part gets seat
        seatsRepartitionPerList = pd.concat([totalVotesDF['ListName'], seatsDivisionRounded, seatsDivisionDecimal], axis=1, keys=['ListName', 'Total Seats', 'Decimal'])    #dataframe of listname, current number of seats per list, decimal part of calculation
        while totalNumberOfSeats != sum(seatsRepartitionPerList['Total Seats']):    #while the totalNumberOfSeats originally calculated != sum of seats given for each list, one seat should be added to the max decimal list
            maxDecimal = max(seatsRepartitionPerList['Decimal'])    #maximum of the decimals
            seatsRepartitionPerList.loc[seatsRepartitionPerList['Decimal']==maxDecimal,'Total Seats']+=1    #one seat is added
        seatsRepartitionPerList = seatsRepartitionPerList.drop('Decimal', 1)  #drop the decimal column after finishing calculcations # drop the Decimal column on the 1 (or column) axis  
        
        # Preferential Vote percentage  
        da2iraSoughraDF= votesDF.groupby('Da2ira Soughra')['Votes'].sum().reset_index()     #get the total votes per da2ira soughra
        prefVotes=[]
        for index, row in votesDF.iterrows():
            votesPerCandidate=votesDF.loc[index,'Votes']   #Votes for each single candidate (using the row iteration)
            votesDFDa2iraSoughra = votesDF.loc[index,'Da2ira Soughra'] #da2ira soghra for each single candidate
            correspondingDa2iraSoughraVotes = da2iraSoughraDF.loc[da2iraSoughraDF['Da2ira Soughra'] == votesDFDa2iraSoughra,'Votes'].values[0] #corresponding da2ira soghra total votes for the specific candidate #values attribute to return the values as a np array and then use [0] to get the first value OR we can put the whole expression inside int()
            prefVotesValue=votesPerCandidate/correspondingDa2iraSoughraVotes*100   #prefVotes%=votesPerCandidate/totalVotesInHisDa2iraSoghra*100
            prefVotes.append(prefVotesValue) #add the prefVotes for each candidate to a list
            
        votesDF['Pref Votes %']=prefVotes   #add the prefList as a column in the DF
        
        votesDF = votesDF.sort_values('Pref Votes %',ascending=False).reset_index(drop=True) #sort the DF by pref votes %
        
        # Winning and Losing candidates
        listOfRitesDF = pd.DataFrame(listOfRites, columns=['Seats','Rites','Da2ira']) # save the list of religion and da2ira soghra of each number of seats as a DF
        WinLoss=[]
        
        for index, row in votesDF.iterrows():                   #loop to go through the DF of candidates
            for j, row2 in listOfRitesDF.iterrows():            #loop to go through the DF of number of seats and their religion and da2ira soghra
                tempReligion=votesDF.loc[index,'Religion']      #when the religion and da2ira soghra of the candidate matches the ones of the corresponding number of seats, decrease the number of seats left for each religion+da2ira soghra AND the number of seats left for each list until they reach 0 and add the corresponding candidate to the winners list
                tempDa2ira=votesDF.loc[index,'Da2ira Soughra']
                tempList=votesDF.loc[index,'List']
                tempReligionJ=listOfRitesDF.loc[j,'Rites']
                tempDa2iraJ=listOfRitesDF.loc[j,'Da2ira']
                if seatsRepartitionPerList.loc[seatsRepartitionPerList['ListName']==tempList,'Total Seats'].values[0]>0 and tempReligion==tempReligionJ and tempDa2ira==tempDa2iraJ and listOfRitesDF.loc[j,'Seats']>0:
                    seatsRepartitionPerList.loc[seatsRepartitionPerList['ListName']==tempList,'Total Seats']-=1     #minus 1 for the counter for the number of seats per list
                    listOfRitesDF.loc[j,'Seats']-=1 #minus 1 for the counter for the number of seats per religion+da2ira soghra 
                    WinLossValue='Winner'   #mark the corresponding candidate as a winner
                    WinLoss.append(WinLossValue)    #add the corresponding winner to the winners+losers list
                elif (seatsRepartitionPerList.loc[seatsRepartitionPerList['ListName']==tempList,'Total Seats'].values[0]<=0 or listOfRitesDF.loc[j,'Seats']<=0)and tempReligion==tempReligionJ and tempDa2ira==tempDa2iraJ : #if one of the counters of the number of seats left per list or the numbers of seats left per religion+da2ira soghra reaches 0, add the corresponding candidate to the losers list
                    WinLossValue='Loser'    #mark the corresponding candidate as a loser
                    WinLoss.append(WinLossValue)    #add the corresponding winner to the winners+losers list
        votesDF['Win/Loss']=WinLoss            #add the list of WinLoss as a new column in the votesDF
                    
        votesDF = pd.concat([self.votesResultsDF['Da2ira'],listExtraVotesDF['ListName'],listExtraVotesDF['ListExtraVote'], votesDF], axis=1)    #output DF form of the election results
        votesDF.to_csv("votesDF.csv", index=False, encoding='utf-8-sig')    #write DF to a csv file

electionResultsGen('votesSaidaJezzine1.csv').getResults()
