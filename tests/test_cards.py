import copy

from gops.cards import Card, CardStack, SuitCards, Hand

def get_values(cards):
    values = []
    for card in cards:
        values.append(card.value)
    return values

def test_Card():
    card_1 = Card("Clubs", "A")

    assert card_1.value() == "A"
    assert card_1.suit() == "Clubs"
    assert card_1.nval == 1

    card_1.ace = "high"
    assert card_1.get_num_value() == 14

    card_1._val = None
    assert card_1.get_num_value() == None

    card_1.display()

def test_CardStack():
    cards = [Card("Clubs", "A"), Card("Clubs", 2), Card("Clubs", 3), Card("Clubs", 4), Card("Clubs", 5)]
    values = get_values(cards)
    stack_1 = CardStack(cards)
    stack_2 = CardStack([])

    assert stack_1.card_count() == 5
    assert not stack_1.empty()

    assert stack_2.card_count() == 0
    assert stack_2.empty()

    # test card in stack
    in_stack, card_loc = stack_1.card_in_stack("Spade", "A")
    assert in_stack == False
    assert card_loc == -1

    in_stack, card_loc = stack_1.card_in_stack("Clubs", 4)
    assert in_stack == True
    assert card_loc == 3

    # test shuffle
    same = True
    attempts = 5
    for x in range(attempts):
        stack_1.shuffle()
        shuffled_values =  get_values(stack_1._order)

        for y in range(stack_1.card_count()):
            if values[y] != shuffled_values[y]:
                same = False
                break    
    assert not same

    stack_1.display_cards()

def test_SuitCards():

    suit = SuitCards("Clubs")
    assert suit.card_count() == 13

    card = suit.draw()
    assert suit.card_count() == 12

def test_Hand():

    hand = Hand("Clubs")

    # test select card
    card = hand.select_card("Spade", 2)
    assert card == None

    card = hand.select_card("Clubs", 2)
    in_stack, card_loc = hand.card_in_stack("Clubs", 2)
    assert card.value() == 2
    assert card.suit() == "Clubs"
    assert in_stack == False
    assert card_loc == -1

    # test select random card
    random_card = False
    hand_copy = copy.deepcopy(hand)
    while hand.empty() == False:
        card_1 = hand.select_random_card()
        card_2 = hand_copy.select_random_card()
     
        if (card_1.value() != card_2.value()) or (card_1.suit() != card_2.suit()):
            random_card = True
            break
    assert random_card == True

    hand.display_cards()
    for x in range(5):
        card = hand.draw()
    hand.display_cards()  
