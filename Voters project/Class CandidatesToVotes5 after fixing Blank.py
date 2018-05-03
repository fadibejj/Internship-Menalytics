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
    seatsRepartitionPerList = pd.DataFrame([])
    listOfRitesDF = pd.DataFrame([])
    da2iraKoubra = ''
    electionResultsFile=''
    hasel = int
    
    def __init__(self, votesResultsFile):
        self.electionResultsFile=votesResultsFile.replace('.csv','') + '_Results.csv'     #Output file name
        self.RepDistributionMay2018DF = pd.read_csv(self.RepDistributionMay2018File, skiprows=0).replace(np.nan, '', regex=True)
        self.votesResultsDF = pd.read_csv(votesResultsFile, skiprows=0, encoding='utf-8-sig')
       
    def getResults(self):
#        Take the candidates part of the table and the Lists part of the table as seperate DFs
        self.candidatesVotesDF = self.votesResultsDF[['Candidate Name','Religion','Da2ira Soughra','List','Votes']] # selecting candidates columns into a new DF
        self.listExtraVotesDF = self.votesResultsDF[['ListName','ListExtraVote']].dropna(how='all') # Selecting List columns  # .dropna() to drop rows with nan, 'all' to drop rows where all values are nan 
        
        # Total number of seats in the Da2ira koubra
        self.da2iraKoubra = self.votesResultsDF.loc[0]['Da2ira']      #Get the da2ira koubra name
        numberOfSeats = self.RepDistributionMay2018DF.loc[self.RepDistributionMay2018DF['الدائرة الكبرى']==self.da2iraKoubra,'عدد المقاعد'] # Get the number of seats column values in the da2ira koubra #we can add .values to get an array instead of series
        totalNumberOfSeats = sum(numberOfSeats)
        
        # Total number of votes
        sumCandidatesVotesDF=self.candidatesVotesDF.groupby(['List']).sum() #Total number of votes per list (sorted (lists 1,2,3)) in the candidates votes DF
        sumListExtraVotesDF = self.listExtraVotesDF.groupby(['ListName']).sum() #Total number of extra votes per list, sorted
        totalVotes=pd.concat([sumListExtraVotesDF,sumCandidatesVotesDF['Votes']], axis=1).sum(axis=1).fillna(0)   #Total number of votes per list
        totalVotes=totalVotes.reset_index()
        totalVotesDF=totalVotes.rename(columns={'index': 'ListName', 0: 'Total Votes'}) 
        
        # 7asel calculation (to remove the lists and their candidates)
        self.hasel =  totalVotesDF['Total Votes'].sum() / totalNumberOfSeats     #7asel= total # of votes / # of seats
        haselList = [self.hasel]
        totalVotesNoBlankDF=totalVotesDF.loc[1:,:].reset_index(drop=True)
        tempTotalVotesDF=totalVotesNoBlankDF   #create a copy of the original totalVotesNoBlankDF to compare the shape with
        totalVotesNoBlankDF = totalVotesNoBlankDF[~(totalVotesNoBlankDF['Total Votes'] < self.hasel)]     # ~ removes the row (list) less than hasel
        while totalVotesNoBlankDF.shape != tempTotalVotesDF.shape:     #while the shape of the tempDF doesnt match the shape of the original DF, another list must be removed
            self.hasel = (totalVotesNoBlankDF['Total Votes'].sum() + totalVotesDF.loc[0,'Total Votes'])/totalNumberOfSeats
            tempTotalVotesDF=totalVotesNoBlankDF
            totalVotesNoBlankDF = totalVotesNoBlankDF[~(totalVotesNoBlankDF['Total Votes'] < self.hasel)]
            haselList.extend([self.hasel])
        
        totalNumberOfVotes = sum(totalVotesNoBlankDF['Total Votes']) + totalVotesDF.loc[0,'Total Votes']  #final total number of votes after 7asel
        passed7aselList = totalVotesNoBlankDF['ListName'].tolist()     #create a list of the lists that passed the 7asel
        blankName=totalVotesDF.loc[0,'ListName']
        passed7aselWithBlankList = passed7aselList.copy()
        passed7aselWithBlankList.extend([blankName])
        haselDF = pd.DataFrame(haselList, columns=['Hasel(s)'])
        
        # Candidates Votes DF after 7asel
        votesDF = self.candidatesVotesDF[self.candidatesVotesDF['List'].isin(passed7aselList)].reset_index(drop=True) #update the candidates list and votes after hasel #reset_index(drop=True) so we dont save the old index
        self.listExtraVotesDF = self.listExtraVotesDF[self.listExtraVotesDF['ListName'].isin(passed7aselWithBlankList)].reset_index(drop=True) #remove the lists that did not pass the hasel from the listExtraVotesDF

        # List of rites and region for the number of seats
        listOfRites = []
        tempLists = []
        seatsRepartition = self.RepDistributionMay2018DF.loc[self.RepDistributionMay2018DF['الدائرة الكبرى']==self.da2iraKoubra,['الدائرة الصغرى','سني','شيعي','درزي','علوي','ماروني','روم كاثوليك','روم ارثوذكس','انجيلي','ارمن كاثوليك','ارمن ارثوذكس','اقليات']].set_index('الدائرة الصغرى')  #seats repartition table as dataframe #we can add .values to get an array instead of series
        for column in seatsRepartition:         # get rites and region for the number of seats using a list # nested loops used to go through all rites and dawa2er soghra
            for index, row in seatsRepartition.iterrows():
                value=seatsRepartition.get_value(index,column)
                if value != '':     #if there exists a value, append it to the list
                    tempLists=[value,column,index]
                    listOfRites.append(tempLists)
                    
        # Seats Repartition per List            
        seatsDivision = totalVotesNoBlankDF.loc[:,'Total Votes']/totalNumberOfVotes*totalNumberOfSeats     #SeatsDivision=NumberOfTotalVotesPerList/TotalNumberOfVotes*TotalNumberOfSeats
        seatsDivisionRounded = (seatsDivision).apply(np.floor)  #Seats Division rounded down to get exact number of seats per list
        seatsDivisionDecimal = seatsDivision%1      #Get decimal part of the division, biggest decimal part gets seat
        seatsDivisionDecimalDuplicates = seatsDivisionDecimal.duplicated(keep=False)
        self.seatsRepartitionPerList = pd.concat([totalVotesNoBlankDF['ListName'], seatsDivision, seatsDivisionRounded, seatsDivisionDecimal, seatsDivisionDecimalDuplicates], axis=1, keys=['ListName', 'Seats Division', 'Total Seats', 'Decimal', 'Decimal Duplicates'])    #dataframe of listname, current number of seats per list, decimal part of calculation
        while totalNumberOfSeats != sum(self.seatsRepartitionPerList['Total Seats']):    #while the totalNumberOfSeats originally calculated != sum of seats given for each list, one seat should be added to the max decimal list, and if decimals are equal, add a seat to the top voter between the equal decimals' list
            maxDecimal = max(self.seatsRepartitionPerList['Decimal'])    #maximum of the decimals
            if self.seatsRepartitionPerList.loc[self.seatsRepartitionPerList['Decimal']==maxDecimal,'Decimal Duplicates'].values[0]==False:
                self.seatsRepartitionPerList.loc[self.seatsRepartitionPerList['Decimal']==maxDecimal,'Total Seats']+=1
                self.seatsRepartitionPerList.loc[self.seatsRepartitionPerList['Decimal']==maxDecimal,'Decimal']=0
            elif self.seatsRepartitionPerList.loc[self.seatsRepartitionPerList['Decimal']==maxDecimal,'Decimal Duplicates'].values[0]==True:        
                seatsDuplicates = self.seatsRepartitionPerList.duplicated('Total Seats', keep=False)
                self.seatsRepartitionPerList = pd.concat([self.seatsRepartitionPerList,seatsDuplicates], axis=1)
                self.seatsRepartitionPerList.columns.values[5] = 'Seats Duplicates'
                maxSeats = max(self.seatsRepartitionPerList.loc[(self.seatsRepartitionPerList['Decimal']==maxDecimal) & (self.seatsRepartitionPerList['Decimal Duplicates']==True), 'Total Seats'])
                if self.seatsRepartitionPerList.loc[(self.seatsRepartitionPerList['Decimal']==maxDecimal) & (self.seatsRepartitionPerList['Total Seats']==maxSeats),'Seats Duplicates'].values[0]==False:
                    self.seatsRepartitionPerList.loc[(self.seatsRepartitionPerList['Decimal']==maxDecimal) & (self.seatsRepartitionPerList['Total Seats']==maxSeats),'Total Seats']+=1
                    self.seatsRepartitionPerList.loc[(self.seatsRepartitionPerList['Decimal']==maxDecimal) & (self.seatsRepartitionPerList['Total Seats']==maxSeats+1),'Decimal']=0
                elif self.seatsRepartitionPerList.loc[(self.seatsRepartitionPerList['Decimal']==maxDecimal) & (self.seatsRepartitionPerList['Total Seats']==maxSeats),'Seats Duplicates'].values[0]==True:
                    duplicateSeatsList1=self.seatsRepartitionPerList.loc[(self.seatsRepartitionPerList['Decimal']==maxDecimal) & (self.seatsRepartitionPerList['Total Seats']==maxSeats),'ListName'].values[0]
                    duplicateSeatsList2=self.seatsRepartitionPerList.loc[(self.seatsRepartitionPerList['Decimal']==maxDecimal) & (self.seatsRepartitionPerList['Total Seats']==maxSeats),'ListName'].values[1]
                    maxCandidate = max(self.candidatesVotesDF.loc[(self.candidatesVotesDF['List']==duplicateSeatsList1) | (self.candidatesVotesDF['List']==duplicateSeatsList2), 'Votes'])
                    maxCandidateList = self.candidatesVotesDF.loc[self.candidatesVotesDF['Votes']==maxCandidate,'List'].values[0]
                    self.seatsRepartitionPerList.loc[(self.seatsRepartitionPerList['Decimal']==maxDecimal) & (self.seatsRepartitionPerList['Total Seats']==maxSeats) & (self.seatsRepartitionPerList['ListName']==maxCandidateList),'Total Seats']+=1            
                    self.seatsRepartitionPerList.loc[(self.seatsRepartitionPerList['Decimal']==maxDecimal) & (self.seatsRepartitionPerList['Total Seats']==maxSeats+1) & (self.seatsRepartitionPerList['ListName']==maxCandidateList),'Decimal']=0                 
                    self.seatsRepartitionPerList = self.seatsRepartitionPerList.drop('Seats Duplicates', 1)        
        
        # Preferential Vote percentage  
        da2iraSoughraDF= votesDF.groupby('Da2ira Soughra')['Votes'].sum().reset_index()     #get the total votes per da2ira soughra
        prefVotes=[]
        for index, row in votesDF.iterrows():
            votesPerCandidate=votesDF.loc[index,'Votes']   #Votes for each single candidate (using the row iteration)
            votesDFDa2iraSoughra = votesDF.loc[index,'Da2ira Soughra'] #da2ira soghra for each single candidate
            correspondingDa2iraSoughraVotes = da2iraSoughraDF.loc[da2iraSoughraDF['Da2ira Soughra'] == votesDFDa2iraSoughra,'Votes'].values[0] #corresponding da2ira soghra total votes for the specific candidate #values attribute to return the values as a np array and then use [0] to get the first value OR we can put the whole expression inside int()
            prefVotesValue=round((votesPerCandidate/correspondingDa2iraSoughraVotes*100),2)   #prefVotes%=votesPerCandidate/totalVotesInHisDa2iraSoghra*100, round to 2 decimals
            prefVotes.append(prefVotesValue) #add the prefVotes for each candidate to a list
            
        votesDF['Pref Votes %']=prefVotes   #add the prefList as a column in the DF
        
        votesDF = votesDF.sort_values('Pref Votes %',ascending=False).reset_index(drop=True) #sort the DF by pref votes %
        
        # Winning and Losing candidates
        self.listOfRitesDF = pd.DataFrame(listOfRites, columns=['Seats','Rites','Da2ira']) # save the list of religion and da2ira soghra of each number of seats as a DF
        WinLoss=[]
        
        for index, row in votesDF.iterrows():                   #loop to go through the DF of candidates
            for j, row2 in self.listOfRitesDF.iterrows():            #loop to go through the DF of number of seats and their religion and da2ira soghra
                tempReligion=votesDF.loc[index,'Religion']      #when the religion and da2ira soghra of the candidate matches the ones of the corresponding number of seats, decrease the number of seats left for each religion+da2ira soghra AND the number of seats left for each list until they reach 0 and add the corresponding candidate to the winners list
                tempDa2ira=votesDF.loc[index,'Da2ira Soughra']
                tempList=votesDF.loc[index,'List']
                tempReligionJ=self.listOfRitesDF.loc[j,'Rites']
                tempDa2iraJ=self.listOfRitesDF.loc[j,'Da2ira']
                if self.seatsRepartitionPerList.loc[self.seatsRepartitionPerList['ListName']==tempList,'Total Seats'].values[0]>0 and tempReligion==tempReligionJ and tempDa2ira==tempDa2iraJ and self.listOfRitesDF.loc[j,'Seats']>0:
                    self.seatsRepartitionPerList.loc[self.seatsRepartitionPerList['ListName']==tempList,'Total Seats']-=1     #minus 1 for the counter for the number of seats per list
                    self.listOfRitesDF.loc[j,'Seats']-=1 #minus 1 for the counter for the number of seats per religion+da2ira soghra 
                    WinLossValue='Winner'   #mark the corresponding candidate as a winner
                    WinLoss.append(WinLossValue)    #add the corresponding winner to the winners+losers list
                elif (self.seatsRepartitionPerList.loc[self.seatsRepartitionPerList['ListName']==tempList,'Total Seats'].values[0]<=0 or self.listOfRitesDF.loc[j,'Seats']<=0)and tempReligion==tempReligionJ and tempDa2ira==tempDa2iraJ : #if one of the counters of the number of seats left per list or the numbers of seats left per religion+da2ira soghra reaches 0, add the corresponding candidate to the losers list
                    WinLossValue='Loser'    #mark the corresponding candidate as a loser
                    WinLoss.append(WinLossValue)    #add the corresponding loser to the winners+losers list
        votesDF['Win/Loss']=WinLoss            #add the list of WinLoss as a new column in the votesDF
        
        emptyDF = pd.DataFrame({'':[]})  #creates a DF with an empty column
        votesDF = pd.concat([self.votesResultsDF['Da2ira'],emptyDF,self.listExtraVotesDF['ListName'],self.listExtraVotesDF['ListExtraVote'],emptyDF, votesDF, emptyDF, totalVotesNoBlankDF, emptyDF, haselDF], axis=1)    #output DF form of the election results
        
        votesDF.to_csv(self.electionResultsFile, index=False, encoding='utf-8-sig')    #write DF to a csv file

KesJbeil2=electionResultsGen('Kes-Jbeiltest2.csv')
KesJbeil2.getResults()
KesJbeil3=electionResultsGen('Kes-Jbeiltest3.csv')
KesJbeil3.getResults()