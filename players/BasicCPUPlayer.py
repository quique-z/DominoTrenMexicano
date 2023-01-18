# Very basic player. Follows the rules but literally plays the first chip available regardless of how good of a move
# that ends up being. Mostly for debugging purposes, inheritance or for flexing an AI against it.
import logging

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

    def init_round(self, chips, double_to_skip=None):
        self.chips = chips
        self.has_won = False
        self.eligible_to_win = False

    def end_turn(self, board, say_one=True):
        if len(self.chips) == 1:
            # Saying "One" when you have 1 chip left is a best practice, but some AI players may chose not to do so and take the intentional penalty draw.
            if say_one:
                print("%s says: One!" % self.name)
            elif board.can_draw():
                print("%s intentionally skips saying \"One\"")
                self.add_chip(board.draw(self.index))

        elif len(self.chips) == 0:
            if board.get_forced_culprit() == self.index:
                self.eligible_to_win = True
                logging.info("%s is out of chips but the board is forced because of them, so they can't win yet." % self.name)
            else:
                self.has_won = True
                logging.info("%s wins this round!" % self.name)

    def add_chip(self, chip):
        self.chips.append(chip)
        logging.info("%s draws: %s" % (self.name, chip.__str__()))

    def can_play(self, board):
        if self.chips is None or len(self.chips) == 0:
            logging.info("%s doesn't have chips, but it is their turn." % self.name)
            return False

        if board.is_forced():
            return self.can_play_forced(board)
        else:
            return self.can_play_any(board)

    def can_play_forced(self, board):
        non_available_numbers = set()
        for number in board.get_forced_numbers():
            if self.can_play_number(number):
                logging.info("%s is forced and has a chip to play" % self.name)
                return True
            else:
                non_available_numbers.add(number)
        logging.info("%s is forced and doesn't have a chip to play" % self.name)
        board.set_numbers_player_does_not_have(self.index, non_available_numbers)
        return False

    def can_play_any(self, board):
        non_available_numbers = set()
        for row in board.get_rows():
            if row.get_index() == self.index or (row.has_train() and (not board.has_train(self.index))):
                for open_position in row.get_open_positions():
                    if self.can_play_number(open_position):
                        return True
                    else:
                        non_available_numbers.add(open_position)
        board.set_numbers_player_does_not_have(self.index, non_available_numbers)
        return False

    def can_play_number(self, number):
        for chip in self.chips:
            if number in chip:
                return True
        return False

    def play(self, board):
        logging.info("%s plays: " % self.name)
        if board.is_forced():
            logging.info("%s is forced" % self.name)
            self.play_forced(board)
        elif board.get_row(self.index).can_play_many():
            self.play_first(board)
        else:
            self.play_any(board)
        self.end_turn(board)

    def play_any(self, board):
        for row in board.get_rows():
            if row.get_index() == self.index or (row.has_train() and (not board.has_train(self.index))):
                for open_number in row.get_open_positions():
                    for chip in self.chips:
                        if open_number in chip:
                            chip_to_play = chip
                            self.chips.remove(chip)
                            board.play_chip(chip_to_play, open_number, row.get_index(), self.index)
                            board.remove_train(self.index)
                            logging.info(self.name, " plays :", chip_to_play)
                            if chip_to_play.is_double():
                                can_play = self.can_play_number(open_number)
                                if can_play:
                                    for second_chip in self.chips:
                                        if open_number in second_chip:
                                            second_chip_to_play = second_chip
                                            self.chips.remove(second_chip)
                                            board.play_chip(second_chip_to_play, open_number, row.get_index(), self.index)
                                            logging.info(self.name, " plays a second chip :", second_chip_to_play)
                                            return
                                else:
                                    board.set_numbers_player_does_not_have(self.index, [open_number])
                                if board.can_draw():
                                    drawn_chip = board.draw(self.index)
                                    self.add_chip(drawn_chip)
                                    can_play = open_number in drawn_chip
                                if can_play:
                                    self.chips.remove(drawn_chip)
                                    board.play_chip(drawn_chip, open_number, row.get_index(), self.index)
                                else:
                                    board.set_numbers_player_does_not_have(self.index, [open_number])
                                    board.set_forced(row.get_index(), open_number, self.index)
                            return

    def play_forced(self, board):
        row = board.get_forced_row()
        for number in board.get_forced_numbers():
            for chip in self.chips:
                if number in chip:
                    chip_to_play = chip
                    logging.info("%s plays :%s" % (self.name, chip_to_play))
                    self.chips.remove(chip)
                    board.play_chip(chip_to_play, number, row, self.index)
                    board.remove_forced(number)
                    if not board.is_forced and row == self.index:
                        board.remove_train(self.index)
                    return

    def get_current_points(self):
        if len(self.chips) == 0:
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

    def declare_as_round_winner(self):
        self.has_won = True

    def is_eligible_to_win(self):
        return self.eligible_to_win

    def set_name(self, name):
        self.name = name

    def get_index(self):
        return self.index

    def init_turn(self, board):
        board.clear_history(self.index)

    def __str__(self):
        s = ["Name: %s" % self.name,
             " Round points: %s" % self.get_current_points(),
             " Total points: %s" % self.total_points,
             " Chips: "]
        for i in self.chips:
            s.append(i.__str__())
            s.append(" ")
        return ''.join(s)
