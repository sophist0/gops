#!/usr/bin/env python3

import re
import pickle
from os import listdir
from os.path import isfile, join

# from gops.game import AIHumanGame, AIAIGame

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
########################################################################################

traces_path = "game_traces/"

trace_pattern = "p1_d1_p2_d1_trace_"
trace_files = [f for f in listdir(traces_path) if (isfile(join(traces_path, f)) and re.search(trace_pattern, f))]
num_traces = len(trace_files)
win_stats = get_win_stats(traces_path, trace_files)

print()
print("*****************************************************")
print("Results for " + trace_pattern)
print_win_stats(win_stats, num_traces)

trace_pattern = "p1_d1_p2_d2_trace_"
trace_files = [f for f in listdir(traces_path) if (isfile(join(traces_path, f)) and re.search(trace_pattern, f))]
num_traces = len(trace_files)
win_stats = get_win_stats(traces_path, trace_files)

print()
print("*****************************************************")
print("Results for " + trace_pattern)
print_win_stats(win_stats, num_traces)

trace_pattern = "p1_d2_p2_d1_trace_"
trace_files = [f for f in listdir(traces_path) if (isfile(join(traces_path, f)) and re.search(trace_pattern, f))]
num_traces = len(trace_files)
win_stats = get_win_stats(traces_path, trace_files)

print()
print("*****************************************************")
print("Results for " + trace_pattern)
print_win_stats(win_stats, num_traces)

trace_pattern = "p1_d2_p2_d2_trace_"
trace_files = [f for f in listdir(traces_path) if (isfile(join(traces_path, f)) and re.search(trace_pattern, f))]
num_traces = len(trace_files)
win_stats = get_win_stats(traces_path, trace_files)

print()
print("*****************************************************")
print("Results for " + trace_pattern)
print_win_stats(win_stats, num_traces)
