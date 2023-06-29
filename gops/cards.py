import random

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

    # untested
    def sort_cards(self, ace="Low"):
        self._order = sorted(self._order, key=lambda x: x.nval)

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

