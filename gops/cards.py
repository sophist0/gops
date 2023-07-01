import random
import numpy as np

import gops.ui_elements as ui

class Card():
    def __init__(self, suit, val):
        self.ace="low"
        self._suit = suit
        self._val = val
        self.nval = self.get_num_value()

    # Move this to the card suit class
    def get_num_value(self):
        if isinstance(self._val, int):
            return int(self._val)
        elif self._val == "J":
            return 11
        elif self._val == "Q":
            return 12
        elif self._val == "K":
            return 13
        elif (self._val == "A") and (self.ace == "low"):
            return 1
        elif (self._val == "A") and (self.ace == "high"):
            return 14
        else:
            return None

    def value(self):
        return self._val

    def suit(self):
        return self._suit

    def display(self):
        print(ui.RVERT + str(self._val) + " " + self._suit + ui.LVERT)

class CardStack():
    def __init__(self, cards):
        self._order = cards

    def card_count(self):
        return len(self._order)

    def display_cards(self):
        for card in self._order:
            card.display()

    def shuffle(self):
        random.shuffle(self._order)

    def sort_cards(self, ace="Low"):
        self._order = sorted(self._order, key=lambda x: x.nval)

    def get_card_nvals(self):
        nvals = []
        for card in self._order:
            nvals.append(card.nval)
        return nvals

    def empty(self):
        if self.card_count() == 0:
            return True
        else:
            return False

    def card_in_stack(self, suit, val):
        in_stack = False
        card_loc = -1
        for card in self._order:
            card_loc += 1
            if (card.suit() == suit) and (card.value() == val):
                in_stack = True
                return in_stack, card_loc
        return in_stack, -1

class SuitCards(CardStack):
    def __init__(self, suit):
        values = [2,3,4,5,6,7,8,9,10,"J","Q","K","A"]
        self.suit = suit

        cards = []
        for value in values:
            card = Card(suit, value)
            cards.append(card)

        CardStack.__init__(self, cards)
        random.shuffle(self._order)

    def draw(self):
        return self._order.pop(0)

class Hand(SuitCards):
    def __init__(self, suit):
        SuitCards.__init__(self, suit)
        self.sort_cards()

    def select_random_card(self):
        selected = random.choice(range(self.card_count()))
        return self._order.pop(selected)

    def max_value(self):
        m = -1
        for card in self._order:
            if card.nval > m:
                m = card.nval
        return m

    def get_dist(self):
        # construct distribution
        card_prob = np.asarray([0 for x in range(self.card_count())])
        prob = self.card_count()
        for x in range(self.card_count()):
            card_prob[x] = prob
            prob -= (prob / 2) 
        return card_prob / sum(card_prob)


    def select_index(self):
        # select index based on distribution
        card_prob = self.get_dist()
        r = random.random()
        s = 0
        for x in range(self.card_count()):
            s += card_prob[x]
            if r <= s:
                return x

    def select_card_strategy_1(self, prize_value):
        # if prize_value < 7, select near min value vard.
        # else select card close to prize value.
        # TODO: Alg. assumes cards are sorted. Should check this!
        card_weight = self.get_card_nvals() 
        prob = self.card_count()
        if prize_value < 7:
            card_indexes = np.argsort(card_weight)
        else:
            if prize_value > 13:
                prize_value = 13
            card_weight = list(np.abs(np.asarray(card_weight) - prize_value))
            # bias towards higher values
            for idx, card in enumerate(self._order):
                if card.nval < prize_value:
                    card_weight[idx] = card_weight[idx] + 0.1

            card_indexes = np.argsort(card_weight)

        # I need to add logging
        # values = []
        # for card in self._order:
        #     values.append(card.value())
        # print()
        # print("prize_value: ",prize_value)
        # print("hand value")
        # print(values)
        # print("card_weight")
        # print(card_weight)
        # print()
        # print("card_indexes")
        # print(card_indexes)
        # print()

        index = self.select_index()
        # print("index: ",index)
        # print()
        card_loc = card_indexes[index]
        # print("card_loc_1: ",card_loc)

        # if prize is high and playing a lower value card, play the lowest value.
        # unless the value select is the maximum card value in the hand
        card_value = self._order[card_loc].nval
        if (prize_value >= 7) and (card_value < prize_value) and (card_value != self.max_value()):
            card_loc = 0 

        # print("card_loc_2: ",card_loc)
        # print()

        return self._order.pop(card_loc)

    def select_card(self, suit, val):
        in_stack, card_loc = self.card_in_stack(suit, val)
        if in_stack:
            return self._order.pop(card_loc)
        else:
            print()
            print("Card not in hand! Select another card.")
            print()
            return None

    def display_cards(self):
        print()
        print("Your Hand:")
        if len(self._order) <= 7:
            print("", end=ui.LVERT)
            for x in range(len(self._order)):
                card = self._order[x]
                print(str(card.value()) + " " + card.suit(), end=ui.CVERT)
            print()
        else:
            print("", end=ui.LVERT)
            for x in range(7):
                card = self._order[x]
                print(str(card.value()) + " " + card.suit(), end=ui.CVERT)
            print()
            print("", end=ui.LVERT)
            for x in range(7, len(self._order)):
                card = self._order[x]
                print(str(card.value()) + " " + card.suit(), end=ui.CVERT)
            print()

