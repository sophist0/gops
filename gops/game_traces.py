import copy, pickle

from gops.cards import Hand


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

    def save_game_trace(self, filepath):
        save_file = filepath + ".pkl"

        with open(save_file, "wb") as file:
            pickle.dump(self, file)
            file.close()

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
