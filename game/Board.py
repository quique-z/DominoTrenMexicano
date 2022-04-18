from game.Row import Row


class Board:

    def __init__(self, n_players, center_chip_double, chips, player_names=[]):
        if not player_names:
            player_names = range(n_players)
        self.list_of_numbers_players_do_not_have = []
        self.players_who_drew = [0] * n_players
        self.center_double = center_chip_double
        self.draw_pile = chips
        self.forced = False
        self.forced_row = -1
        self.forced_numbers = []
        self.forced_culprit = -1
        self.rows = []
        for i in range(n_players):
            self.rows.append(Row(i, center_chip_double, player_names[i]))
            self.list_of_numbers_players_do_not_have.append(set())

    def play_chip(self, chip_to_play, side_to_play, row):
        if chip_to_play.is_double():
            self.rows[row].add_open_positions(side_to_play)
        else:
            self.rows[row].swap_open_positions(side_to_play, chip_to_play.get_other_side(side_to_play))

    def set_forced(self, row, number, culprit):
        self.forced = True
        self.forced_row = row
        self.forced_numbers.append(number)
        self.forced_culprit = culprit
        self.set_train(culprit)

    def remove_forced(self, number):
        self.forced_numbers.remove(number)
        if len(self.forced_numbers) == 0:
            self.forced = False
            self.forced_row = -1
            self.forced_culprit = -1

    def set_numbers_player_does_not_have(self, index, numbers):
        self.list_of_numbers_players_do_not_have[index] = self.list_of_numbers_players_do_not_have[index].union(numbers)

    def get_numbers_players_do_not_have(self):
        return self.list_of_numbers_players_do_not_have

    def clear_numbers_player_does_not_have(self, index):
        self.list_of_numbers_players_do_not_have[index] = set()

    def get_players_who_drew(self):
        return self.players_who_drew

    def clear_players_who_drew(self, index):
        self.players_who_drew[index] = 0

    def is_forced(self):
        return self.forced

    def get_forced_row(self):
        return self.forced_row

    def get_forced_numbers(self):
        return self.forced_numbers

    def get_forced_culprit(self):
        return self.forced_culprit

    def get_row(self, i):
        return self.rows[i]

    def get_rows(self):
        return self.rows

    def can_draw(self):
        return len(self.draw_pile) > 0

    def draw(self, player_index):
        self.players_who_drew[player_index] += 1
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
