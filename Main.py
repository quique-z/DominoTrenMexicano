from game.GameManager import GameManager
from ai.ChipNode import ChipNode
from ai.SequenceGeneration import *
from game.ChipFactory import *
import random
import time
"""
chips = []

chips.append(Chip(0,1))
chips.append(Chip(1,1))
chips.append(Chip(1,2))
chips.append(Chip(2,3))
chips.append(Chip(3,4))

cs = generate_sequence([5], chips, 5, 0.99)
print(cs)

while cs.has_chip_to_play():
    print("Turno")
    ctp = cs.get_best_chip_to_play()
    for i in ctp:
        print(i)
    print(cs)



pool = create_chips(12)
random.shuffle(pool)
chips = []
for i in range(12):
    chip = pool.pop()
    print("Ficha: " + chip.__str__())
    chips.append(chip)
    open_positions = []
for i in range(1, random.randrange(4)):
    open_positions.append(random.randrange(12))
    print("Posición: " + open_positions[i-1].__str__())
cs = generate_sequence(open_positions, chips, 12.55)

print(cs)
ctp = cs.get_best_chip_to_play()
for i in ctp:
    print(i)
print(cs)

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
        cs = generate_sequence([random.randrange(12)], chips, 12.55)
        run_time = time.time() * 1000 - millis
        total_time += run_time
        if run_time > max_time:
            max_time = run_time
        if run_time < min_time:
            min_time = run_time
    print("Tiempo promedio en ordenar %s fichas es: " % j + "{:.0f}".format(total_time/100) + " ms. Max y min son %s ms y %s ms" % (max_time, min_time))

"""
fichas_para_robar = 12
mula_mas_alta = 12
mula_inicial = 12
n_jugadores = 4
winners = [0, 0, 0, 0]
for i in range(100):
    game_manager = GameManager(fichas_para_robar, mula_mas_alta, mula_inicial, 0, 4)
    game_manager.name_players("Pety", "Anel", "Abuela", "Titi")
    winners[game_manager.play_ai_game()] += 1

print(winners)
