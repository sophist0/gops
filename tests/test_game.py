import io

from gops.game import Player, AIPlayer, HumanPlayer, PlayArea, GameBase
from gops.cards import Card, SuitCards, Hand

def test_Player():
   hand = Hand("Hearts")
   player = Player(hand)

   assert player.quit_value() == False
   assert player.score() == 0

   player.accept_points(1)
   player.accept_points(1)
   assert player.score() == 2

   player.quit()
   assert player.quit_value() == True

def test_AIPlayer():
   hand = Hand("Hearts")
   player = AIPlayer(hand)
   card = player.play_random_card()

   assert isinstance(card, Card)
   assert card.suit() == "Hearts"

def test_HumanPlayer(monkeypatch):

    monkeypatch.setattr("sys.stdin", io.StringIO("2"))
    hand = Hand("Hearts")
    player = HumanPlayer(hand)
    card = player.play_card()
    
    assert isinstance(card, Card)
    assert card.value() == 2
    assert card.suit() == "Hearts"

def test_PlayArea():

    # round 0
    play_area_1 = PlayArea()
    assert play_area_1.player_1_card == None
    assert play_area_1.player_2_card == None
    assert play_area_1.prize_cards == []
    assert play_area_1.round == 0

    # round 1
    player_1_hand = Hand("Hearts")
    player_1 = AIPlayer(player_1_hand)
    card_1 = player_1.play_random_card()

    player_2_hand = Hand("Spades")
    player_2 = AIPlayer(player_2_hand)
    card_2 = player_2.play_random_card()

    prize_deck = SuitCards("Clubs")
    prize_card_1 = prize_deck.draw()

    # play_area_1.start_round(card_1, card_2, prize_card_1)
    play_area_1.flip_prize(prize_card_1)
    play_area_1.flip_cards(card_1, card_2)

    assert isinstance(play_area_1.player_1_card, Card)
    assert play_area_1.player_1_card.suit() == "Hearts"

    assert isinstance(play_area_1.player_2_card, Card)
    assert play_area_1.player_2_card.suit() == "Spades"

    assert isinstance(play_area_1.prize_cards[0], Card)
    assert play_area_1.prize_cards[0].suit() == "Clubs"

    assert play_area_1.round == 1

    # round 2
    card_1 = player_1.play_random_card()
    card_2 = player_2.play_random_card()

    prize_card_2 = prize_deck.draw()

    # play_area_1.start_round(card_1, card_2, prize_card_2)
    play_area_1.flip_prize(prize_card_2)
    play_area_1.flip_cards(card_1, card_2)


    assert (prize_card_1.nval + prize_card_2.nval) == play_area_1.prize_value()

    # test award_points
    play_area_2 = PlayArea()

    player_1_hand = Hand("Hearts")
    player_1 = AIPlayer(player_1_hand)
    card_1 = player_1.play_random_card()

    player_2_hand = Hand("Spades")
    player_2 = AIPlayer(player_2_hand)
    card_2 = player_2.play_random_card()

    prize_deck = SuitCards("Clubs")
    prize_card_1 = prize_deck.draw()

    # play_area_2.start_round(card_1, card_2, prize_card_1)
    play_area_2.flip_prize(prize_card_1)
    play_area_2.flip_cards(card_1, card_2)

    play_area_2.award_points(player_1, player_2)
   
    # would be better to trigger individual cases
    if card_1.nval > card_2.nval:
        assert player_1.score() == prize_card_1.nval
        assert player_2.score() == 0
    elif card_2.nval > card_1.nval:
        assert player_2.score() == prize_card_1.nval
        assert player_1.score() == 0
    else:
        assert player_1.score() == 0
        assert player_2.score() == 0

def test_Game():

    player_1 = AIPlayer("Hearts")
    player_2 = AIPlayer("Spades")
    game_1 = GameBase(player_1, player_2)
    assert isinstance(game_1.prize_deck, SuitCards)
    assert isinstance(game_1.player_1, Player)
    assert isinstance(game_1.player_2, Player)
    assert isinstance(game_1.play_area, PlayArea)

    assert game_1.game_over() == False
    for x in range(13):
        game_1.prize_deck.draw()
    assert game_1.game_over() == True

    game_2 = GameBase(player_1, player_2)
    assert game_2.game_over() == False
    game_2.player_1.quit()
    assert game_2.game_over() == True

    player_3 = AIPlayer("Hearts")
    player_4 = AIPlayer("Spades") 
    game_3 = GameBase(player_3, player_4)
    assert game_3.game_over() == False
    game_3.player_2.quit()
    assert game_3.game_over() == True

# Need to test AIAIGame

# Need to test AIHumanGame