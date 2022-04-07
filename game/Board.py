from game.Row import Row


class Board:

    def __init__(self, n_players, center_chip_double, chips, player_names=None):
        if player_names is None:
            player_names = range(n_players)
        elif len(player_names != n_players):
            raise Exception("Number of players and list of player names are not the same size.")

        self.center_double = center_chip_double
        self.draw_pile = chips
        self.forced = False
        self.forced_row = -1
        self.forced_numbers = []
        self.rows = []
        for i in range(n_players):
            self.rows.append(Row(i, center_chip_double, player_names[i]))

    def play_chip(self, chip_to_play, side_to_play, row):
        if chip_to_play.is_double():
            self.rows[row].add_open_positions(side_to_play)
        else:
            self.rows[row].swap_open_positions(side_to_play, chip_to_play.get_other_side(side_to_play))

    def set_forced(self, row, numbers):
        self.forced = True
        self.forced_row = row
        self.forced_numbers.append(numbers)

    def remove_forced(self, number):
        self.forced_numbers.remove(number)
        if len(self.forced_numbers) == 0:
            self.forced = False
            self.forced_row = -1

    def is_forced(self):
        return self.forced

    def get_forced_row(self):
        return self.forced_row

    def get_forced_numbers(self):
        return self.forced_numbers

    def get_row(self, i):
        return self.rows[i]

    def get_rows(self):
        return self.rows

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
            s.append("\nRow %s has these open positions: " % row.get_name())
            s.append(row.__str__())
            s.append("and ")
            if row.has_train():
                s.append("has train")
            else:
                s.append("doesn't have train")
        if self.forced:
            s.append("\nAnd board is forced to row " + self.forced_row.__str__())
            s.append("\nOn numbers " + self.forced_numbers.__str__())
        return ''.join(s)
