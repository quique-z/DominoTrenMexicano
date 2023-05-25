# Very basic player. Follows the rules but plays a the first available move it can find. Mostly for debugging purposes, inheritance or for testing an AI against it.
import logging

from game.ChipNode import ChipNode
from game.ChipNodeList import ChipNodeList


class Player:

    def __init__(self, index, name=None):
        if name is None:
            self.name = index.__str__()
        else:
            self.name = name
        self.index = index
        self.chips = None
        self.say_one = True
        self.has_won = False
        self.total_points = 0
        self.remove_train = True
        self.eligible_to_win = False
        self.numbers_player_does_not_have = set()

    def init_round(self, chips, double_to_skip=None):
        self.chips = chips
        self.has_won = False
        self.eligible_to_win = False

    def init_turn(self, board):
        self.numbers_player_does_not_have = set()

    def end_turn(self, board):
        if len(self.chips) == 0:
            if board.get_forced_culprit_index() == self.index:
                self.eligible_to_win = True
                logging.info("%s is out of chips but the board is forced because of them, so they can't win yet." % self.name)
            else:
                self.has_won = True
                logging.info("%s wins this round!" % self.name)

    def add_chip(self, chip):
        self.chips.append(chip)
        self.numbers_player_does_not_have = set()
        logging.info("%s draws: %s" % (self.name, chip.__str__()))

    def remove_chip(self, chip):
        self.chips.remove(chip)
        logging.info("%s plays: %s" % (self.name, chip.__str__()))

    def can_play(self, board):
        if len(self.chips) == 0:
            logging.info("%s doesn't have chips, but it is their turn." % self.name)
            return False

        if board.is_forced():
            return self.can_play_forced(board)
        else:
            return self.can_play_any(board)

    def can_play_forced(self, board):
        for number in board.get_forced_numbers():
            if self.can_play_number(number):
                logging.info("%s is forced and has a chip to play" % self.name)
                return True
        logging.info("%s is forced and doesn't have a chip to play" % self.name)
        return False

    def can_play_any(self, board):
        for row in board.get_rows():
            if row.get_index() == self.index or (row.has_train() and not board.has_train(self.index)):
                for open_position in row.get_open_positions():
                    if self.can_play_number(open_position):
                        return True
        return False

    def can_play_number(self, number):
        for chip in self.chips:
            if number in chip:
                return True
        self.numbers_player_does_not_have.add(number)
        return False

    def play(self, board, players):
        if board.is_forced():
            logging.info("%s is forced: " % self.name)
            return self.play_forced(board)
        if board.get_row(self.index).can_play_many():
            logging.info("%s is playing many: " % self.name)
            return self.play_first(board)
        else:
            logging.info("%s is playing just one: " % self.name)
            return self.play_any(board)

    def play_any(self, board):
        for row in board.get_rows_random_start():
            if row.get_number() == self.index or (row.has_train() and not board.has_train(self.index)):
                for open_number in row.get_open_positions():
                    for chip in self.chips:
                        if open_number in chip:
                            cn = ChipNode(chip, open_number)
                            logging.info(self.name, " plays :", chip)
                            if chip.is_double():
                                can_play = self.can_play_number(open_number)
                                if can_play:
                                    for second_chip in self.chips:
                                        if open_number in second_chip:
                                            cn.add_next_node(ChipNode(second_chip, open_number))
                                            logging.info(self.name, " plays a second chip :", second_chip)
                                            break
                            return [ChipNodeList([cn]), row.get_number()]

    def play_forced(self, board):
        for number in board.get_forced_numbers():
            for chip in self.chips:
                if number in chip:
                    chip_to_play = chip
                    logging.info("%s plays :%s" % (self.name, chip_to_play))
                    return [ChipNodeList([ChipNode(chip, number)]), board.get_forced_row_index()]

    def get_current_points(self):
        total = 0
        for chip in self.chips:
            total += chip.get_value()
        return total

    def play_first(self, board):
        return self.play_any(board)

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

    def get_chip_count(self):
        return len(self.chips)

    def get_numbers_player_does_not_have(self):
        return self.numbers_player_does_not_have

    def will_say_one(self):
        return self.say_one

    def will_remove_train(self):
        return self.remove_train

    def has_chips(self, chips):
        for chip in chips:
            if chip not in self.chips:
                return False
        return True

    def __str__(self):
        s = ["Name: %s" % self.name,
             " Round points: %s" % self.get_current_points(),
             " Total points: %s" % self.total_points,
             " Chips: "]
        for i in self.chips:
            s.append(i.__str__())
            s.append(" ")
        return ''.join(s)
