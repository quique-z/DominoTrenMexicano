# This player considers all possible moves and weighs them using a heuristic function. It then chooses the highest ranking move.
from ai.ProbabilityMapList import ProbabilityMapList
from players.SimpleCPUPlayer import SimpleCPUPlayer
from ai.Heuristic import Heuristic


class HeuristicAIPlayer(SimpleCPUPlayer):
    def __init__(self, index, names, highest_double, n_chips_per_player):
        super().__init__(index, names[index])
        self.probability_map_list = ProbabilityMapList(names, highest_double, n_chips_per_player, index)
        self.heuristic = Heuristic()
        self.n_players = len(names)

    def init_round(self, chips, double_to_skip):
        super().init_round(chips)
        self.probability_map_list.init_round(chips, double_to_skip)

    def init_turn(self, board):
        super().init_turn(board)
        # Cycles through all players starting after self.index, excluding self.index
        for i in range(self.n_players - 1):
            mod_counter = (self.index + i + 1) % self.n_players
            move_list = board.get_move_history(mod_counter)
            for move in move_list:
                if move[0] == "Chip":
                    self.probability_map_list.chip_was_played_by_player(mod_counter, move[1])
                elif move[0] == "Numbers":
                    self.probability_map_list.remove_numbers_from_probability_map(mod_counter, move[1])
                elif move[0] == "Draw":
                    self.probability_map_list.player_draws_chips(mod_counter)

    def add_chip(self, chip):
        super().add_chip(chip)
        self.probability_map_list.chip_was_seen(chip)

    def __str__(self):
        s = [super().__str__(), self.probability_map_list.__str__()]
        return ''.join(s)
