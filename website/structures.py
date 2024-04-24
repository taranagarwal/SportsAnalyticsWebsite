import numpy as np
import pandas as pd
import heapq
from itertools import permutations
from typing import List

from LinearWeights import LinearWeights
from PTM import PTM

"""
This file contains data structures relevant to creating hypergroups and exploring cycles. 
"""

class Node():
    """
    Initialize a node that computes 

    players_with_ptms : List[List[str, List[List]]]
    """
    def __init__(self, players_with_ptms : List):
        self.players_with_ptms = players_with_ptms
        LW = LinearWeights()
        self.weight = LW.getRunExpectancyBOS(self.players_with_ptms)


class NewNode:
    def __init__(self, players, value=None, parent=None):
        self.players = players
        self.parent = parent
        self.value = value

    def calc_edge_weight(self):
        if (self.parent != None):
            return self.value - self.parent.value
        else:
            return -1000