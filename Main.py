import logging

from game.GameManager import GameManager

logging.info = print


human_py = 0
random_py = 4
smart_py = 1
heuristic_py = 1
n_players = random_py + smart_py + heuristic_py + human_py
historic_winners = [0 for _ in range(n_players)]

def play_many_games():
    for i in range(100):
        game_manager = GameManager(random_py, smart_py, heuristic_py, human_py)
        game_winners = game_manager.play_game()
        for player in game_winners:
            historic_winners[player] += 1
    print(historic_winners)

play_many_games()
# time_sequence_generation()
# test_sequence_generation()