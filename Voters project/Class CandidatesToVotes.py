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
    candidatesVotesDf = pd.DataFrame([])
    listExtraVotesDf = pd.DataFrame([])
    da2iraKoubra = ''
    hasel = int
    
    def __init__(self, votesResultsFile):
#        Load the RepDistribution and votes results file as DFs
        self.RepDistributionMay2018DF = pd.read_csv(self.RepDistributionMay2018File, skiprows=0).replace(np.nan, '', regex=True)
        self.votesResultsDF = pd.read_csv(votesResultsFile, skiprows=0, encoding='utf-8-sig')
       
    def getResults(self):
#        Take the candidates part of the table and the Lists part of the table as seperate DFs
        candidatesVotesDf = self.votesResultsDF[['Candidate Name','Religion','Da2ira Soughra','List','Votes']] # selecting candidates columns into a new df
        listExtraVotesDf = self.votesResultsDF[['ListName','ListExtraVote']].dropna(how='all') # Selecting List columns  # .dropna() to drop rows with nan, 'all' to drop rows where all values are nan 
        
        # Total number of seats in the Da2ira koubra
        da2iraKoubra = self.votesResultsDF.loc[0]['Da2ira']      #Get the da2ira koubra name
        numberOfSeats = self.RepDistributionMay2018DF.loc[self.RepDistributionMay2018DF['الدائرة الكبرى']==da2iraKoubra,'عدد المقاعد'] # Get the number of seats column values in the da2ira koubra #we can add .values to get an array instead of series
        totalNumberOfSeats = sum(numberOfSeats)
        
        # Total number of votes
        sumCandidatesVotesDf=candidatesVotesDf.groupby(['List']).sum().reset_index() #Total number of votes per list (sorted (lists 1,2,3)) in the candidates votes df # reset_index to get normal index 0,1,2
        sumListExtraVotesDf = listExtraVotesDf.groupby(['ListName']).sum().reset_index() #Total number of extra votes per list, note: here votes are already sorted by lists but needed in case lists are not sorted in order
        totalVotes = sumCandidatesVotesDf['Votes'] + sumListExtraVotesDf['ListExtraVote'] #Total number of votes per list
        totalVotesDf = pd.concat([sumListExtraVotesDf['ListName'], totalVotes], axis=1, keys=['ListName', 'Total Votes']) #add the list names to the total number of votes per list # axis=1 to concat along the columns axis not rows, keys are the new column names
        
        # 7asel calculation (to remove the lists and their candidates)
        hasel =  totalVotesDf['Total Votes'].sum() / totalNumberOfSeats     #7asel= total # of votes / # of seats
        tempTotalVotesDf=totalVotesDf   #create a copy of the original totalVotesDf to compare the shape with
        totalVotesDf = totalVotesDf[~(totalVotesDf['Total Votes'] < hasel)]     # ~ removes the row (list) less than hasel
        while totalVotesDf.shape != tempTotalVotesDf.shape:     #while the shape of the tempDF doesnt match the shape of the original DF, another list must be removed
            hasel = totalVotesDf['Total Votes'].sum() / totalNumberOfSeats
            tempTotalVotesDf=totalVotesDf
            totalVotesDf = totalVotesDf[~(totalVotesDf['Total Votes'] < hasel)]
        
        totalNumberOfVotes = sum(totalVotesDf['Total Votes'])  #final total number of votes after 7asel
        passed7aselList = totalVotesDf['ListName'].tolist()     #create a list of the lists that passed the 7asel
        listExtraVotesDf = listExtraVotesDf[listExtraVotesDf['ListName'].isin(passed7aselList)].reset_index(drop=True) #remove the lists that did not pass the hasel from the listExtraVotesDf

        # Candidates Votes Df after 7asel
        votesDf = candidatesVotesDf[candidatesVotesDf['List'].isin(passed7aselList)].reset_index(drop=True) #update the candidates list and votes after hasel #reset_index(drop=True) so we dont save the old index
        
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
        seatsDivision = totalVotesDf.loc[:,'Total Votes']/totalNumberOfVotes*totalNumberOfSeats     #SeatsDivision=NumberOfTotalVotesPerList/TotalNumberOfVotes*TotalNumberOfSeats
        seatsDivisionRounded = (seatsDivision).apply(np.floor)  #Seats Division rounded down to get exact number of seats per list
        seatsDivisionDecimal = seatsDivision%1      #Get decimal part of the division, biggest decimal part gets seat
        seatsRepartitionPerList = pd.concat([totalVotesDf['ListName'], seatsDivisionRounded, seatsDivisionDecimal], axis=1, keys=['ListName', 'Total Seats', 'Decimal'])    #dataframe of listname, current number of seats per list, decimal part of calculation
        while totalNumberOfSeats != sum(seatsRepartitionPerList['Total Seats']):    #while the totalNumberOfSeats originally calculated != sum of seats given for each list, one seat should be added to the max decimal list
            maxDecimal = max(seatsRepartitionPerList['Decimal'])    #maximum of the decimals
            seatsRepartitionPerList.loc[seatsRepartitionPerList['Decimal']==maxDecimal,'Total Seats']+=1    #one seat is added
        seatsRepartitionPerList = seatsRepartitionPerList.drop('Decimal', 1)  #drop the decimal column after finishing calculcations # drop the Decimal column on the 1 (or column) axis  
        
        # Preferential Vote percentage  
        da2iraSoughraDf= votesDf.groupby('Da2ira Soughra')['Votes'].sum().reset_index()     #get the total votes per da2ira soughra
        prefVotes=[]
        for index, row in votesDf.iterrows():
            votesPerCandidate=votesDf.loc[index,'Votes']   #Votes for each single candidate (using the row iteration)
            votesDfDa2iraSoughra = votesDf.loc[index,'Da2ira Soughra'] #da2ira soghra for each single candidate
            correspondingDa2iraSoughraVotes = da2iraSoughraDf.loc[da2iraSoughraDf['Da2ira Soughra'] == votesDfDa2iraSoughra,'Votes'].values[0] #corresponding da2ira soghra total votes for the specific candidate #values attribute to return the values as a np array and then use [0] to get the first value OR we can put the whole expression inside int()
            prefVotesValue=votesPerCandidate/correspondingDa2iraSoughraVotes*100   #prefVotes%=votesPerCandidate/totalVotesInHisDa2iraSoghra*100
            prefVotes.append(prefVotesValue) #add the prefVotes for each candidate to a list
            
        votesDf['Pref Votes %']=prefVotes   #add the prefList as a column in the DF
        
        votesDf = votesDf.sort_values('Pref Votes %',ascending=False).reset_index(drop=True) #sort the DF by pref votes %
        
        # Winning and Losing candidates
        listOfRitesDf = pd.DataFrame(listOfRites, columns=['Seats','Rites','Da2ira']) # save the list of religion and da2ira soghra of each number of seats as a DF
        WinLoss=[]
        
        for index, row in votesDf.iterrows():                   #loop to go through the DF of candidates
            for j, row2 in listOfRitesDf.iterrows():            #loop to go through the DF of number of seats and their religion and da2ira soghra
                tempReligion=votesDf.loc[index,'Religion']      #when the religion and da2ira soghra of the candidate matches the ones of the corresponding number of seats, decrease the number of seats left for each religion+da2ira soghra AND the number of seats left for each list until they reach 0 and add the corresponding candidate to the winners list
                tempDa2ira=votesDf.loc[index,'Da2ira Soughra']
                tempList=votesDf.loc[index,'List']
                tempReligionJ=listOfRitesDf.loc[j,'Rites']
                tempDa2iraJ=listOfRitesDf.loc[j,'Da2ira']
                if seatsRepartitionPerList.loc[seatsRepartitionPerList['ListName']==tempList,'Total Seats'].values[0]>0 and tempReligion==tempReligionJ and tempDa2ira==tempDa2iraJ and listOfRitesDf.loc[j,'Seats']>0:
                    seatsRepartitionPerList.loc[seatsRepartitionPerList['ListName']==tempList,'Total Seats']-=1     #minus 1 for the counter for the number of seats per list
                    listOfRitesDf.loc[j,'Seats']-=1 #minus 1 for the counter for the number of seats per religion+da2ira soghra 
                    WinLossValue='Winner'   #mark the corresponding candidate as a winner
                    WinLoss.append(WinLossValue)    #add the corresponding winner to the winners+losers list
                elif (seatsRepartitionPerList.loc[seatsRepartitionPerList['ListName']==tempList,'Total Seats'].values[0]<=0 or listOfRitesDf.loc[j,'Seats']<=0)and tempReligion==tempReligionJ and tempDa2ira==tempDa2iraJ : #if one of the counters of the number of seats left per list or the numbers of seats left per religion+da2ira soghra reaches 0, add the corresponding candidate to the losers list
                    WinLossValue='Loser'    #mark the corresponding candidate as a loser
                    WinLoss.append(WinLossValue)    #add the corresponding winner to the winners+losers list
        votesDf['Win/Loss']=WinLoss            #add the list of WinLoss as a new column in the votesDF
                    
        votesDf = pd.concat([self.votesResultsDF['Da2ira'],listExtraVotesDf['ListName'],listExtraVotesDf['ListExtraVote'], votesDf], axis=1)    #output DF form of the election results
        votesDf.to_csv("votesDf.csv", index=False, encoding='utf-8-sig')    #write DF to a csv file

electionResultsGen('votesSaidaJezzine1.csv').getResults()
