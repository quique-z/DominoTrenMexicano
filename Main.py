from fractions import Fraction

from ai.ProbabilityMap import ProbabilityMap
from game.Chip import Chip
from game.GameManager import GameManager


pm = ProbabilityMap(2, 0, True)
# print(pm)

new_map = pm.detach_sub_probability_map(2)
pm.remove_chip_from_probability_map(Chip([0, 1]))
pm.withdraw_chip_from_probability_map(Chip([1, 1]))


print(pm)
"""

chips_to_draw = 7
highest_double = 12
initial_double = 12
basic_py = 7
simple_py = 1
heuristic_py = 0
n_players = basic_py + simple_py + heuristic_py
historic_winners = [0] * n_players
names = ["Pety", "Anel", "Abuela", "Titi", "Man", "Joe", "Manolo", "Paul", "Arnaldo", "Paco"]

for i in range(10):
    game_manager = GameManager(chips_to_draw, highest_double, initial_double, basic_py, simple_py, heuristic_py, names[:n_players])
    game_winners = game_manager.play_ai_game()
    for player in game_winners:
        historic_winners[player] += 1

print(historic_winners)


chips = []
chips.append(Chip(3, 7))
chips.append(Chip(0, 5))
chips.append(Chip(1, 2))
chips.append(Chip(6, 9))
chips.append(Chip(7, 12))
chips.append(Chip(9, 11))
chips.append(Chip(6, 6))
chips.append(Chip(3, 3))
chips.append(Chip(4, 4))
chips.append(Chip(7, 10))
chips.append(Chip(12, 12))
chips.append(Chip(1, 10))

cs = generate_sequence([7], chips, 7, 0.99)
for chip in cs.get_chipset():
    print(chip)
    

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