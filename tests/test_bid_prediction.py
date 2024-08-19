import math
from gops.bid_prediction import Strategy, StrategyCollection, get_player_bid_efficiency

def test_Strategy():
    turn = 0
    prize = 1
    bid_diff = 2
    strat = Strategy(turn, prize, bid_diff)
    strat_val = strat.get_strategy()

    assert strat_val[0] == turn
    assert strat_val[1] == prize
    assert strat_val[2] == bid_diff

def test_StrategyCollection_init():

    sc = StrategyCollection()

    assert sc.min_prize == 1
    assert sc.max_prize == 13
    assert len(sc.collection) == 13

    prizes = [x+1 for x in range(13)]
    for key in sc.collection.keys():
        strat = sc.collection[key]

        assert strat.turn == 0
        assert strat.bid_diff == 0
        assert strat.prize in prizes
        prizes.remove(strat.prize)

def test_StrategyCollection_add_strategy():

    sc = StrategyCollection()
    turn = 1
    prize = 2
    bid_diff = 3
    strat = Strategy(turn, prize, bid_diff)
    sc.add_strategy(strat)

    ADDED = False
    for key in sc.collection.keys():
        strat = sc.collection[key]

        if (strat.turn == turn) and (strat.prize == prize) and (strat.bid_diff == bid_diff):
            ADDED = True
            break
    assert ADDED is True

def test_StrategyCollection_get_strat_prob_1():
    sc = StrategyCollection()

    turn_1 = 1
    prize_1 = 1
    bid_diff_1 = 0
    strat_1 = Strategy(turn_1, prize_1, bid_diff_1)
    sc.add_strategy(strat_1)

    turn_2 = 1
    prize_2 = 2
    bid_diff_2 = 0
    strat_2 = Strategy(turn_2, prize_2, bid_diff_2)
    sc.add_strategy(strat_2)

    cturn_A = 2
    cprize_A = 2
    norm_const_A = sc._get_norm_constant(cturn_A, cprize_A)
    prob_s1_A = sc._get_strat_prob(cturn_A, cprize_A, strat_1, norm_const_A)
    prob_s2_A = sc._get_strat_prob(cturn_A, cprize_A, strat_2, norm_const_A)

    assert prob_s2_A > prob_s1_A

    turn_3 = 2
    prize_3 = 2
    bid_diff_3 = 0
    strat_3 = Strategy(turn_3, prize_3, bid_diff_3)
    sc.add_strategy(strat_3)

    cturn_B = 3
    cprize_B = 2
    norm_const_B = sc._get_norm_constant(cturn_B, cprize_B)
    prob_s2_B = sc._get_strat_prob(cturn_B, cprize_B, strat_2, norm_const_B)

    assert norm_const_A > norm_const_B
    assert prob_s2_A > prob_s2_B

def test_StrategyCollection_get_strat_prob_2():

    # check the probability of all strategies is not the same initially for varying prize value.
    # This is due to boundary conditions, however the probability is symmetric around prize=7.

    sc = StrategyCollection()

    probs = []
    for key in sc.collection.keys():
        strat = sc.collection[key]
        norm_const = sc._get_norm_constant(strat.turn, strat.prize)
        strat_prob = sc._get_strat_prob(strat.turn, strat.prize, strat, norm_const)
        probs.append(strat_prob)

    assert math.isclose(probs[0], probs[12])
    assert math.isclose(probs[5], probs[7])

def test_StrategyCollection_predicted_strategy():
    sc = StrategyCollection()

    turn_1 = 0
    prize_1 = 1
    bid_diff_1 = 0
    strat_1 = Strategy(turn_1, prize_1, bid_diff_1)

    turn_2 = 0
    prize_2 = 13
    bid_diff_2 = 0
    strat_2 = Strategy(turn_2, prize_2, bid_diff_2)

    turn_3 = 0
    prize_3 = 7
    bid_diff_3 = 0
    strat_3 = Strategy(turn_3, prize_3, bid_diff_3)

    trials = 1000

    cturn_A = 0
    cprize_A = 1
    cturn_B = 0
    cprize_B = 13

    cnt_match_1 = 0
    cnt_match_2 = 0
    cnt_match_3 = 0
    for x in range(trials):
        strat_A = sc.predicted_strategy(cturn_A, cprize_A)
        strat_B = sc.predicted_strategy(cturn_B, cprize_B)

        if (strat_1.prize == strat_A.prize) and (strat_1.turn == strat_A.turn) and (strat_1.bid_diff == strat_A.bid_diff):
            cnt_match_1 += 1

        if (strat_2.prize == strat_B.prize) and (strat_2.turn == strat_B.turn) and (strat_2.bid_diff == strat_B.bid_diff):
            cnt_match_2 += 1

        # strat_B should rarely be strat_3 given the different prize values
        if (strat_3.prize == strat_B.prize) and (strat_3.turn == strat_B.turn) and (strat_3.bid_diff == strat_B.bid_diff):
            cnt_match_3 += 1

    assert abs(cnt_match_1 - cnt_match_2) < 0.1 * trials

    # prize value effects selection probability
    assert cnt_match_1 > cnt_match_3
    assert cnt_match_2 > cnt_match_3


    # Add a new strategy on turn 1, then check that it is chosen more often on turn 2 than the init strategy for turn 0
    nturn = 1
    nprize = 7
    nbid_diff = 3
    nstrat = Strategy(nturn, nprize, nbid_diff)
    sc.add_strategy(nstrat)

    iturn = 0
    iprize = 7
    ibid_diff = 0
    istrat = Strategy(iturn, iprize, ibid_diff)

    cturn_C = 2
    cprize_C = 7
    cnt_match_n = 0
    cnt_match_i = 0
    for x in range(trials):
        strat_C = sc.predicted_strategy(cturn_C, cprize_C)

        if (nstrat.prize == strat_C.prize) and (nstrat.turn == strat_C.turn) and (nstrat.bid_diff == strat_C.bid_diff):
            cnt_match_n += 1

        if (istrat.prize == strat_C.prize) and (istrat.turn == strat_C.turn) and (istrat.bid_diff == strat_C.bid_diff):
            cnt_match_i += 1

    assert cnt_match_n > cnt_match_i

def test_get_player_bid_efficiency():

    player_bids = [x+1 for x in range(13)]

    opponent_bid = 7
    prize = 7
    bid_efficiency, max_idx, max_val = get_player_bid_efficiency(prize, opponent_bid, player_bids)
    assert max_val == 6.125
    assert max_idx == 8

    opponent_bid = 1
    prize = 7
    bid_efficiency, max_idx, max_val = get_player_bid_efficiency(prize, opponent_bid, player_bids)
    assert max_val == 12.25
    assert max_idx == 2

    opponent_bid = 13
    prize = 7
    bid_efficiency, max_idx, max_val = get_player_bid_efficiency(prize, opponent_bid, player_bids)
    assert max_val == 12
    assert max_idx == 1

    opponent_bid = 7
    prize = 10
    bid_efficiency, max_idx, max_val = get_player_bid_efficiency(prize, opponent_bid, player_bids)
    assert max_val == 8.75
    assert max_idx == 8

    opponent_bid = 7
    prize = 4
    bid_efficiency, max_idx, max_val = get_player_bid_efficiency(prize, opponent_bid, player_bids)
    assert max_val == 6
    assert max_idx == 1
