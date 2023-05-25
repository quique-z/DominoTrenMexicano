from random import randrange

from game.Row import Row


class Board:

    def __init__(self, n_players, center_chip_double, chips, player_names=None):
        if player_names is None:
            player_names = range(n_players)
        self.center_double = center_chip_double
        self.n_players = n_players
        self.draw_pile = chips
        self.forced = False
        self.forced_row = -1
        self.forced_numbers = []
        self.forced_culprit = -1
        self.rows = []
        for i in range(n_players):
            self.rows.append(Row(i, center_chip_double, player_names[i]))

    def play_chip(self, chip_to_play, side_to_play, row_to_play):
        if chip_to_play.is_double():
            self.rows[row_to_play].add_open_positions(side_to_play)
        else:
            self.rows[row_to_play].swap_open_positions(side_to_play, chip_to_play.get_other_side(side_to_play))

    def play_chip_node_list(self, chip_node_list, row_to_play):
        while chip_node_list.has_chip_to_play():
            cn = chip_node_list.get_best_chip_to_play()
            self.play_chip_nodes(cn, row_to_play)

    def play_chip_nodes(self, chip_node, row_to_play):
        for chip in chip_node.get_next_move_as_chip_list():
            self.play_chip(chip, chip_node.get_chip_side_to_play(), row_to_play)

    def set_forced(self, row, numbers, culprit):
        self.forced = True
        self.forced_row = row
        self.forced_numbers.extend(numbers)
        self.forced_culprit = culprit
        self.set_train(culprit)

    def remove_forced(self, number):
        self.forced_numbers.remove(number)
        if len(self.forced_numbers) == 0:
            self.forced = False
            self.forced_row = -1
            self.forced_culprit = -1

    def is_forced(self):
        return self.forced

    def get_forced_row_index(self):
        return self.forced_row

    def get_forced_numbers(self):
        return self.forced_numbers

    def get_forced_culprit_index(self):
        return self.forced_culprit

    def get_row(self, i):
        return self.rows[i]

    def get_rows(self):
        return self.rows

    def get_rows_random_start(self):
        i = randrange(len(self.rows))
        return self.rows[i:] + self.rows[:i]

    def can_draw(self):
        return len(self.draw_pile) > 0

    def draw(self):
        return self.draw_pile.pop()

    def set_train(self, index):
        self.rows[index].set_train()

    def remove_train(self, index):
        self.rows[index].remove_train()

    def has_train(self, index):
        return self.rows[index].has_train()

    def __str__(self):
        s = ["Center double: %s" % self.center_double,
             "\nPlayers: %s" % len(self.rows),
             "\nChips in draw pile: %s" % len(self.draw_pile)]
        for row in self.rows:
            s.append("\n%s" % row.__str__())
        if self.forced:
            s.append("\nAnd board is forced to row " + self.forced_row.__str__())
            s.append("\nOn numbers " + self.forced_numbers.__str__())
        return ''.join(s)
