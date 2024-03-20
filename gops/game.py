import os, copy
from typing import Union

import gops.ui_elements as ui
from gops.cards import SuitCards, Hand, Card


class Player():
    def __init__(self, hand: Hand):
        self._hand = hand
        self._score = 0
        self._quit = False

    def accept_points(self, points: int):
        self._score += points

    def score(self) -> int:
        return self._score

    def quit(self):
        self._quit = True

    def quit_value(self) -> bool:
        return self._quit


class AIPlayer(Player):
    def __init__(self, id, hand: Hand, difficulty: int = 1):
        Player.__init__(self, hand)
        self._difficulty = difficulty
        self.id = id

    def play_card(self, prize_value: int) -> Card:
        if self._difficulty == 1:
            return self._hand.select_random_card()
        elif self._difficulty == 2:
            return self._hand.select_card_strategy_1(prize_value)

    def set_difficulty(self, difficulty: int):
        if difficulty not in [1, 2]:
            raise Exception("Bad difficulty.")
        self._difficulty = difficulty


class HumanPlayer(Player):
    def __init__(self, hand: Hand):
        Player.__init__(self, hand)

        # move somewhere more general
        self.str_2_val = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
                          "J": "J", "j": "J", "Q": "Q", "q": "Q", "K": "K", "k": "K", "A": "A", "a": "A"}

    def show_hand(self):
        self._hand.display_cards()

    def play_card(self) -> Card:
        card = None
        while card is None:
            print()
            value = input("Select card value: ")
            print()
            print(ui.DIVIDER)

            if value in self.str_2_val:
                value = self.str_2_val[value]
                card = self._hand.select_card(self._hand.suit, value)
        return card


class PlayArea():
    def __init__(self):
        self.clear()
        self.round = 0
        self.prize_cards = []

    def print_round(self):
        print()
        print(ui.DIVIDER)
        print("Round: ", self.round)
        print(ui.DIVIDER)

    def flip_prize(self, prize: int):
        self.prize_cards.append(prize)

    def flip_cards(self, card_1: Card, card_2: Card):
        self.player_1_card = card_1
        self.player_2_card = card_2
        self.round += 1

    def get_prize_string(self):
        prize_string = ""
        for cnt, prize in enumerate(self.prize_cards):
            if cnt > 0:
                prize_string = prize_string.rstrip(ui.VERT)
            prize_string += "{} {} {} {}".format(ui.VERT, prize.value(), prize.suit(), ui.VERT)
        return prize_string

    def prize_winner(self, winner: Union[str, None]):
        if winner is None:
            print("Tie no prizes awarded.")
        else:
            print(winner + " won: " + self.get_prize_string())

    def display_pizes(self):
        print()
        print("Prizes: " + self.get_prize_string())

    def display_cards(self):
        print()
        print("Cards Played:")
        print(ui.TAB1 + "player 1: {} {} {} {}".format(ui.VERT, self.player_1_card.value(),
                                                       self.player_1_card.suit(), ui.VERT))
        print(ui.TAB1 + "player 2: {} {} {} {}".format(ui.VERT, self.player_2_card.value(),
                                                       self.player_2_card.suit(), ui.VERT))
        print()

    def prize_value(self):
        total = 0
        for card in self.prize_cards:
            total += card.nval
        return total

    # move to Game class?
    def award_points(self, player_1: Player, player_2: Player):
        if self.player_1_card.nval > self.player_2_card.nval:
            player_1.accept_points(self.prize_value())
            self.prize_winner("Player 1")
            self.clear()
        elif self.player_2_card.nval > self.player_1_card.nval:
            player_2.accept_points(self.prize_value())
            self.prize_winner("Player 2")
            self.clear()
        else:
            # deal with tie
            self.prize_winner(None)
            self.clear_player_cards()

    def clear_player_cards(self):
        self.player_1_card = None
        self.player_2_card = None

    def clear(self):
        self.clear_player_cards()
        self.prize_cards = []


class GameBase():
    def __init__(self, player_1: Player, player_2: Player, reset: bool = True):
        self.prize_deck = None
        self.reset = reset
        self.player_1 = player_1
        self.player_2 = player_2

        self.prize_deck = SuitCards("Clubs")
        self.prize_deck.shuffle()
        self.play_area = PlayArea()
        self.winner = None

    def game_over(self):
        if self.prize_deck.empty():
            return True
        elif self.player_1.quit_value():
            return True
        elif self.player_2.quit_value():
            return True
        else:
            return False

    def decide_winner(self):
        if self.player_1.score() > self.player_2.score():
            self.winner = 1
        elif self.player_2.score() > self.player_1.score():
            self.winner = 2
        elif self.player_1.score() == self.player_2.score():
            self.winner = 0

    def final_msg(self):
        if self.winner is None:
            print("Winner is not decided.")
        elif self.winner == 1:
            print("Player 1 is the winner.")
        elif self.winner == 2:
            print("Player 2 is the winner.")
        elif self.winner == 0:
            print("Player 1 and Player 2 tied.")

    def display_score(self):
        print()
        print(ui.DIVIDER)
        print()
        print("Scores:")
        print(ui.TAB1 + "Player_1 score: {}".format(self.player_1.score()))
        print(ui.TAB1 + "Player_2 score: {}".format(self.player_2.score()))

    def wait_and_reset(self):
        print()
        input("Continue.....")
        print()
        # if self.reset:
        #     os.system("clear")

# Added
####################################################################################

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

class TurnData():
    def __init__(self, player_1_data, player_2_data, prize_cards):
        self.player_1_data = player_1_data
        self.player_2_data = player_2_data
        self.prize_cards = copy.deepcopy(prize_cards)
        self.previous_prize_cards = []

    def add_prize_cards(self, previous_prizes):
        for prize in previous_prizes:
            self.previous_prize_cards.append(prize)


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

####################################################################################

class AIAIGame(GameBase):
    def __init__(self, reset: bool = True):
        player_1 = AIPlayer(1, Hand("Hearts"))
        player_2 = AIPlayer(2, Hand("Spades"))
        GameBase.__init__(self, player_1, player_2, reset)
        self.game_trace = GameTrace()

    def run_game(self):
        while not self.game_over():
            prize = self.prize_deck.draw()

            self.play_area.print_round()
            self.play_area.flip_prize(prize)
            self.play_area.display_pizes()

            # Added
            ##################
            self.game_trace.update_trace(self.player_1, self.player_2, self.play_area.prize_cards)
            ##################

            player_1_card = self.player_1.play_card(self.play_area.prize_value())
            player_2_card = self.player_2.play_card(self.play_area.prize_value())

            # Added
            ##################
            self.game_trace.add_played_cards(player_1_card, player_2_card)
            ##################

            self.play_area.flip_cards(player_1_card, player_2_card)
            self.play_area.display_cards()

            self.play_area.award_points(self.player_1, self.player_2)
            self.display_score()

            self.wait_and_reset()

        self.decide_winner()
        self.final_msg()

        # Added
        ##################
        self.game_trace.update_winner(self.winner)
        self.game_trace.write_game_trace()
        ##################



class AIHumanGame(GameBase):
    def __init__(self, reset=True):
        player_1 = AIPlayer(Hand("Hearts"))
        player_2 = HumanPlayer(Hand("Spades"))
        GameBase.__init__(self, player_1, player_2, reset)

    def run_game(self):
        print()
        difficulty = None
        while difficulty is None:
            selected = input("Select AI difficulty [1, 2]: ")
            if selected not in ["1", "2"]:
                print("Invalid selection.")
                print()
            else:
                difficulty = int(selected)
        print()
        self.player_1.set_difficulty(difficulty)

        while not self.game_over():
            self.play_area.print_round()
            self.player_2.show_hand()

            prize = self.prize_deck.draw()
            self.play_area.flip_prize(prize)
            self.play_area.display_pizes()

            player_1_card = self.player_1.play_card(self.play_area.prize_value())
            player_2_card = self.player_2.play_card()

            self.play_area.flip_cards(player_1_card, player_2_card)
            self.play_area.display_cards()

            self.play_area.award_points(self.player_1, self.player_2)
            self.display_score()

            self.wait_and_reset()

        self.decide_winner()
        self.final_msg()
