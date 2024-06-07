#!/usr/bin/env python3

import torchtext
torchtext.disable_torchtext_deprecation_warning()

from gops.game import AIHumanGame

new_game = AIHumanGame()
new_game.run_game()
