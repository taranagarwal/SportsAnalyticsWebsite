#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 14:22:43 2024

@author: dylanshih

"""

import pandas as pd
import numpy as np
from .PTM import PTM


class LinearWeights:

    def __init__(self, players):
        self.p = PTM(players)
        
    def get_linearWeights(self):
        #get the linear weights aka expected run values of each base-out state
        df5 = pd.read_csv('lin_weights_RE.csv')
        df5 = df5.iloc[:, [0]]
        df5 = df5.to_dict()
        df5 = df5['0']
        return df5
    
    def calc_actualRuns(self, startState, endState, N):
        if endState != 25:
            if startState == 0:
                startRunners = 0
            elif startState%8 == 0:
                #if startState Mod 8 is zero then we are in bases loaded state
                startRunners = 8
            elif startState%8 != 0:
                #we mod 8 to get rid of outs (basically saying state 1 is equal to state 9 since both represent no runners on base but 9 has one out and 1 has zero outs)
                startRunners = endState%8; 
                
            if endState == 0:
                endRunners = 0
            elif endState%8 == 0:
                #same as above but just using end state
                endRunners = 8;
            elif endState%8 != 0:
                #same as above but just using end state
                endRunners = endState%8;
            #outs calc example: state = 9, state of runners = 1 (represents no runners) (9-1)/8 = 1 outs
            endOut = (endState - endRunners)/8
            startOut = (startState - startRunners)/8
            #1/3 = 0, 2/3, 3/3, 4/3 = 1, 5/3, 6/3, 7/3 = 2, 8/3 = 3 so it works out
            numEndRunners = round(endRunners/3)
            numStartRunners = round(startRunners/3)
            '''the actual runs scored is N (number of people in hypergroup) minus
                the number of people that end on the bases plus the number of people that
                start on the bases minus the end number of outs plus the start number of outs
                Basically this equation is tracking where the runners went during this hypergroup of 4
                since runners either get out, get on base, or score'''
            R = N - (numEndRunners-numStartRunners) - (endOut-startOut);
            if R < 0:
                return 0
            return R

        else:
            return 0
        
    def getRunExpectancyBOS(self, subline, boSTATE = [0, 0, 0]): #subline is a list of size 4, with components A,B,C 
                                                    #A,B,...,I: player_name, hit_probs, ptm
                                                    #boSTATE should be default [0,0,0]
        #build actual runs 
        actualRunList1 = []
        actualRunList2 = []
        actualRunList3 = []
        actualRunList4 = []

        #for each base out state we calculate the number of actual runs that are scored given i batters
        for i in range(1, 26):
            actualRunList1.append(self.calc_actualRuns(boSTATE[0], i, 1));
        for i in range(1, 26):
            actualRunList2.append(self.calc_actualRuns(boSTATE[0], i, 2));
        for i in range(1, 26):
            actualRunList3.append(self.calc_actualRuns(boSTATE[0], i, 3));
        for i in range(1, 26):
            actualRunList4.append(self.calc_actualRuns(boSTATE[0], i, len(subline)));

        actualRuns1 = np.array(actualRunList1)
        actualRuns2 = np.array(actualRunList2)
        actualRuns3 = np.array(actualRunList3)
        actualRuns4 = np.array(actualRunList4)

        #setting up the linear weights
#         self.placeHolder = self.get_linearWeights()
        rew0 = np.array(list(self.get_linearWeights().values()))

        abc_dict={}
        
        #change rew to actual runs - rew0 cuz the expected runs would have scored anyways when in that state
        #rew SHOULD Be finished state - initial state + actual runs evaluated at each time step?
        
        #rew1 = np.abs(rew0 - actualRuns1)
        #rew2 = np.abs(rew0 - actualRuns2)
        #rew3 = np.abs(rew0 - actualRuns3)
        #rew4 = np.abs(rew0 - actualRuns4)

        rew1 = rew0 - rew0[0] + actualRuns1
        

        #we get the player "objects" here
        first_player = subline[0]
        second_player = subline[1]
        third_player = subline[2]
        fourth_player = subline[3]
        
        REi = []
        REf = []
        NRE = 0

#         [abcd, abc, bcd, bc, cd, d]

        #steal_perc = steal_dict[first_player[0]] #to be defined

        #get PTM of first player at that base out state
        ptm1 = first_player[2]
        ptm1 = ptm1[boSTATE[0]]
        ptm4 = fourth_player[2]
        
        

        #calculate probability matrix of going from initial state to end state using 
#        matrix multiplication with player 1 starting the inning
        speed_4_players = [first_player[3], second_player[3], third_player[3]]
        for i in range(1, len(subline)-1):
            if i == 1:
                speed_player_1 = [0, 0, first_player[3]]
                next_player = subline[i]
                next_ptm = self.p.adjusted_PTM(speed_factors=speed_player_1, player=next_player)
                ptm1 = np.matmul(ptm1, next_ptm)
            if i == 2:
                speed_player_2 = [0, first_player[3], second_player[3]]
                next_player=subline[i]
                next_ptm = self.p.adjusted_PTM(speed_player_2, next_player)

        abcd_score = 0
        abcd_ptm = self.p.adjusted_PTM(speed_4_players, fourth_player)
        #manual computation of run value
        for i in range(0, len(abcd_ptm)):
            for j in range(0, len(ptm1)):
                abcd_score += ptm1[j]*abcd_ptm[j][i]*(rew0[i]-rew0[j] + self.calc_actualRuns(j, i, 1))

        
        #REi = initial run expectancy, REf = final run expectancy
        #basically we're saying what is the net added runs of player 4 given that
        #inning starts with player 1 batting
        #REi.append(np.matmul(ptm1, rew3))
        #REf.append(np.matmul(np.matmul(ptm1, self.p.adjusted_PTM(speed_4_players, fourth_player)), rew4))
        REf.append(abcd_score)

        ptm2 = second_player[2]
        ptm2 = ptm2[boSTATE[0]]

        speed_B = [0,0,second_player[3]]
        speed_B_C = [0, second_player[3], third_player[3]]

        bcd_score = 0
        ptm2 = np.matmul(ptm2, self.p.adjusted_PTM(speed_B, third_player))
        bcd_ptm = self.p.adjusted_PTM(speed_B_C, fourth_player)

        for i in range(0, len(bcd_ptm)):
            for j in range(0, len(ptm2)):
                bcd_score += ptm2[j]*bcd_ptm[j][i]*(rew0[i]-rew0[j] + self.calc_actualRuns(j, i, 1))

        
        #same as above except this time it's with player 2 starting the inning
        #REi.append(np.matmul(np.matmul(ptm2, self.p.adjusted_PTM(speed_B, third_player)), rew2))
        #REf.append(np.matmul(np.matmul(np.matmul(ptm2, self.p.adjusted_PTM(speed_B, third_player)), self.p.adjusted_PTM(speed_B_C, fourth_player)), rew3))
        REf.append(bcd_score)


        ptm3 = third_player[2]
        ptm3 = ptm3[boSTATE[0]]

        cd_score = 0
        cd_ptm = self.p.adjusted_PTM([0, 0, third_player[3]], fourth_player)

        for i in range(0, len(cd_ptm)):
            for j in range(0, len(ptm3)):
                cd_score += ptm3[j]*cd_ptm[j][i]*(rew0[i]-rew0[j] + self.calc_actualRuns(j, i, 1))

        #same as above but it's with player 3 batting
        #REi.append(np.matmul(ptm3, rew0))
        #REf.append(np.matmul(np.matmul(ptm3, self.p.adjusted_PTM([0, 0, third_player[3]], fourth_player)), rew2))
        REf.append(cd_score)
        #player 4's individual run contribution if he starts the inning
        #REi.append(0)
        
        d_score = np.matmul(ptm4[boSTATE[0]], rew1)
        REf.append(d_score)

#         print(f'PTM4, rew: {ptm4.shape} , {rew.shape}')

#         print(f'- {i} - : {REf}, {REi}')
        TRE = 0

        for i in range(0, len(REf)):
#             print(f'inside sum: {(REf[i] - REi[i]) / 4}')
            TRE += REf[i] / 4
            #NRE += (REf[i] - REi[i]) / 4
#         print(f'FUNC : {NRE}')
        # print(REi)
        #print(REf)

        return TRE
    
