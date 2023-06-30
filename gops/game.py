import random
import os
import time

import gops.ui_elements as ui
from gops.cards import SuitCards, Hand

class Player():
    def __init__(self, hand):
        self._hand = hand
        self._score = 0
        self._quit = False

    def accept_points(self, points):
        self._score += points

    def score(self):
        return self._score

    def quit(self):
        self._quit = True

    def quit_value(self):
        return self._quit

class AIPlayer(Player):
    def __init__(self, hand):
        Player.__init__(self, hand)

    def play_random_card(self):
        return self._hand.select_random_card()

class HumanPlayer(Player):
    def __init__(self, hand):
        Player.__init__(self, hand)

        # move somewhere more general
        self.str_2_val = {"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,
                        "J":"J","j":"J","Q":"Q","q":"Q","K":"K","k":"K","A":"A","a":"A"}

    def show_hand(self):
        self._hand.display_cards()

    def play_card(self):
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

    def print_round(self):
        print()
        print(ui.DIVIDER)
        print("Round: ", self.round) 
        print(ui.DIVIDER)

    def flip_prize(self, prize):
        self.prize_cards.append(prize)

    def flip_cards(self, card_1, card_2):
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

    def prize_winner(self, winner):
        if winner == None:
            print("Tie no prizes awarded.")
        else:
            print(winner + " won: " + self.get_prize_string())

    def display_pizes(self):
        print()
        print("Prizes: " + self.get_prize_string())

    def display_cards(self):
        print()
        print("Cards Played:")
        print(ui.TAB1 + "player 1: {} {} {} {}".format(ui.VERT, self.player_1_card.value(), self.player_1_card.suit(), ui.VERT))
        print(ui.TAB1 + "player 2: {} {} {} {}".format(ui.VERT, self.player_2_card.value(), self.player_2_card.suit(), ui.VERT))
        print()

    def prize_value(self):
        total = 0
        for card in self.prize_cards:    
            total += card.nval
        return total

    # move to Game class?
    def award_points(self, player_1, player_2):
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
    def __init__(self, player_1, player_2):
        self.prize_deck = None
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
        if self.winner == None:
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

# Untested, FIX
class AIAIGame(GameBase):
    def __init__(self):
        player_1 = AIPlayer(Hand("Hearts"))
        player_2 = AIPlayer(Hand("Spades"))
        GameBase.__init__(self, player_1, player_2)

    def run_game(self, reset=True):
        while not self.game_over():
            prize = self.prize_deck.draw()

            self.play_area.print_round()
            self.play_area.flip_prize(prize)
            self.play_area.display_pizes()

            player_1_card = self.player_1.play_random_card()
            player_2_card = self.player_2.play_random_card()

            self.play_area.flip_cards(player_1_card, player_2_card)
            self.play_area.display_cards()

            self.play_area.award_points(self.player_1, self.player_2)
            self.display_score()

            # wait
            print()
            input("Continue.....")
            if reset:
                os.system("reset")

        self.decide_winner()
        self.final_msg()

# Untested
class AIHumanGame(GameBase):
    def __init__(self):
        player_1 = AIPlayer(Hand("Hearts"))
        player_2 = HumanPlayer(Hand("Spades"))
        GameBase.__init__(self, player_1, player_2)

    def run_game(self, reset=True):
        while not self.game_over():
            self.play_area.print_round()
            self.player_2.show_hand()

            prize = self.prize_deck.draw()
            self.play_area.flip_prize(prize)
            self.play_area.display_pizes()

            player_1_card = self.player_1.play_random_card()
            player_2_card = self.player_2.play_card()

            self.play_area.flip_cards(player_1_card, player_2_card)
            self.play_area.display_cards()

            self.play_area.award_points(self.player_1, self.player_2)
            self.display_score()

            # wait
            print()
            input("Continue.....")
            if reset:
                os.system("reset")

        self.decide_winner()
        self.final_msg()
