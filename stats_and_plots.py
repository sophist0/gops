#!/usr/bin/env python3

import re
import pickle
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt

from gops.game_traces import ExtractTraceMoves

# load all game traces and look at the number of times player 1 won, player 2 won and their win percentages.

def load_game_trace(filepath):
    load_file = filepath
    with open(load_file, "rb") as file:
        loaded_game_trace = pickle.load(file)
        file.close()
        return loaded_game_trace

def get_win_stats(traces_path, trace_files):
    win_stats = {"player_1_wins": 0, "player_2_wins": 0, "player_ties": 0}

    for filename in trace_files:
        game_trace = load_game_trace(traces_path + filename)
        # print("winner: ", game_trace.game_winner)
        if game_trace.game_winner == 0:
            win_stats["player_ties"] += 1
        if game_trace.game_winner == 1:
            win_stats["player_1_wins"] += 1
        elif game_trace.game_winner == 2:
            win_stats["player_2_wins"] += 1

    return win_stats
 
def print_win_stats(win_stats, num_traces):
    print()
    print("Traces: ", num_traces)
    print("Player 1 Wins: ", win_stats["player_1_wins"])
    print("Player 2 Wins: ", win_stats["player_2_wins"])
    print("Player Ties: ", win_stats["player_ties"])
    print()
    print("Percent of Player 1 Wins: ", win_stats["player_1_wins"]/num_traces)
    print("Percent of Player 2 Wins: ", win_stats["player_2_wins"]/num_traces)
    print("Percent of Player Ties: ", win_stats["player_ties"]/num_traces)
    print()

def print_all_win_stats(traces_path):

    print()
    print("*****************************************************")
    print("Win Statistics")
    print("*****************************************************")

    trace_pattern = "p1_d1_p2_d1_trace_"
    trace_files = [f for f in listdir(traces_path) if (isfile(join(traces_path, f)) and re.search(trace_pattern, f))]
    num_traces = len(trace_files)
    win_stats = get_win_stats(traces_path, trace_files)

    print()
    print("*****************************************************")
    print("Results for " + trace_pattern)
    print_win_stats(win_stats, num_traces)

    # trace_pattern = "p1_d1_p2_d2_trace_"
    # trace_files = [f for f in listdir(traces_path) if (isfile(join(traces_path, f)) and re.search(trace_pattern, f))]
    # num_traces = len(trace_files)
    # win_stats = get_win_stats(traces_path, trace_files)

    # print()
    # print("*****************************************************")
    # print("Results for " + trace_pattern)
    # print_win_stats(win_stats, num_traces)

    # trace_pattern = "p1_d2_p2_d1_trace_"
    # trace_files = [f for f in listdir(traces_path) if (isfile(join(traces_path, f)) and re.search(trace_pattern, f))]
    # num_traces = len(trace_files)
    # win_stats = get_win_stats(traces_path, trace_files)

    # print()
    # print("*****************************************************")
    # print("Results for " + trace_pattern)
    # print_win_stats(win_stats, num_traces)

    # trace_pattern = "p1_d2_p2_d2_trace_"
    # trace_files = [f for f in listdir(traces_path) if (isfile(join(traces_path, f)) and re.search(trace_pattern, f))]
    # num_traces = len(trace_files)
    # win_stats = get_win_stats(traces_path, trace_files)

    # print()
    # print("*****************************************************")
    # print("Results for " + trace_pattern)
    # print_win_stats(win_stats, num_traces)

def prizes_to_value(prizes):
    prize_to_num = {"A":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":11, "Q":12, "K":13}
    total_value = 0
    for prize in prizes:
        total_value += prize_to_num[prize]
    return total_value

def get_count_played(moves):
    # get count times a card is played relative to the prize value.

    card_values = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
    prize_values = list(range(1,92))
    play_count = {}
    for card in card_values:
        play_count[card] = {}
        for val in prize_values:
            play_count[card][val] = 0 

    for move in moves:
        prize_cards = move["pre_play_data"]["prize_values"]
        prize_value = prizes_to_value(prize_cards)
        card_played = move["post_play_data"]["own_played_card"]
        # print()
        # print("prize_cards: ", prize_cards)
        # print("prize_valueL ", prize_value)
        # print("card_played: ", card_played)

        play_count[card_played][prize_value] += 1
    return play_count

def plot_count_played(play_count, title):
    prize_values = list(range(1,92))
    legend = []
    max_prize = 0
    for card in play_count.keys():
        play_vec = []
        legend.append(card)
        for val in prize_values:
            count = play_count[card][val]
            play_vec.append(count)

            if count > 0 and val > max_prize:
                max_prize = val

        plt.plot(prize_values, play_vec)

    plt.title(title)
    plt.xlim([1, max_prize])
    plt.legend(legend)
    plt.show()



########################################################################################

traces_path = "game_traces/"

print_all_win_stats(traces_path)

extract = ExtractTraceMoves("game_traces", 1, 1)
extract.get_good_moves()
all_moves = extract.get_all_moves()
good_moves = extract.get_good_moves()

# print()
# print(all_moves)
# print()

title = "All Moves"
all_move_cnts = get_count_played(all_moves)
plot_count_played(all_move_cnts, title)

title = "Good Moves"
good_move_cnts = get_count_played(good_moves)
plot_count_played(good_move_cnts, title)
