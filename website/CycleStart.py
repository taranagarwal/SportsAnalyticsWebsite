#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 16:42:05 2024

@author: dylanshih
"""
from LinearWeights import LinearWeights
from PTM import PTM
import numpy as np
import pandas as pd

class CycleStart:
    def __init__(self, lineup):
        self.lineup = lineup
        df = pd.read_csv("ExtraABs.csv")
        self.probs = list(df['%ExtraABs'])
        self.lw = LinearWeights()
        self.weights = np.array(list(self.lw.get_linearWeights().values()))
        
    def FindNRL(self, player):
        #PTM[0] * updated linear weights
        ptm1 = player[2]
        NREzero = np.matmul(ptm1[0], self.weights) #linearweights
        avgNRE = self.AvgNRE(player)
        
    
        return avgNRE - NREzero
    
    def FindNRL2(self, player):
        ptm = player[2]
        NREzeroOne = (np.matmul(ptm[0], self.weights) + np.matmul(ptm[1], self.weights) + np.matmul(ptm[2], self.weights)
                      + np.matmul(ptm[3], self.weights)+ np.matmul(ptm[9], self.weights))/5
        avgNRE = self.AvgNRE(player)
        
        #NRL2 is negative !!!, means there's a BENEFIT to batters hitting 2nd in the lineup, my guess is lowest RE are in the two out states
        
        return avgNRE - NREzeroOne
    
    #def FindNRL3(self, player)
        
            
    def AvgNRE(self, player):
        ptm = player[2]
        totalNRE = 0
        for i in range(0, 24):
            totalNRE += np.matmul(ptm[i], self.weights) #linear weights
        
        return totalNRE/24
        
    def NetRunsGained(self, lineup):
        #probs = [p1, p2, p3, p4, p5, p6, p7, p8, p9]
        NRG = 0
        for i in range(0, 9):
            player = lineup[i]
            NRG += self.AvgNRE(player) * self.probs[i]
        return NRG - self.FindNRL(lineup[0]) - self.FindNRL2(lineup[1])
    
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
            name = [item[0] for item in l]
            lNames.append(name)
            lVals[c] = self.NetRunsGained(l)
            c+=1
        
        return lNames[lVals.argmax()]
        
        
if __name__ == "__main__":
    p = PTM("WBCValidation.csv")
    PTMs = p.build_player_objects()
    c = CycleStart(PTMs)
    print(c.StartCycle())
    
    

    

    