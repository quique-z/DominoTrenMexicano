from game.GameManager import GameManager
from ai.ChipNode import ChipNode
from ai.SequenceGeneration import *
from game.Chip import Chip

fichas_para_robar = 12
mula_mas_alta = 12
mula_inicial = 12
n_jugadores = 4

chips = []
chips.append(Chip(3,5))
chips.append(Chip(5,5))
chips.append(Chip(5,1))
chips.append(Chip(5,10))
chips.append(Chip(5,8))

print(generate_sequence([1, 3], chips))




"""
winners = [0, 0, 0, 0]
for i in range(1):
    game_manager = GameManager(n_jugadores, fichas_para_robar, mula_mas_alta, mula_inicial)
    game_manager.name_players("Pety", "Anel", "Abuela", "Titi")
    winners[game_manager.play_ai_game()] += 1

print(winners)
"""
