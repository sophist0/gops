import random
import os
import ui_elements as ui

from cards import SuitCards, Hand

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

    def show_hand(self):
        self._hand.display_cards()

    def play_card(self):
        card = None
        while card is None:
            value = input("Select card value: ")
            print()

            # fix types
            if value not in ["J", "Q", "K", "A", "j" ,"q" ,"k", "a"]:
                value = int(value)
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

    def start_round(self, card_1, card_2, prize):
        self.player_1_card = card_1
        self.player_2_card = card_2
        self.prize_cards.append(prize)
        self.round += 1

    def display_prize(self):
        print("Prizes: ")
        for prize in self.prize_cards:
            prize.display()

    def display_cards(self):
        print()
        print("Cards Played:")
        print(ui.TAB1 + "player 1: {}:{}".format(self.player_1_card.value(), self.player_1_card.suit()))
        print(ui.TAB1 + "player 2: {}:{}".format(self.player_2_card.value(), self.player_2_card.suit()))
        print()
        self.display_prize()

    def prize_value(self):
        total = 0
        for card in self.prize_cards:    
            total += card.num_value()
        return total

    # move to Game class?
    def award_points(self, player_1, player_2):
        if self.player_1_card.num_value() > self.player_2_card.num_value():
            player_1.accept_points(self.prize_value())
            self.clear()
        elif self.player_2_card.num_value() > self.player_1_card.num_value():
            player_2.accept_points(self.prize_value())
            self.clear()
        else:
            # deal with tie
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
        print("Scores:")
        print(ui.TAB1 + "Player_1 score: {}".format(self.player_1.score()))
        print(ui.TAB1 + "Player_2 score: {}".format(self.player_2.score()))

# Untested
class AIAIGame(GameBase):
    def __init__(self):
        player_1 = AIPlayer(Hand("Hearts"))
        player_2 = AIPlayer(Hand("Spades"))
        GameBase.__init__(self, player_1, player_2)

    def run_game(self):
        while not self.game_over():
            prize = self.prize_deck.draw()
            player_1_card = self.player_1.play_random_card()
            player_2_card = self.player_2.play_random_card()

            self.play_area.start_round(player_1_card, player_2_card, prize)
            self.play_area.display_cards()

            self.play_area.award_points(self.player_1, self.player_2)
            self.display_score()

            # wait
            print()
            input("Continue.....")
            os.system("reset")

        self.decide_winner()
        self.final_msg()

# Untested
class AIHumanGame(GameBase):
    def __init__(self):
        player_1 = AIPlayer(Hand("Hearts"))
        player_2 = HumanPlayer(Hand("Spades"))
        GameBase.__init__(self, player_1, player_2)

    def run_game(self):
        while not self.game_over():
            prize = self.prize_deck.draw()
            player_1_card = self.player_1.play_random_card()

            self.play_area.print_round()
            self.player_2.show_hand()
            print()
            print("prize (FIX does not display all pizes in play area): ")
            prize.display()
            print()
            player_2_card = self.player_2.play_card()
            os.system("reset")

            self.play_area.print_round()
            self.play_area.start_round(player_1_card, player_2_card, prize)
            self.play_area.display_cards()

            self.play_area.award_points(self.player_1, self.player_2)
            self.display_score()

            # wait
            print()
            input("Continue.....")
            os.system("reset")

        self.decide_winner()
        self.final_msg()
