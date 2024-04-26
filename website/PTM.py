#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 14:26:30 2024

@author: Credit goes to ashwin

"""
import numpy as np
import pandas as pd
import os
from sklearn.preprocessing import normalize

class PTM:
    def __init__(self, players):
       self.players = players
       data = {
           "Unnamed: 0": list(range(9)),
           "Rk": list(range(1, 10)),
           "Pos": [player.pos for player in players],
           "Name": [p.player for p in players],
           "Age": [p.age for p in players],
           "G": [p.g for p in players],
           "PA": [p.pa for p in players],
           "AB": [p.ab for p in players],
           "R": [p.r for p in players],
           "H": [p.h for p in players],
           "2B": [p.twoB for p in players],
           "3B": [p.threeB for p in players],
           "HR": [p.hr for p in players],
           "RBI": [p.rbi for p in players],
           "SB": [p.sb for p in players],
           "CS": [p.cs for p in players],
           "BB": [p.bb for p in players],
           "SO": [p.so for p in players],
           "BA": [p.ba for p in players],
           "OBP": [p.obp for p in players],
           "SLG": [p.slg for p in players],
           "OPS": [p.ops for p in players],
           "OPS+": [p.opsPlus for p in players],
           "TB": [p.tb for p in players],
           "GDP": [p.gdp for p in players],
           "HBP": [p.hbp for p in players],
           "SH": [p.sh for p in players],
           "SF": [p.sf for p in players],
           "IBB": [p.ibb for p in players],
           "SpF": [p.spf for p in players]
        }
       self.data_rates = pd.DataFrame(data)
       self.player_names = self.lineup()
       self.speed_factor = self.calc_speed_factor()
       self.ptm_list = [self.generate_probability_matrix_real(self.data_rates, name) for name in self.player_names]
    
    #Building and cleaning data
#    def fix_event_classification(self, data):
#        event = data["woba_value"]
#        event = event.replace(2, 4)
#        event = event.replace(1.25, 2)
#        event = event.replace(0.9, 1)
#        event = event.replace(1.6, 3)
#        event = event.replace(0.7, 0)
#        data["total_bases"] = event
#        return data
    
    def fix_names(self, name):
        index = [name.find('#'), name.find('\\'), name.find('*'), name.find('+')]
        filtered = [i for i in index if i >= 0]
        if len(filtered) <= 0:
            return name
        loc = min(filtered)
        spliced = name[0:loc].split(" ", 1)
        new = f"{spliced[1]}, {spliced[0]}"
        return new
    
    #def build_all_data(self):
        path = os.getcwd()
        data = []
        for file in os.listdir(path):
            if(os.path.isfile(os.path.join(path, file))):
                if file.endswith(".csv") and "4" not in file and "orioles" not in file: 
                    print(os.path.join(path, file))
                    df = pd.read_csv(filepath_or_buffer=os.path.join(path, file), header=0)
                    data.append(df)
        dataframe = pd.concat(data, ignore_index = True)
        #dataframe = self.fix_event_classification(dataframe)
        return dataframe
    
    def get_real_outcome_in_play_distribution(self, data, player_name):
        data_for_player = self.data_rates[self.data_rates["Name"] == player_name]
        pa = data_for_player.PA.iloc[0]
        h = data_for_player.H.iloc[0]
        doubles = data_for_player["2B"].iloc[0]
        triples = data_for_player["3B"].iloc[0]
        hr = data_for_player["HR"].iloc[0]
        so = data_for_player["SO"].iloc[0]
        bb = data_for_player["BB"].iloc[0] + data_for_player["IBB"].iloc[0]
        singles = h - doubles - triples - hr
        out = pa - h - so - bb
        
        hit_distribution = pd.Series({"single": singles/pa, 
                                      "double": doubles/pa,
                                      "triple": triples/pa,
                                      "home_run": hr/pa,
                                     "out": out/pa})
        return hit_distribution/sum(hit_distribution)
    
    #building player transition matrices
    def get_values_for_player_real(self, data, player):
        bbper, soper, bip = self.get_walk_and_strikeout_rate(player)
        outcome = self.get_real_outcome_in_play_distribution(data, player)
        return bbper, soper, bip, outcome
    
    def get_walk_and_strikeout_rate(self, player_name):
        try:
            data_for_player = self.data_rates[self.data_rates["Name"] == player_name]
            pa = data_for_player["PA"].iloc[0]
            so = data_for_player["SO"].iloc[0]
            bb = data_for_player["BB"].iloc[0] + data_for_player["IBB"].iloc[0]
        except:
            print(f"probably a player name issue: {player_name}")
        bip = pa - bb - so
        bb_percent = bb/pa
        so_percent = so/pa
        bip_percent = bip/pa
        return [bb_percent, so_percent, bip_percent]
    
    def generate_a_matrix_bb(self, bbper, soper, bip, outcome):
        out = outcome.loc["out"]*bip
        hr = outcome.loc["home_run"]*bip
        single = outcome.loc["single"]*bip
        double = outcome.loc["double"]*bip
        triple = outcome.loc["triple"]*bip
        
        state_1 = [hr, hr, hr, hr, hr, hr, hr, hr]
        state_2 = [single+bbper, 0, single, single, 0, 0, single, 0]
        state_3 = [double, 0, double, double, 0, 0, double, 0]
        state_4 = [triple, triple, triple, triple, triple, triple, triple, triple]
        state_5 = [0, single+bbper, bbper, 0, single, single, 0, single]
        state_6 = [0, 0, 0, bbper, 0, 0, 0, 0]
        state_7 = [0, double, 0, 0, double, double, 0, double]
        state_8 = [0, 0, 0, 0, bbper, bbper, bbper, bbper]
        
        a_matrix = pd.DataFrame({'state 1': state_1, 
                                  'state_2': state_2,
                                  'state_3': state_3,
                                  'state_4': state_4,
                                  'state_5': state_5,
                                  'state_6': state_6,
                                  'state_7': state_7,
                                  'state_8': state_8})
        a_matrix.index = a_matrix.columns
        
        return a_matrix
    
    
    def generate_b_matrix_bb(self, soper, bip, outcome):
        out = outcome.loc["out"]*bip+soper
        b_matrix = np.zeros((8, 8))
        np.fill_diagonal(b_matrix, out+soper)
        b_matrix = pd.DataFrame(b_matrix)
    #     b_matrix.columns = state_names
    #     b_matrix.index = b_matrix.columns
        return b_matrix
    
    def generate_c_matrix_bb(self):
        c_matrix = np.zeros((8,8))
        c_matrix[1][0] = .023529
        c_matrix[2][0] = .023529
        c_matrix[3][0] = .023529
        return c_matrix
    
    def generate_d_matrix(self):
        d_matrix = np.array([[0, 0, 0, 0, 1, 1, 1, 1]]).transpose()*0.000049
        return d_matrix
    
    def generate_e_matrix_bb(self):
        e_matrix = np.array([[0, 1, 1, 1, 0, 0, 0, 0]]).transpose()*.023529
        return e_matrix
    
    def generate_f_matrix_bb(self, soper, bip, outcome):
        """
        For the real distribution, we can just pass 1 for bip and then feed in the true probabilities
        """
        out = outcome.loc["out"]*bip+soper
        f_matrix = np.zeros((1, 8))+out
        return f_matrix.transpose()
    
    
    def generate_probability_matrix_real(self, data, player):
        bbper, soper, bip, outcome = self.get_values_for_player_real(data, player)
        a_matrix = self.generate_a_matrix_bb(bbper, soper, bip, outcome).to_numpy()
        b_matrix = self.generate_b_matrix_bb(soper, bip, outcome).to_numpy()
        c_matrix = self.generate_c_matrix_bb()
        d_matrix = self.generate_d_matrix()
        e_matrix = self.generate_e_matrix_bb()
        f_matrix = self.generate_f_matrix_bb(soper, bip, outcome)
        zero_block = np.zeros((8,8))    
        zero_list = np.zeros((1, 8))
        probability_matrix = np.block([
            [a_matrix, b_matrix, c_matrix, d_matrix],
            [zero_block, a_matrix, b_matrix, e_matrix],
            [zero_block, zero_block, a_matrix, f_matrix],
            [zero_list, zero_list, zero_list, 1]
        ])
        normed_matrix = normalize(probability_matrix, axis=1, norm='l1')
        return normed_matrix
    
    def lineup(self):
        return self.data_rates['Name'][0:9]
    
    def lineup_prob(self):
        l_p = []
        for i in range(9):
            l_p.append(self.get_real_outcome_in_play_distribution(self.data_rates, self.player_names[i]))
        return l_p
        # lineup_prob
        
    def build_player_objects(self):
        players = []
        for i in range(0,9):
            players.append([self.player_names[i], self.lineup_prob()[i].to_numpy(), self.ptm_list[i], self.speed_factor[i], self.players[i].id])
        
        for i in range(0, len(players)):
            players[i][2] = self.steals_adjustment(players[i])
            
        return players
    
    def calc_speed_factor(self):
        return self.data_rates["SpF"][0:9]*0.01
    
    def adjusted_PTM(self, speed_factors, player):
        #speed_factors is list of SF of the three batters batting in front
        #player is current player object
        #let's make everything a function of the lead runner
        PTM = player[2]
        x = speed_factors[2]
        y = speed_factors[1]
        z = speed_factors[0]
        
        #0 outs, Runner on 1st starting state
        
        PTM[1][4] = player[1][0]*(1-((x-0.5)*0.4 + 0.3))+self.get_walk_and_strikeout_rate(player[0])[0] #from first to second on a single
        PTM[1][5] = player[1][0]*(((x-0.5)*0.4 + 0.3)) #from first to third on a single
        
        #0 outs, Runner on 2nd starting state
        PTM[2][1] = player[1][0]*((x-0.5)*0.4 + 0.6) #from second to home on a single
        PTM[2][5] = player[1][0]*(1-((x-0.5)*0.4 + 0.6)) #from second to third on a single


        #0 outs, runners first and second
        PTM[4][5] = player[1][0]*((x-0.5)*0.4 + 0.6) # from first and second to first and third on a single
        PTM[4][7] = player[1][0]*(1-((x-0.5)*0.4 + 0.6)) + self.get_walk_and_strikeout_rate(player[0])[0] # from first and second to bases loaded on a single
        
        #0 outs, runners first and third
        PTM[5][4] = player[1][0]*(1-((y-0.5)*0.4 + 0.3)) #from first and third to first and second on a single
        PTM[5][5] = player[1][0]*((y-0.5)*0.4 + 0.3) #from first and third to first and third on a single
        
        #0 outs, runners on second and third
        PTM[6][1] = player[1][0]*((y-0.5)*0.4 + 0.6) #from second and third to first on a single
        PTM[6][5] = player[1][0]*(1-((y-0.5)*0.4 + 0.6)) #from second and third to first and third on a single
        
        #0 outs, bases loaded
        PTM[7][5] = player[1][0]*((y-0.5)*0.4 + 0.6) #from bases loaded to first and third on a single
        PTM[7][7] = player[1][0]*(1-((y-0.5)*0.4 + 0.6))+self.get_walk_and_strikeout_rate(player[0])[0] #from bases loaded to bases loaded on a single   
        
        #----------------------------------------------------------------------------
        
        #1 outs, Runner on 1st starting state --> +8, +8
        PTM[9][12] = player[1][0]*(1-((x-0.5)*0.4 + 0.3))+self.get_walk_and_strikeout_rate(player[0])[0] #from first to second on a single
        PTM[9][13] = player[1][0]*(((x-0.5)*0.4 + 0.3)) #from first to third on a single
        
        #1 outs, Runner on 2nd starting state
        PTM[10][9] = player[1][0]*((x-0.5)*0.4 + 0.6) #from second to home on a single
        PTM[10][13] = player[1][0]*(1-((x-0.5)*0.4 + 0.6)) #from second to third on a single


        #1 outs, runners first and second
        PTM[12][13] = player[1][0]*((x-0.5)*0.4 + 0.6) # from first and second to first and third on a single
        PTM[12][15] = player[1][0]*(1-((x-0.5)*0.4 + 0.6)) + self.get_walk_and_strikeout_rate(player[0])[0] # from first and second to bases loaded on a single
        
        #1 outs, runners first and third
        PTM[13][12] = player[1][0]*(1-((y-0.5)*0.4 + 0.3)) #from first and third to first and second on a single
        PTM[13][13] = player[1][0]*((y-0.5)*0.4 + 0.3) #from first and third to first and third on a single
        
        #1 outs, runners on second and third
        PTM[14][9] = player[1][0]*((y-0.5)*0.4 + 0.6) #from second and third to first on a single
        PTM[14][13] = player[1][0]*(1-((y-0.5)*0.4 + 0.6)) #from second and third to first and third on a single
        
        #1 outs, bases loaded
        PTM[15][13] = player[1][0]*((y-0.5)*0.4 + 0.6) #from bases loaded to first and third on a single
        PTM[15][15] = player[1][0]*(1-((y-0.5)*0.4 + 0.6))+self.get_walk_and_strikeout_rate(player[0])[0] #from bases loaded to bases loaded on a single     
        
        #------------------------------------------------------------------------------
        
        #2 outs, Runner on 1st starting state
        PTM[17][20] = player[1][0]*(1-((x-0.5)*0.4 + 0.3))+self.get_walk_and_strikeout_rate(player[0])[0] #from first to second on a single
        PTM[17][21] = player[1][0]*(((x-0.5)*0.4 + 0.3)) #from first to third on a single
        
        #2 outs, Runner on 2nd starting state
        PTM[18][17] = player[1][0]*((x-0.5)*0.4 + 0.6) #from second to home on a single
        PTM[18][21] = player[1][0]*(1-((x-0.5)*0.4 + 0.6)) #from second to third on a single


        #2 outs, runners first and second
        PTM[20][21] = player[1][0]*((x-0.5)*0.4 + 0.6) # from first and second to first and third on a single
        PTM[20][23] = player[1][0]*(1-((x-0.5)*0.4 + 0.6)) + self.get_walk_and_strikeout_rate(player[0])[0] # from first and second to bases loaded on a single
        
        #2 outs, runners first and third
        PTM[21][20] = player[1][0]*(1-((y-0.5)*0.4 + 0.3)) #from first and third to first and second on a single
        PTM[21][21] = player[1][0]*((y-0.5)*0.4 + 0.3) #from first and third to first and third on a single
        
        #2 outs, runners on second and third
        PTM[22][17] = player[1][0]*((y-0.5)*0.4 + 0.6) #from second and third to first on a single
        PTM[22][21] = player[1][0]*(1-((y-0.5)*0.4 + 0.6)) #from second and third to first and third on a single
        
        #2 outs, bases loaded
        PTM[23][21] = player[1][0]*((y-0.5)*0.4 + 0.6) #from bases loaded to first and third on a single
        PTM[23][23] = player[1][0]*(1-((y-0.5)*0.4 + 0.6))+self.get_walk_and_strikeout_rate(player[0])[0] #from bases loaded to bases loaded on a single     
        
        
        return PTM

    def steals_adjustment(self, player):
        #proxy for MLB average steals rate is 0.72(2023 steals per game) / singles per game (around 5)
        PTM = player[2]
        SpF = player[3]
        
        #0 outs single
        PTM[0][1] = player[1][0]*(1-(SpF-0.5)*(0.72/5))
        PTM[0][2] = player[1][0]*((SpF-0.5)*(0.72/5)) + player[1][1]
        #1 out single
        PTM[8][9] = player[1][0]*(1-(SpF-0.5)*(0.72/5))
        PTM[8][10] = player[1][0]*((SpF-0.5)*(0.72/5)) + player[1][1]
        #2 outs single
        PTM[16][17] = player[1][0]*(1-(SpF-0.5)*(0.72/5))
        PTM[16][18] = player[1][0]*((SpF-0.5)*(0.72/5)) + player[1][1]

        return PTM