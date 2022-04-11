from game.GameManager import GameManager
from ai.ChipNode import ChipNode
from ai.SequenceGeneration import *
from game.ChipFactory import *
import random
import time

chips_to_draw = 12
highest_double = 12
initial_double = 12
n_players = 4
historic_winners = [0] * n_players

for i in range(10):
    game_manager = GameManager(chips_to_draw, highest_double, initial_double, n_players, 0, ["Pety", "Anel", "Abuela", "Titi"])
    game_winners = game_manager.play_ai_game()
    for player in game_winners:
        historic_winners[player] += 1

print(historic_winners)


"""
pool = create_chips(12)
random.shuffle(pool)
chips = []
for i in range(10):
            chip = pool.pop()
            chips.append(chip)

for chip in chips:
    print(chip)
cs = generate_sequence([12,0], chips, 12.55, 0.99)

print("Sequence")

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
        open_positions = []
        for i in range(random.randint(1,3)):
            open_positions.append(random.randrange(12))
        cs = generate_sequence(open_positions, chips, 12.55, 0.99)
        run_time = time.time() * 1000 - millis
        total_time += run_time
        if run_time > max_time:
            max_time = run_time
        if run_time < min_time:
            min_time = run_time
    print("Tiempo promedio en ordenar %s fichas es: " % j + "{:.0f}".format(total_time/100) + " ms. Max y min son %s ms y %s ms" % (max_time, min_time))

"""