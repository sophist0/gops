import torch
import random
import numpy as np
from typing import List, Tuple, Union

import gops.ui_elements as ui

from model_components.inference_components import translate_greedy, translate_random
from model_components.transformer_components import construct_vocab_transform, construct_text_transform, construct_token_transform

from gops.statements import state_to_statement

class Card():
    def __init__(self, suit: str, val: Union[str, int]):
        self.ace = "low"
        self._suit = suit
        self._val = val
        self.nval = self.get_num_value()

    # Move this to the card suit class
    def get_num_value(self) -> Union[int, None]:
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

    def value(self) -> Union[int, str]:
        return self._val

    def suit(self) -> str:
        return self._suit

    def display(self):
        print(ui.RVERT + str(self._val) + " " + self._suit + ui.LVERT)


class CardStack():
    def __init__(self, cards: List[Card]):
        self.card_suits = ["Hearts", "Spades", "Clubs", "Diamonds"]
        self.card_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K", "A"]
        self._order = cards

    def add_cards(self, cards: List[Card]):
        self._order = cards

    def card_count(self) -> int:
        return len(self._order)

    def display_cards(self):
        for card in self._order:
            card.display()

    def shuffle(self):
        random.shuffle(self._order)

    def sort_cards(self):
        self._order = sorted(self._order, key=lambda x: x.nval)

    def get_card_nvals(self) -> List[int]:
        nvals = []
        for card in self._order:
            nvals.append(card.nval)
        return nvals

    def empty(self) -> bool:
        if self.card_count() == 0:
            return True
        else:
            return False

    def card_in_stack(self, suit: str, val: int) -> Tuple[bool, int]:
        if suit not in self.card_suits:
            raise Exception("Bad card suit.")
        if val not in self.card_values:
            raise Exception("Bad card value.")

        in_stack = False
        card_loc = -1
        for card in self._order:
            card_loc += 1
            if (card.suit() == suit) and (card.value() == val):
                in_stack = True
                return in_stack, card_loc
        return in_stack, -1


class SuitCards(CardStack):
    def __init__(self, suit: str):
        self.suit = suit
        cards = []
        CardStack.__init__(self, cards)

        if self.suit not in self.card_suits:
            raise Exception("Bad card suit.")

        for value in self.card_values:
            card = Card(suit, value)
            cards.append(card)
        self.add_cards(cards)

        random.shuffle(self._order)

    def draw(self) -> Card:
        return self._order.pop(0)


class Hand(SuitCards):
    def __init__(self, suit: str):
        SuitCards.__init__(self, suit)
        self.sort_cards()
        self.transformer_model = None
        self._bad_selections = 0

    def select_random_card(self) -> Card:
        selected = random.choice(range(self.card_count()))
        return self._order.pop(selected)

    def max_value(self) -> int:
        m = -1
        for card in self._order:
            if card.nval > m:
                m = card.nval
        return m

    def get_dist(self) -> float:
        # construct distribution
        card_prob = np.asarray([0 for x in range(self.card_count())])
        prob = self.card_count()
        for x in range(self.card_count()):
            card_prob[x] = prob
            prob -= (prob / 2)
        return card_prob / sum(card_prob)

    def select_index(self) -> int:
        # select index based on distribution
        card_prob = self.get_dist()
        r = random.random()
        s = 0
        for x in range(self.card_count()):
            s += card_prob[x]
            if r <= s:
                return x

    def select_prize_card_strategy(self, prize_card) -> Card:
        # selects same card as last prize card
        card_values = self.get_card_nvals()
        idx = 0
        for val in card_values:
            if val == prize_card.nval:
                return self._order.pop(idx)
            idx += 1
        return None

    def select_card_strategy_1(self, prize_value) -> Card:
        # if prize_value < 7, select near min value vard.
        # else select card close to prize value.
        # TODO: Alg. assumes cards are sorted. Should check this!
        card_weight = self.get_card_nvals()
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

        index = self.select_index()
        card_loc = card_indexes[index]

        # if prize is high and playing a lower value card, play the lowest
        # value. unless the value select is the maximum card value in the hand.
        card_value = self._order[card_loc].nval
        if ((prize_value >= 7) and (card_value < prize_value) and (card_value != self.max_value())):
            card_loc = 0

        return self._order.pop(card_loc)
    
    def select_transformer_model(self, move_data) -> Card:
        # Need all the state info available here for the model to choose a card!
 
        if self.transformer_model is None:

            # load transformer model
            NUM_EPOCHS = 7
            model_version = 7
            modelpath = "models/epoch_" + str(NUM_EPOCHS) + "_v" + str(model_version)
            self.transfomer_model = torch.load(modelpath)

        game_state = state_to_statement(move_data)

        # Define special symbols and indices
        STATE_LANGUAGE = 'state'
        MOVE_LANGUAGE = 'move'
        UNK_IDX, PAD_IDX, BOS_IDX, EOS_IDX = 0, 1, 2, 3
        special_symbols = ['<unk>', '<pad>', '<bos>', '<eos>']

        DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        token_transform = construct_token_transform(STATE_LANGUAGE, MOVE_LANGUAGE)

        ##########################################################################################
        # Load training data to get the transforms.
        ##########################################################################################
        with open('models/train_data_' + str(NUM_EPOCHS) + '_v' + str(model_version) + '.npy', 'rb') as f:
            train_iter = np.load(f, allow_pickle=True)

        vocab_transform = construct_vocab_transform(train_iter, STATE_LANGUAGE, MOVE_LANGUAGE, UNK_IDX, special_symbols, token_transform)
        text_transform = construct_text_transform(token_transform, vocab_transform, STATE_LANGUAGE, MOVE_LANGUAGE, BOS_IDX, EOS_IDX)

        selected_card = translate_greedy(self.transfomer_model, game_state, text_transform, vocab_transform, MOVE_LANGUAGE, STATE_LANGUAGE, BOS_IDX, DEVICE, EOS_IDX)
        selected_val = int(selected_card.split("_")[2])

        for idx, card in enumerate(self._order):
            if card.get_num_value() == selected_val:
                return self._order.pop(idx)
            
        # print()
        # print("Error card not in hand!!!!")
        # print("selecting random card")
        self._bad_selections += 1
        return self.select_random_card()


    def select_card(self, suit: str, val: int) -> Union[int, None]:
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
