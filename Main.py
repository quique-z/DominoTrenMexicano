import logging

from game.GameManager import GameManager

logging.info = print

chips_to_draw = [12, 12, 12, 12, 12, 10, 9, 8, 8, 7, 7]
human_py = 0
random_py = 0
simple_py = 7
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

"""

for j in range(5, 31):
    total_time = 0
    max_time = -math.inf
    min_time = math.inf
    for k in range(1):
        pool = ChipFactory.create_chips(12)
        random.shuffle(pool)
        chips = []
        for i in range(j):
            chips.append(pool.pop())
        millis = time.time() * 1000
        open_positions = []
        for i in range(random.randint(1, 3)):
            open_positions.append(random.randrange(12))
        cs = SequenceGeneration.generate_sequence(open_positions, chips, 12.55, 0.99, 3)
        logging.info(cs.__str__())
        run_time = time.time() * 1000 - millis
        total_time += run_time
        if run_time > max_time:
            max_time = run_time
        if run_time < min_time:
            min_time = run_time
    print("Average time to order %s chips is: " % j + "{:.0f}".format(total_time/1000) + " s. Max and Min are %s ms and %s ms" % (max_time, min_time))
"""
