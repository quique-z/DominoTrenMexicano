class Heuristic:
    def __init__(self):
        self.heuristic_value_per_chip = 7  # 12.55 is avg for 12 chip games
        self.front_loaded_index = 0.99  # 1 gives no preference to chip ordering
        self.not_likely_to_have_chip_multiplier = 0.1
        self.play_chip_elsewhere_multiplier = 1.5
        self.penalty_for_playing_lone_double = 12