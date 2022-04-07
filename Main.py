from game.GameManager import GameManager
from ai.ChipNode import ChipNode
from ai.SequenceGeneration import *
from game.ChipFactory import *
import random
import time


fichas_para_robar = 12
mula_mas_alta = 12
mula_inicial = 12
n_jugadores = 4
historic_winners = [0] * n_jugadores

for i in range(10):
    game_manager = GameManager(fichas_para_robar, mula_mas_alta, mula_inicial, n_jugadores, 0)
    game_manager.name_players("Pety", "Anel", "Abuela", "Titi")
    game_winners = game_manager.play_ai_game()
    for player in game_winners:
        historic_winners[player] += 1

print(historic_winners)


"""

pool = create_chips(12)
random.shuffle(pool)
chips = []
for i in range(15):
            chip = pool.pop()
            chips.append(chip)

for chip in chips:
    print(chip)
cs = generate_sequence([12], chips, 12.55, 0.99)

print("Secuencia")

for chip in cs.get_chipset():
    print(chip)



for j in range(5, 25):
    total_time = 0
    max_time = -math.inf
    min_time = math.inf
    for k in range(100):
        pool = create_chips(12)
        random.shuffle(pool)
        chips = []
        for i in range(j):
            chip = pool.pop()
            chips.append(chip)
        millis = time.time() * 1000
        cs = generate_sequence([random.randrange(12)], chips, 12.55, 0.99)
        run_time = time.time() * 1000 - millis
        total_time += run_time
        if run_time > max_time:
            max_time = run_time
        if run_time < min_time:
            min_time = run_time
    print("Tiempo promedio en ordenar %s fichas es: " % j + "{:.0f}".format(total_time/100) + " ms. Max y min son %s ms y %s ms" % (max_time, min_time))


"""