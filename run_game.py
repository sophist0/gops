#!/usr/bin/env python3

from gops.game import AIHumanGame, AIAIGame

HUMAN_PLAYER = False

if HUMAN_PLAYER:
    new_game = AIHumanGame()
else:
    new_game = AIAIGame(difficulty_1=2, difficulty_2=2)

# new_game.run_game()
trace_num = 1000
new_game.generate_traces(trace_num)
