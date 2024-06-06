import copy
import json
import re
from os import listdir
from os.path import isfile, join
import pandas as pd

from gops.cards import Hand
from gops.statements import move_to_statement


class PlayerTraceData():
    def __init__(self, id, hand, score):
        self.player_id = id
        self.player_hand = copy.deepcopy(hand)
        self.player_suit = hand.suit
        self.player_score = score
        self.prev_cards_played = self.add_prev_cards_played()
        self.card_played = None

    def add_prev_cards_played(self):
        prev_cards_played = []
        og_hand = Hand(self.player_suit)
        for card in og_hand._order:
            if self.player_hand.card_in_stack(card.suit(), card.value())[0] is False:
                prev_cards_played.append(card)
        return prev_cards_played
    
    def play_data_to_dict(self):
        player_data = {"pre_play_data": {}, "post_play_data": {}}

        player_data["pre_play_data"]["own_score"] = str(self.player_score)
        hand_values = []
        for card in self.player_hand._order:
            hand_values.append(str(card.value()))
        hand_values.sort()
        player_data["pre_play_data"]["own_hand"] = hand_values

        if self.card_played:
            player_data["post_play_data"]["own_played_card"] = str(self.card_played.value())

        return player_data

class TurnData():
    def __init__(self, player_1_data: PlayerTraceData, player_2_data: PlayerTraceData, prize_cards):
        self.player_1_data = player_1_data
        self.player_2_data = player_2_data
        self.prize_cards = copy.deepcopy(prize_cards)
        self.previous_prize_cards = []

    def add_prize_cards(self, previous_prizes):
        for prize in previous_prizes:
            self.previous_prize_cards.append(prize)

    def player_game_state_to_dict(self, player):
        # this assumes perfect memory of the game state

        player_dict = None
        opponent_dict = None
        if player == 1:
            player_dict = self.player_1_data.play_data_to_dict()
            opponent_dict = self.player_2_data.play_data_to_dict()
        elif player == 2:
            player_dict = self.player_2_data.play_data_to_dict()
            opponent_dict = self.player_1_data.play_data_to_dict()

        player_dict["pre_play_data"]["opponent_score"] = opponent_dict["pre_play_data"]["own_score"]
        player_dict["pre_play_data"]["opponent_hand"] = opponent_dict["pre_play_data"]["own_hand"]

        prize_values = []
        for card in self.prize_cards:
            prize_values.append(str(card.value()))
        prize_values.sort()
        player_dict["pre_play_data"]["prize_values"] = prize_values

        pre_prize_values = []
        for card in self.previous_prize_cards:
            pre_prize_values.append(str(card.value()))
        pre_prize_values.sort()
        player_dict["pre_play_data"]["previous_prize_values"] = pre_prize_values

        return player_dict


class GameTrace():
    def __init__(self):
        self.turn = 1
        self.game_trace = {}
        self.game_winner = None

    def update_trace(self, player_1, player_2, prize_cards):

        player_1_data = PlayerTraceData(player_1.id, player_1._hand, player_1._score)
        player_2_data = PlayerTraceData(player_2.id, player_2._hand, player_2._score)
        current_turn = TurnData(player_1_data, player_2_data, prize_cards)

        if self.turn > 1:
            previous_turn = self.game_trace[self.turn-1]
            current_turn.add_prize_cards(previous_turn.previous_prize_cards)

        # update previous prizes if last round scored
        if (self.turn > 1) and (len(prize_cards) == 1):
            current_turn.add_prize_cards(previous_turn.prize_cards)

        self.game_trace[self.turn] = current_turn

    # no protection for this turn update happening at the correct time
    def update_trace_turn(self):
        self.turn += 1

    def add_played_cards(self, player_1_card, player_2_card):
        self.game_trace[self.turn].player_1_data.card_played = player_1_card
        self.game_trace[self.turn].player_2_data.card_played = player_2_card
        self.update_trace_turn()

    def update_winner(self, winner):
        self.game_winner = winner

    def cards_to_values(self, cards):
        values = []
        if isinstance(cards, Hand):
            for card in cards._order:
                values.append(card.value())
        else:
            for card in cards:
                values.append(card.value())
        return values

    def save_game_trace(self, filepath):
        save_file = filepath + ".json"
        with open(save_file, "w") as outfile:
            json_trace = self.to_json()
            json.dump(json_trace, outfile)
            outfile.close()

    def to_json(self):
        trace = {"turns": {}, "winner": None}
        for turn in range(1, self.turn):
            turn_data = self.game_trace[turn]
            player_1_move = turn_data.player_game_state_to_dict(1)
            player_2_move = turn_data.player_game_state_to_dict(2)

            trace["turns"][turn] = {}
            trace["turns"][turn]["player_1_move"] = player_1_move
            trace["turns"][turn]["player_2_move"] = player_2_move
          
        trace["winner"] = self.game_winner
        return trace
    
    def write_game_trace(self):
        print()
        print("#############################################################")
        print()
        for turn in range(1, self.turn):
            turn_data = self.game_trace[turn]
            print("turn: ", turn)
            prev_prize_values = self.cards_to_values(turn_data.previous_prize_cards)
            print("previous prizes: ", prev_prize_values)
            current_prize_values = self.cards_to_values(turn_data.prize_cards)
            print("current_prize_cards", current_prize_values)

            print()
            print("player 1")
            print("player_id: ", turn_data.player_1_data.player_id)
            player_1_hand_values = self.cards_to_values(turn_data.player_1_data.player_hand)
            print("player_hand: ", player_1_hand_values)
            print("player_suit: ", turn_data.player_1_data.player_suit)
            print("player_score: ", turn_data.player_1_data.player_score)
            player_1_prev_cards_played = self.cards_to_values(turn_data.player_1_data.prev_cards_played)
            print("prev_cards_played: ", player_1_prev_cards_played)
            print("card_played: ", turn_data.player_1_data.card_played.value())

            print()
            print("player 2")
            print("player_id: ", turn_data.player_2_data.player_id)
            player_2_hand_values = self.cards_to_values(turn_data.player_2_data.player_hand)
            print("player_hand: ", player_2_hand_values)
            print("player_suit: ", turn_data.player_2_data.player_suit)
            print("player_score: ", turn_data.player_2_data.player_score)
            player_2_prev_cards_played = self.cards_to_values(turn_data.player_2_data.prev_cards_played)
            print("prev_cards_played: ", player_2_prev_cards_played)
            print("card_played: ", turn_data.player_2_data.card_played.value())

            print()
            print("#############################################################")

        print()
        print("game winner: ", self.game_winner)
        print("#############################################################")
        print()

# Class extracts winning moves (state, played_card) pairs from the traces.
# Here wins are defined as game wins not prize wins.
class ExtractTraceMoves():
    def __init__(self, tracepath=None, p1_difficulty=None, p2_difficulty=None):
        # Added the None default to use the move_to_statement() method

        self.tracespath = tracepath
        self.p1_difficulty = p1_difficulty
        self.p2_difficulty = p2_difficulty

        self.traces = None
        if (self.tracespath is not None) and (self.p1_difficulty is not None) and (self.p2_difficulty is not None): 
            self.traces = self.get_trace_names()

        self.good_moves = None
        self.all_moves = None

    def get_trace_names(self):
        trace_pattern = "p1_d" + str(self.p1_difficulty) + "_p2_d" + str(self.p2_difficulty) + "_trace_"
        trace_files = [f for f in listdir(self.tracespath) if (isfile(join(self.tracespath, f)) and re.search(trace_pattern, f))]
        return trace_files
    
    # Need to load from json now
    def load_trace(self, filepath):
        load_file = filepath
        with open(load_file, "rb") as file:
            loaded_game_trace = json.load(file)
            file.close()
        return loaded_game_trace
 
    def get_moves(self):
        good_moves = []
        all_moves = []
        for trace_name in self.traces:

            trace_data = self.load_trace(self.tracespath + "/" + trace_name)
            for turn in trace_data["turns"]:
                turn_data = trace_data["turns"][turn]
                player_1_move = turn_data["player_1_move"]
                player_2_move = turn_data["player_2_move"]
                all_moves.append(player_1_move)
                all_moves.append(player_2_move)
                if trace_data["winner"] == 1:
                    good_moves.append(player_1_move)
                elif trace_data["winner"] == 2:
                    good_moves.append(player_2_move)
                   
        self.good_moves = good_moves
        self.all_moves = all_moves
        return self.all_moves, self.good_moves

    def statements_dict_to_dataframe(self):
        samples = self.good_moves_and_states_to_statements()

        data = []
        for sample in samples:
            row = [sample["state"], sample["move"]]
            data.append(row)
        df = pd.DataFrame(data, columns=["State", "Move"])
        return df

    # TODO: test 
    def good_moves_and_states_to_statements(self):
        all_samples = []
        for trace_name in self.traces:
            trace_data = self.load_trace(self.tracespath + "/" + trace_name)
            for turn in trace_data["turns"]:
                turn_data = trace_data["turns"][turn]

                if trace_data["winner"] == 1:
                    good_move = turn_data["player_1_move"] 
                    sample = move_to_statement(good_move)
                    all_samples.append(sample)

                if trace_data["winner"] == 2:
                    good_move = turn_data["player_2_move"] 
                    sample = move_to_statement(good_move)
                    all_samples.append(sample)

        return all_samples
