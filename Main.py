from game.GameManager import GameManager
from ai.ChipNode import ChipNode
from ai.SequenceGeneration import *
from game.ChipFactory import *
import random

fichas_para_robar = 12
mula_mas_alta = 12
mula_inicial = 12
n_jugadores = 4


"""
pool = create_chips(12)
random.shuffle(pool)
chips = []
for i in range(20):
    chips.append(pool.pop())

cs = generate_sequence([9,3,5,2,9], chips, 12.55, 0)
print(cs.get_value())
print(cs)

"""

winners = [0, 0, 0, 0]
for i in range(1):
    game_manager = GameManager(fichas_para_robar, mula_mas_alta, mula_inicial, 0, 4)
    game_manager.name_players("Pety", "Anel", "Abuela", "Titi")
    winners[game_manager.play_ai_game()] += 1

print(winners)
