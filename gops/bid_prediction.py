import math
import random

class Strategy:

    def __init__(self, turn: int, prize: int, bid_diff: int):
        self.turn = turn
        self.prize = prize
        self.bid_diff = bid_diff

    def get_strategy(self):
        return (self.turn, self.prize, self.bid_diff)
    
class StrategyCollection:

    def __init__(self):
        self.collection = None
        self.min_prize = 1
        self.max_prize = 13
        self._init_collection()

    def _get_key(self, turn, prize):
        return str(turn) + "|" + str(prize)
    
    def _get_base_strat_prob(self, cturn, cprize, strat):
            dturn = cturn - strat.turn
            dprize = abs(cprize - strat.prize)
            return math.exp(-(dturn + dprize))

    def _get_norm_constant(self, cturn, cprize):
        norm_const = 0
        for key in self.collection.keys():
            strat = self.collection[key]
            norm_const += self._get_base_strat_prob(cturn, cprize, strat)
        return norm_const

    def _init_collection(self):
        turn = 0
        bid_diff = 0
        self.collection = {}
        for x in range(self.min_prize, self.max_prize + 1):
            strat = Strategy(turn, x, bid_diff)
            key = self._get_key(turn, x)
            self.collection[key] = strat

    def add_strategy(self, new_strat):
        key = self._get_key(new_strat.turn, new_strat.prize)
        self.collection[key] = new_strat

    def _get_strat_prob(self, cturn, cprize, strat, norm_const):
        base_prob = self._get_base_strat_prob(cturn, cprize, strat)
        norm_prob = base_prob / norm_const
        return norm_prob

    def predicted_strategy(self, cturn, cprize):
        norm_const = self._get_norm_constant(cturn, cprize)
        rand = random.random()

        total_prob = 0
        for key in self.collection.keys():
            strat = self.collection[key]
            norm_prob = self._get_strat_prob(cturn, cprize, strat, norm_const)
            total_prob += norm_prob

            if rand <= total_prob:
                return strat

#############################################################3

# NOTE: This function probably needs to be adjusted
def get_player_bid_efficiency(r, bo, bpvec):
    c = 3.5
    mval = -1
    mdx = None
    ea = []
    for idx, b in enumerate(bpvec):
        if b > bo:
            term = (r*c) / math.log2(1+b+bo)
        elif b == bo:
            term = 0
        else:
            term = bo-b
        ea.append(term)
        if term > mval:
            mval = term
            mdx = idx + 1
    return ea, mdx, mval
