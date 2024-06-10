import io

from gops.game import Player, AIPlayer, HumanPlayer, PlayArea, GameBase, AIHumanGame
from gops.cards import Card, SuitCards, Hand


def test_Player():
    hand = Hand("Hearts")
    player = Player(hand)

    assert player.quit_value() is False
    assert player.score() == 0

    player.accept_points(1)
    player.accept_points(1)
    assert player.score() == 2

    player.quit()
    assert player.quit_value() is True


def test_AIPlayer():
    hand = Hand("Hearts")
    player = AIPlayer(1, hand)
    card = player.play_card(1, hand._order[0], None)            # TODO: pass in game state

    assert isinstance(card, Card)
    assert card.suit() == "Hearts"


def test_HumanPlayer(monkeypatch):

    hand = Hand("Hearts")
    player = HumanPlayer(2, hand)

    monkeypatch.setattr("sys.stdin", io.StringIO("2"))
    card = player.play_card()
    assert isinstance(card, Card)
    assert card.value() == 2
    assert card.suit() == "Hearts"

    monkeypatch.setattr("sys.stdin", io.StringIO("k"))
    card = player.play_card()
    assert card.value() == "K"

    player.show_hand()


def setup_AIAI_game():

    play_area_1 = PlayArea()
    prize_deck = SuitCards("Clubs")
    player_1 = AIPlayer(1, Hand("Hearts"))
    player_2 = AIPlayer(2, Hand("Spades"))

    return [play_area_1, prize_deck, player_1, player_2]


def run_round(play_area, prize_deck, player_1, player_2):

    prize_card = prize_deck.draw()
    card_1 = player_1.play_card(prize_card.value, prize_card, None)         # TODO: pass in game state
    card_2 = player_2.play_card(prize_card.value, prize_card, None)         # TODO: pass in game state

    play_area.flip_prize(prize_card)
    play_area.flip_cards(card_1, card_2)

    return play_area, prize_card, card_1, card_2, prize_card


def test_PlayArea():

    # round 0, null case
    play_area_1 = PlayArea()
    assert play_area_1.player_1_card is None
    assert play_area_1.player_2_card is None
    assert play_area_1.prize_cards == []
    assert play_area_1.round == 0

    # round 1, normal case
    play_area_1, prize_deck, player_1, player_2 = setup_AIAI_game()
    play_area_1, prize_card_1, _, _, _ = run_round(play_area_1, prize_deck, player_1, player_2)

    assert isinstance(play_area_1.player_1_card, Card)
    assert play_area_1.player_1_card.suit() == "Hearts"

    assert isinstance(play_area_1.player_2_card, Card)
    assert play_area_1.player_2_card.suit() == "Spades"

    assert isinstance(play_area_1.prize_cards[0], Card)
    assert play_area_1.prize_cards[0].suit() == "Clubs"

    assert play_area_1.round == 1

    # round 2, prize values added case
    play_area_1, prize_card_2, _, _, _ = run_round(play_area_1, prize_deck, player_1, player_2)
    assert (prize_card_1.nval + prize_card_2.nval) == play_area_1.prize_value()

    # test award_points
    play_area_2, prize_deck, player_1, player_2 = setup_AIAI_game()
    play_area_2, _, card_1, card_2, prize_card_2 = run_round(play_area_2, prize_deck, player_1, player_2)

    play_area_2.display_pizes()
    play_area_2.display_cards()

    play_area_2.award_points(player_1, player_2)
    play_area_2.print_round()

    # would be better to trigger individual cases
    if card_1.nval > card_2.nval:
        assert player_1.score() == prize_card_2.nval
        assert player_2.score() == 0
    elif card_2.nval > card_1.nval:
        assert player_2.score() == prize_card_2.nval
        assert player_1.score() == 0
    else:
        assert player_1.score() == 0
        assert player_2.score() == 0

    # prize string case
    play_area_3 = PlayArea()
    card_3 = Card("Spades", "A")
    card_4 = Card("Spades", "9")
    play_area_3.flip_prize(card_3)
    play_area_3.flip_prize(card_4)
    prize_string = play_area_3.get_prize_string()
    assert prize_string == "| A Spades | 9 Spades |"


def test_GameBase():

    # case 1
    _, _, player_1, player_2 = setup_AIAI_game()
    game_1 = GameBase(player_1, player_2)
    assert isinstance(game_1.prize_deck, SuitCards)
    assert isinstance(game_1.player_1, Player)
    assert isinstance(game_1.player_2, Player)
    assert isinstance(game_1.play_area, PlayArea)

    assert game_1.game_over() is False
    for x in range(13):
        game_1.prize_deck.draw()
    assert game_1.game_over() is True

    # case 2
    game_2 = GameBase(player_1, player_2)
    assert game_2.game_over() is False
    game_2.player_1.quit()
    assert game_2.game_over() is True

    # case 3
    _, _, player_3, player_4 = setup_AIAI_game()
    game_3 = GameBase(player_3, player_4)
    assert game_3.game_over() is False
    game_3.player_2.quit()
    assert game_3.game_over() is True

    game_1.display_score()

def test_AIHumanGame(mocker):
    human_game = AIHumanGame(reset=False)
    v = io.StringIO("\r")
    s = ["1", "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    print(type(s[0]))
    inputs = []
    for x in range(len(s)):
        inputs.append(v)
        inputs.append(s[x])
    inputs.append(v)

    print()
    print("inputs")
    print(inputs)
    print(len(inputs))
    mocker.patch("builtins.input", side_effect=inputs)
    human_game.run_game()
