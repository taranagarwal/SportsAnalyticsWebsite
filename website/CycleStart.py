#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 16:42:05 2024

@author: dylanshih
"""
from .LinearWeights import LinearWeights
from .PTM import PTM
import numpy as np
import pandas as pd

class CycleStart:
    

    def __init__(self, lineup, players):
        self.l = LinearWeights(players)
        self.lineup = lineup
        df = pd.read_csv("ExtraABs.csv")
        self.probs = list(df['%ExtraABs'])
        self.lw = LinearWeights(players)
        self.weights = np.array(list(self.lw.get_linearWeights().values()))
        
    #subset of lineup where last player is the player of interest
    def FindNRL(self, lineup):
        #PTM[0] * updated linear weights
        ptm1 = lineup[0][2]
        NREzero = np.matmul(ptm1[0], self.weights) #linearweights
        subline = [lineup[-3], lineup[-2], lineup[-1], lineup[0]]
        avgNRE = self.AvgNRE(subline)
    
        return avgNRE - NREzero
    
    def FindNRL2(self, lineup):
        player_1 = lineup[0]
        player_2 = lineup[1]
        ptm = player_2[2]
        NREzeroOne = np.matmul(np.matmul(player_1[2][0], ptm), self.weights)
        subline = [lineup[-2], lineup[-1], lineup[0], lineup[1]]
        avgNRE = self.AvgNRE(subline)
        
        #NRL2 is negative !!!, means there's a BENEFIT to batters hitting 2nd in the lineup, my guess is lowest RE are in the two out states
        
        return avgNRE - NREzeroOne
    
    def FindNRL3(self, lineup):
        player_1 = lineup[0]
        player_2 = lineup[1]
        player_3 = lineup[2]
        NREzeroOneTwo = np.matmul( np.matmul( np.matmul(player_1[2][0], player_2[2]) , player_3[2]) , self.weights)
        subline = [lineup[-1], lineup[0], lineup[1], lineup[2]]
        avgNRE = self.AvgNRE(subline)
        
        return avgNRE - NREzeroOneTwo
            
    #take in input of 4 players to calculate run expectancy
    def AvgNRE(self, subline):
        score = self.l.getRunExpectancyBOS(subline)
        return score
        
    def NetRunsGained(self, lineup):
        #probs = [p1, p2, p3, p4, p5, p6, p7, p8, p9]
        NRG = 0
        for i in range(0, 9):
            subline = [lineup[i-3], lineup[i-2], lineup[i-1], lineup[i]]
            #problem is that we need a new lineup to put in for average runs expected
            #if we input subline it could be easier?
            NRG += self.AvgNRE(subline) * self.probs[i]
        return NRG - self.FindNRL(lineup) - self.FindNRL2(lineup) - self.FindNRL3(lineup)
    
    def StartCycle(self):
        lp = self.lineup
        #iterate through every possible combo of lineups, append to list
        lineupList = [lp]
        
        for i in range(0, 8):
            temp = lp[0]
            lp.pop(0)
            lp.append(temp)
            name = [item for item in lp]
            lineupList.append(name)
        
        
        #for every lineup calculate score and append to a dictionary, then find max of it
        lNames = []
        lVals = np.empty(9)
        c = 0
        for l in lineupList:
            temp = []
            for item in l:
                temp.append((item[0], item[4]))
            lNames.append(temp)
            lVals[c] = self.NetRunsGained(l)
            c+=1
        lineup1 = lNames.pop(lVals.argmax())
        lineup2 = lNames.pop(lVals.argmax())
        lineup3 = lNames.pop(lVals.argmax())
        return [lineup1, lineup2, lineup3]
    
    

    

    