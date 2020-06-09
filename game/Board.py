from game.Row import Row


class Board:

    def __init__(self, n_players, center_chip_double, chips):
        self.center_double = center_chip_double
        self.draw_pile = chips
        self.forced = False
        self.forced_row = 0
        self.forced_numbers = []
        self.rows = []
        for i in range(n_players):
            self.rows.append(Row(i, center_chip_double))

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

    def play_chip(self, chip_to_play, side_to_play, row):
        if chip_to_play.is_double():
            self.rows[row].add_open_positions(side_to_play)
        else:
            self.rows[row].swap_open_positions(side_to_play, chip_to_play.get_other_side(side_to_play))

    def is_forced(self):
        return self.forced

    def set_forced(self, row, numbers):
        self.forced = True
        self.forced_row = row
        self.forced_numbers.append(numbers)

    def remove_forced(self, number):
        self.forced_numbers.remove(number)
        if len(self.forced_numbers) == 0:
            self.forced = False

    def get_forced_row(self):
        return self.forced_row

    def get_forced_numbers(self):
        return self.forced_numbers

    def __str__(self):
        s = ["Mula Central: %s" % self.center_double, "\nJugadores: %s" % len(self.rows),
             "\nFichas para robar: %s" % len(self.draw_pile)]
        for row in self.rows:
            s.append("\nCarril %s tiene estas posiciones abiertas: " % row.get_index())
            s.append(row.__str__())
            s.append("y ")
            if not row.has_train():
                s.append("no ")
            s.append("tiene tren")
        if self.forced:
            s.append("\nY están obligados al carril " + self.forced_row.__str__())
        return ''.join(s)
