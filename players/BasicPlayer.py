# Very basic player. Follows the rules but literally plays the first chip available regardless of how good of a move
# that ends up being. Mostly for debugging purposes, inheritance or for flexing an AI against it.


class Player:

    def __init__(self, index, name=None):
        if name is None:
            self.name = index.__str__()
        else:
            self.name = name
        self.index = index
        self.chips = None
        self.total_points = 0
        self.has_won = False
        self.eligible_to_win = False

    def init_round(self, chips):
        self.chips = chips
        self.has_won = False
        self.eligible_to_win = False

    def end_turn(self, board):
        if len(self.chips) == 1:
            # Saying "One" is a best practice, but some AI players may chose not to do so and take the intentional draw.
            print("%s says: One!" % self.name)
        elif len(self.chips) == 0:
            if board.get_forced_culprit() == self.index:
                self.eligible_to_win = True
                print("%s is out of chips but the board is forced because of them, so they can't win yet." % self.name)
            else:
                self.has_won = True
                print("%s wins this round!" % self.name)

    def add_chip(self, chip):
        self.chips.append(chip)
        print("%s draws: %s" % (self.name, chip.__str__()))

    def can_play_any(self, board):
        if self.chips is None or len(self.chips) == 0:
            print("%s doesn't have chips, but it is their turn." % self.name)
            return False

        if board.is_forced():
            return self.can_play_forced(board)

        for row in board.get_rows():
            if row.get_index() == self.index or (row.has_train() and (not board.has_train(self.index))):
                for open_position in row.get_open_positions():
                    if self.can_play_number(open_position):
                        return True
        return False

    def can_play_forced(self, board):
        numbers = board.get_forced_numbers()
        for number in numbers:
            if self.can_play_number(number):
                print("%s is forced and has a chip to play" % self.name)
                return True
        print("%s is forced and doesn't have a chip to play" % self.name)
        return False

    def can_play_number(self, number):
        for chip in self.chips:
            if chip.__contains__(number):
                return True
        return False

    def play(self, board):
        if board.is_forced():
            self.play_forced(board)
        else:
            self.play_any(board)
        self.end_turn(board)

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
                            print(self.name, " plays :", chip_to_play)
                            if chip_to_play.is_double():
                                board.set_forced(row.get_index(), chip_to_play.get_side_a(), self.index)
                                can_play = self.can_play_number(chip_to_play.get_side_a())
                                if not can_play and board.can_draw():
                                    drawn_chip = board.draw()
                                    self.add_chip(drawn_chip)
                                    can_play = drawn_chip.__contains__(chip_to_play.get_side_a())
                                if can_play:
                                    self.play(board)
                                else:
                                    board.set_train(self.index)
                            return

    def play_forced(self, board):
        for number in board.get_forced_numbers():
            for chip in self.chips:
                if chip.__contains__(number):
                    chip_to_play = chip
                    print(self.name, " plays :", chip_to_play)
                    self.chips.remove(chip)
                    board.play_chip(chip_to_play, number, board.get_forced_row())
                    board.remove_forced(number)
                    if not board.is_forced and board.get_forced_row == self.index:
                        board.remove_train(self.index)
                    return

    def get_current_points(self):
        if self.chips is None or len(self.chips) == 0:
            return 0
        total = 0
        for chip in self.chips:
            total += chip.get_value()
        return total

    def play_first(self, board):
        self.play_any(board)

    def get_total_points(self):
        return self.total_points

    def add_up_points(self):
        self.total_points += self.get_current_points()

    def get_name(self):
        return self.name

    def is_round_winner(self):
        return self.has_won

    def declare_round_winner(self):
        self.has_won = True

    def is_eligible_to_win(self):
        return self.eligible_to_win

    def set_name(self, name):
        self.name = name

    def get_index(self):
        return self.index

    def __str__(self):
        s = ["Name: %s" % self.name,
             " Round points: %s" % self.get_current_points(),
             " Total points: %s" % self.total_points,
             " Chips: "]
        for i in self.chips:
            s.append(i.__str__())
            s.append(" ")
        return ''.join(s)
