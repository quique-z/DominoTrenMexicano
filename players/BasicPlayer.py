class Player:

    def __init__(self, index):
        self.index = index
        self.name = index.__str__()
        self.chips = None
        self.total_points = 0
        self.has_won = False

    def init_round(self, chips):
        self.chips = chips
        self.has_won = False

    def add_chip(self, chip):
        self.chips.append(chip)
        print(self.name + " roba: " + chip.__str__())

    def can_play_any(self, board):
        if self.chips is None or len(self.chips) == 0:
            if board.get_forced_row() != self.index:
                self.has_won = True
                print("Gané de manera chistosa")
            return False

        if board.is_forced():
            return self.can_play_forced(board)

        for row in board.get_rows():
            if row.get_index() == self.index or (row.has_train() and (not board.has_train(self.index))):
                for open_position in row.get_open_positions():
                    if self.can_play_number(open_position):
                        return True
        return False

    def can_play_number(self, number):
        for chip in self.chips:
            if chip.__contains__(number):
                return True
        return False

    def can_play_forced(self, board):
        print(self.name + " está obligada")
        numbers = board.get_forced_numbers()
        for number in numbers:
            if self.can_play_number(number):
                return True
        return False

    def play(self, board):
        print(self.name + " juega: ")
        if board.is_forced():
            self.play_forced(board)
        elif board.get_row(self.index).can_play_many():
            self.play_first(board)
        else:
            self.play_any(board)

    def play_any(self, board):
        for row in board.get_rows():
            if row.get_index() == self.index or (row.has_train() and (not board.has_train(self.index))):
                for open_number in row.get_open_positions():
                    for chip in self.chips:
                        if chip.__contains__(open_number):
                            chip_to_play = chip
                            self.chips.remove(chip)
                            board.play_chip(chip_to_play, open_number, row.get_index())
                            board.remove_train(self.index)
                            print(chip_to_play)
                            if chip_to_play.is_double():
                                board.set_forced(row.get_index(), chip_to_play.get_side_a())
                                can_play = self.can_play_number(chip_to_play.get_side_a())
                                if not can_play and board.can_draw():
                                    self.add_chip(board.draw())
                                    can_play = self.can_play_number(chip_to_play.get_side_a())
                                if can_play:
                                    self.play(board)
                                else:
                                    board.set_train(self.index)
                            self.end_turn(board)
                            return

    def play_forced(self, board):
        for number in board.get_forced_numbers():
            for chip in self.chips:
                if chip.__contains__(number):
                    chip_to_play = chip
                    print(chip_to_play)
                    self.chips.remove(chip)
                    board.play_chip(chip_to_play, number, board.get_forced_row())
                    board.remove_forced(number)
                    if not board.is_forced and board.get_forced_row == self.index:
                        board.remove_train(self.index)
                    self.end_turn(board)
                    return

    def get_current_points(self):
        if self.chips is None or len(self.chips) == 0:
            return 0
        total = 0
        for chip in self.chips:
            total += chip.get_value()
        return total

    def get_total_points(self):
        return self.total_points

    def add_up_points(self):
        self.total_points += self.get_current_points()

    def get_name(self):
        return self.name

    def is_round_winner(self):
        return self.has_won

    def set_name(self, name):
        self.name = name

    def get_index(self):
        return self.index

    def end_turn(self, board):
        if len(self.chips) == 1:
            print("%s: ¡Uno!" % self.name)
        elif len(self.chips) == 0:
            # TODO: puedes ganar si tu ultima ficha es mula y otro jugador la desbloquea
            if not board.is_forced or board.get_forced_row() != self.index:
                self.has_won = True

    def play_first(self, board):
        self.play_any(board)

    def __str__(self):
        s = ["Nombre: ", self.name, " Puntos Actuales: %s" % self.get_current_points(),
             " Puntos totales: %s" % self.total_points, " Fichas: "]
        for i in self.chips:
            s.append(i.__str__())
            s.append(" ")
        return ''.join(s)
