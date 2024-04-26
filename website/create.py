import numpy as np
import pandas as pd
import heapq
from itertools import permutations
import typing
from tqdm import tqdm

from .LinearWeights import LinearWeights as LW
from .PTM import PTM
from .structures import Node, NewNode

class Create():
    """
    Class responsible for creating hypergroups, lineups, and retrieving best lineups

    self.hypergroups : should end up being a List of 3024 elements, each element is a List of 4 subelements, each subelement is a List with
                       a player_name in the first index and corresponding PTM in the second index
    """
    def __init__(self, players, DataAgent : PTM, hypergroup_size : int = 4):
        self.players = players
        self.DataAgent = DataAgent
        self.hypergroup_size = hypergroup_size

        self.player_names = self.DataAgent.player_names
        self.ptms = self.DataAgent.ptm_list
        self.players_and_ptms = [[self.player_names[i], self.ptms[i]] for i in range(0, len(self.player_names))]

        self.subline = self.DataAgent.build_player_objects()

        self.hypergroups = self.create_all_hypergroups(self.subline)

        self.all_nodes = self.create_newnodes(self.hypergroups, self.players_and_ptms)
        self.nodes_map = {tuple(node.players): node for node in self.all_nodes}

        self.topk, self.topuniquek = self.find_top_k_scores(self.player_names, self.nodes_map, self.hypergroup_size)
        
    def allHyperNodes(self, to_scramble, length, tempArr = []):
        """
        Create all permutations of to_scramble of size length

        to_scramble: List : For our purposes, a list of size 9 containing player names to permutate
        length: int : get all permutations of size 4 using players from to_scramble
        """
        if (len(tempArr) == length):
            return [tempArr]
        ans = []
        for i,j in enumerate(to_scramble):
            newTemp = tempArr.copy()
            newTemp.append(j)
            newScramble = to_scramble[:i] + to_scramble[i+1:]
            ans += self.allHyperNodes(newScramble, length, newTemp)
        return ans

    def get_every_group(self, players):
        """
        Given a list of players, return all permutations of those players in groups of size k
        
        players : players_and_ptms should be passed in here 

        return : List[str, np.array(List[List[]])] s.t. index 0 = name, index 1 = PTM 
        """
        k = self.hypergroup_size
        trees_for_each = self.allHyperNodes(players, k)
        all_hypergroups = [[i for i in hg] for hg in trees_for_each] # only player names for now 
        return all_hypergroups
    
    def create_all_hypergroups(self, permute):
        """
        Create and return all hypergroups of size 9P(hypergroup_size)
        """
        return self.get_every_group(permute)
    
    def create_directory(self):
        """
        directory: keys are NewNode, values are tuple of NewNodes
        **** This function is deprecated ****
        """
        all_hypergroups = self.hypergroups
        players_with_ptm = self.players_and_ptms

        directory = {}
        
        for idx in tqdm(range(0, len(all_hypergroups))):
            start_root = all_hypergroups[idx]
            root = Node(start_root, self.players) 
            picked_player_names = [i[0] for i in start_root]
            new_root = NewNode(picked_player_names, root.weight)
            directory[new_root] = []
            
            unpicked = [hypergroup for hypergroup in players_with_ptm if hypergroup[0] not in picked_player_names]
            next_node = start_root[1:]
            for new_node in unpicked:
                next_node.append(new_node) 
                weight_node = Node(next_node, self.players)
                new_direct_node = NewNode([i[0] for i in next_node], weight_node.weight)
                directory[new_root].append(new_direct_node)
                next_node.pop()
                
        return directory
    
    def create_newnodes(self, all_hypergroups, players_with_ptm):
        """
        Create new nodes for 8! create algo 
        """
        all_hypergroups = self.hypergroups
        players_with_ptm = self.players_and_ptms

        nodes = []
        for idx in tqdm(range(0, len(all_hypergroups))):
            start_root = all_hypergroups[idx]
            root = Node(start_root, self.players)
            nodes.append(NewNode([i[0] for i in start_root], root.weight))
        
        return nodes
    
    def calculate_score(self, ordering, nodes_map):
        """Calculate the score for a given ordering."""
        score = 0
        # loop through the ordering in steps to get each unique group of 4 players
        for i in range(len(ordering) - 4): # will be range(6 - 3) = range(3)
            current_group = tuple(ordering[i:i+4])
            next_group = tuple(ordering[i+1:i+5]) 
    #         print(f'current: {current_group}, next: {next_group}')
            
            current_node = nodes_map[current_group]
            next_node = nodes_map[next_group]
            
            if current_node and next_node:
                #score += next_node.value - current_node.value
                score+=next_node.value
        return score
    
    def find_top_k_scores(self, players, nodes_map, k):
        """
        players: list of 9 player names 
        nodes_map: map of all uniquely ordered subsets of 4 
        """
        heap1 = []  # min heap to store the top k scores
        heap2 = [] # min heap for unique first nodes; this is currently broken 
        seen_nodes = set()
        
        # fix one player and generate 8! permutations of the rest
        fixed_player = players[0]
        best_score = -10000
        best_ordering = None
        for perm in permutations(players[1:], len(players)-1):
            ordering = [fixed_player] + list(perm) + [fixed_player] + list(perm)[0:2]
            score = self.calculate_score(ordering, nodes_map)
            
            if score > best_score:
                best_score = score
                best_ordering = ordering
        
            heapq.heappush(heap1, (score, ordering))
            if len(heap1) > k:
                heapq.heappop(heap1)
                
            first_node = tuple(ordering[:4])
            if first_node not in seen_nodes:
                seen_nodes.add(first_node)
                heapq.heappush(heap2, (-score, ordering))
            
            if len(heap2) > k:
                heapq.heappop(heap2)
        
        topk = [(score, ordering) for score, ordering in heap1]
        topuniquek = [(-score, ordering) for score, ordering in heap2]
        # print(best_score)
        # print(best_ordering[0:9])
        return topk, topuniquek
