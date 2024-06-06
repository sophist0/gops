#!/usr/bin/env python3

import time

from gops.game import AIHumanGame, AIAIGame

# HUMAN_PLAYER = False
HUMAN_PLAYER = True

start = time.time()

if HUMAN_PLAYER:
    new_game = AIHumanGame()
    new_game.run_game()
else:
    # trace_num = 10000
    trace_num = 1000

    # new_game = AIAIGame(difficulty_1=1, difficulty_2=4)
    # new_game.generate_traces(trace_num)

    # new_game = AIAIGame(difficulty_1=2, difficulty_2=4)
    # new_game.generate_traces(trace_num)

    # new_game = AIAIGame(difficulty_1=3, difficulty_2=4)
    # new_game.generate_traces(trace_num)

    new_game = AIAIGame(difficulty_1=1, difficulty_2=4)

    # TODO: Parallize the trace generation to make the bootstrap training on traces generated from previous models faster.
    # TODO: Try cleaning the dataset so that for every state there is only one best move (the most frequent best move
    # for that state). This might make training easier but I'm not sure how it would effect generalization.
    # Actually not sure this model is generalizing at all.
    new_game.generate_traces(trace_num)

end = time.time()

print()
print("Running time: ", end-start)
print()
