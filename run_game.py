#!/usr/bin/env python3

#import torchtext
#torchtext.disable_torchtext_deprecation_warning()

from gops.game import AIHumanGame

transformer_params = {"epochs": 7,
                    "version": 45,
                    "topk": 1,
                    "run_device": "cpu",
                    "train_device": "xpu",
                    "tokenizer": "HF",
                    "nproc": 12}

new_game = AIHumanGame(transformer_params)
new_game.run_game()
