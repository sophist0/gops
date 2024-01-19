#!/usr/bin/env python3

from gops.game import AIHumanGame, AIAIGame

HUMAN_PLAYER = True

if HUMAN_PLAYER:
    new_game = AIHumanGame()
else:
    new_game = AIAIGame()

new_game.run_game()
