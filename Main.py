from game.GameManager import GameManager
from ai.ChipSequence import ChipSequence
from game.Chip import Chip

fichas_para_robar = 12
mula_mas_alta = 12
mula_inicial = 12
n_jugadores = 4

#chip1 = Chip(3,5)
#chip2 = Chip(5,0)
#cs1 = ChipSequence(chip1)
#cs2 = ChipSequence(chip2)

#cs1.add_next(cs2)

#print(cs1)

winners = [0, 0, 0, 0]
for i in range(1):
    game_manager = GameManager(n_jugadores, fichas_para_robar, mula_mas_alta, mula_inicial)
    game_manager.name_players("Pety", "Anel", "Abuela", "Titi")
    winners[game_manager.play_ai_game()] += 1

print(winners)
