import torch
import random
import numpy as np
from typing import List, Tuple, Union

from tokenizers import Tokenizer
from tokenizers.models import WordLevel

import gops.ui_elements as ui

from gops.bid_prediction import StrategyCollection, get_player_bid_efficiency

from model_components.inference_components import translate_random
from model_components.transformer_components import construct_text_transform

from gops.statements import state_to_statement

from gops.bid_prediction import StrategyCollection, get_player_bid_efficiency


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

        # probabilistic strategy 2
        self.strat_collection = None
        self.current_turn = 0
        self.opp_hand = None

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

    def select_prize_card_strategy(self, prize_card: Card) -> Card:
        # selects same card as last prize card
        card_values = self.get_card_nvals()
        idx = 0
        for val in card_values:
            if val == prize_card.nval:
                return self._order.pop(idx)
            idx += 1
        return None

    def find_card(self, target_card: Card) -> Card:
        card_values = self.get_card_nvals()
        idx = 0
        for val in card_values:
            if val == target_card.nval:
                return self._order.pop(idx)
            idx += 1
        return None

    def select_card_strategy_1(self, prize_value: int) -> Card:
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

    def select_card_strategy_2(self, prize_value: int) -> Card:
        # Probabilistic strategy 2

        # Attempts to predict the opponent bid and then using that knowledge
        # play the player bid with the highest bid efficiency
        self.current_turn += 1
        if self.strat_collection is None:
            self.strat_collection = StrategyCollection()
            self.opp_hand = np.asarray([x+1 for x in range(13)])

        pred_strat = self.strat_collection.predicted_strategy(self.current_turn, prize_value)

        pred_opp_bid = prize_value + pred_strat.bid_diff
        pred_diff = np.absolute(self.opp_hand - pred_opp_bid)
        min_idx = np.argmin(pred_diff)

        constrained_pred_opp_bid = self.opp_hand[min_idx]
        possible_player_bids = self.get_card_nvals()
        bid_efficiency, max_idx, max_val = get_player_bid_efficiency(prize_value, constrained_pred_opp_bid, possible_player_bids)

        card_val = possible_player_bids[max_idx-1]
        card_obj = Card("Hearts", int(card_val))
        return self.find_card(card_obj)

    def select_transformer_model(self, move_data, app_path, topk, DEVICE, tokenizer_lib) -> Card:
        # Need all the state info available here for the model to choose a card!

        modelpath = app_path["model_path"]

        game_state = state_to_statement(move_data)

        STATE_LANGUAGE = 'state'
        MOVE_LANGUAGE = 'move'
        BOS_IDX, EOS_IDX = 1, 2

        if self.transformer_model is None:
            self.transformer_model = torch.load(modelpath, map_location=DEVICE)

            # load tokenizer
            if tokenizer_lib == "HF":

                self.state_tokenizer = Tokenizer.from_file(app_path["state_tokenizer_path"])
                self.move_tokenizer = Tokenizer.from_file(app_path["move_tokenizer_path"])

                self.text_transform = construct_text_transform(self.state_tokenizer, self.move_tokenizer, STATE_LANGUAGE, MOVE_LANGUAGE)
                selected_card = translate_random(self.transformer_model, game_state, self.text_transform, MOVE_LANGUAGE, STATE_LANGUAGE, BOS_IDX, DEVICE, EOS_IDX, topk)

            elif tokenizer_lib == "TT":
                raise Exception("Bad tokenizer library TT")


        if tokenizer_lib == "HF":
            selected_card = translate_random(self.transformer_model, game_state, self.text_transform, MOVE_LANGUAGE, STATE_LANGUAGE, BOS_IDX, DEVICE, EOS_IDX, topk)
        elif tokenizer_lib == "TT":
            raise Exception("Bad tokenizer library TT")

        selected_val = int(selected_card.split("_")[2])
        for idx, card in enumerate(self._order):
            if card.get_num_value() == selected_val:
                return self._order.pop(idx)

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


def card_value_to_nval(vec: list) -> list:
    convert_map = {"0": 0, "A": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
                   "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13}
    nvec = []
    for val in vec:
        nvec.append(convert_map[val])
    return nvec


def hand_to_played(hand: Hand) -> list:
    deck = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    played = []
    for val in deck:
        if val not in hand:
            played.append(val)
    return played


def state_to_statement(game_move: dict) -> str:
    tmp_state = ""
    phw = game_move["pre_play_data"]["own_hand"]
    phw = card_value_to_nval(phw)
    phw.sort()
    phw = list(map(str, phw))
    player_hand_word = "player_hand_" + "_".join(phw)
    tmp_state += player_hand_word + " "

    os = game_move["pre_play_data"]["own_score"]
    player_score_word = "player_score_" + str(os)
    tmp_state += player_score_word + " "

    opp_h = game_move["pre_play_data"]["opponent_hand"]
    opp_p = hand_to_played(opp_h)
    opp_p = card_value_to_nval(opp_p)
    opp_p.sort()
    opp_p = list(map(str, opp_p))
    opp_cards_played = "opp_cards_played_" + "_".join(opp_p)
    tmp_state += opp_cards_played + " "

    opps = game_move["pre_play_data"]["opponent_score"]
    opp_score_word = "opponent_score_" + str(opps)
    tmp_state += opp_score_word + " "

    pvals = game_move["pre_play_data"]["prize_values"]
    pvals = card_value_to_nval(pvals)
    pval = str(sum(pvals))
    score_card_word = "current_score_card_" + pval
    tmp_state += score_card_word + " "

    ppv = game_move["pre_play_data"]["previous_prize_values"]
    ppv = card_value_to_nval(ppv)
    ppv.sort()
    ppv = list(map(str, ppv))
    prev_score_cards = "prev_score_cards_" + "_".join(ppv)
    tmp_state += prev_score_cards

    return tmp_state
