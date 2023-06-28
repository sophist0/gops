import random

class Card():
    def __init__(self, suit, val):
        self._suit = suit
        self._val = val

    def num_value(self):
        if isinstance(self._val, int):
            return self._val
        elif self._val == "J":
            return 10
        elif self._val == "Q":
            return 11
        elif self._val == "K":
            return 12
        elif self._val == "A":
            return 1
        else:
            return None

    def value(self):
        return self._val

    def suit(self):
        return self._suit

    def display(self):
        print(str(self._val) + ":" + self._suit)

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
            print("", end="| ")
            for x in range(len(self._order)):
                card = self._order[x]
                print(str(card.value()) + " " + card.suit(), end=" | ")
            print()
        else:
            print("", end="| ")
            for x in range(7):
                card = self._order[x]
                print(str(card.value()) + " " + card.suit(), end=" | ")
            print()
            print("", end="| ")
            for x in range(7, len(self._order)):
                card = self._order[x]
                print(str(card.value()) + " " + card.suit(), end=" | ")
            print()

