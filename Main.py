import logging

from ai.SequenceGeneration import time_sequence_generation
from game.GameManager import GameManager

logging.info = print

chips_to_draw = [12, 12, 12, 12, 12, 10, 9, 8, 8, 7, 7]
human_py = 0
random_py = 9
simple_py = 1
heuristic_py = 0
n_players = random_py + simple_py + heuristic_py + human_py
highest_double = 12
initial_double = highest_double
historic_winners = [0 for _ in range(n_players)]
names = ["Alice", "Bob", "Cindy", "Dan", "Emma", "Frank", "Gina", "Han", "Ivy", "Jane"]

for i in range(100):
    game_manager = GameManager(chips_to_draw[n_players], highest_double, initial_double, random_py, simple_py, heuristic_py, human_py, names[:n_players])
    game_winners = game_manager.play_ai_game()
    for player in game_winners:
        historic_winners[player] += 1
print(historic_winners)


# time_sequence_generation()

