def card_value_to_nval(vec):
    convert_map = {"0": 0, "A": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
                   "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13}
    nvec = []
    for val in vec:
        nvec.append(convert_map[val])
    return nvec


def hand_to_played(hand):
    deck = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    played = []
    for val in deck:
        if val not in hand:
            played.append(val)
    return played


def state_to_statement(game_move):
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


def move_to_statement(game_move):
    sample = {"state": "", "move": ""}
    tmp_state = state_to_statement(game_move)

    pc = game_move["post_play_data"]["own_played_card"]
    pc = card_value_to_nval([pc])
    played_card = "played_card_" + str(pc[0])

    sample["state"] = tmp_state
    sample["move"] = played_card

    return sample
