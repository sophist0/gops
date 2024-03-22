#!/usr/bin/env python3

from gops.game_traces import ExtractTraceGoodMoves

extract = ExtractTraceGoodMoves("game_traces", 1, 1)
extract.get_good_moves()
