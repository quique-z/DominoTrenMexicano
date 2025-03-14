import logging
import math
import random
import time
from typing import List, Set

from ai.TurnLog import TurnLog, TurnAction
from game import PlayableChipNode
from game.Board import Board
from game.ChipFactory import create_chips
from players.HeuristicCPUPlayer import HeuristicCPUPlayer
from players.HumanPlayer import HumanPlayer
from players.RandomCPUPlayer import RandomCPUPlayer
from players.SmartCPUPlayer import SmartCPUPlayer
from ui.Input import row_input


class GameManager:
    placeholder_names = ["Alice", "Bob", "Cindy", "Dan", "Emma", "Frank", "Gina", "Han", "Ivy", "Jane"]
    chips_per_player_table = [12, 12, 12, 12, 12, 10, 9, 8, 8, 7, 7]

    def __init__(self, random_py: int, smart_py: int, heuristic_py: int, human_py: int,
                 highest_double: int = 12, initial_double: int = 12, player_names: List[str] = None) -> None:

        self.n_players = random_py + smart_py + heuristic_py + human_py
        self.chips_per_player = self.chips_per_player_table[self.n_players]
        self.round_direction = -1 if initial_double else 1
        self.endgame_countdown = self.n_players
        self.highest_double = highest_double
        self.current_double = initial_double
        self.human_game = bool(human_py)
        self.global_winner = []
        self.seen_chips = None
        self.endgame = False
        self.players = []
        self.board = None
        self.turn = 0


        self.player_names = player_names if player_names else self.placeholder_names[:self.n_players]
        self.turn_offset = row_input(self.player_names) if self.human_game else random.randrange(self.n_players)

        # Init Players.
        for i in range(random_py):
            self.players.append(RandomCPUPlayer(i, self.highest_double, self.n_players, self.player_names[i]))

        for i in range(len(self.players), len(self.players) + smart_py):
            self.players.append(SmartCPUPlayer(i, self.highest_double, self.n_players, self.player_names[i]))

        for i in range(len(self.players), len(self.players) + heuristic_py):
            self.players.append(HeuristicCPUPlayer(i, self.highest_double, self.n_players, self.player_names[i]))

        for i in range(len(self.players), len(self.players) + human_py):
            self.players.append(HumanPlayer(i, self.highest_double, self.n_players, self.player_names[i]))


    def init_round(self) -> None:
        self.endgame_countdown = self.n_players
        self.seen_chips = set()
        self.endgame = False
        self.turn = 0

        chips = create_chips(self.highest_double, self.current_double, self.human_game)

        for player in self.players:
            starting_chips = {chips.pop() for _ in range(self.chips_per_player)}
            player.init_round(starting_chips, self.current_double)

        self.board = Board(self.n_players, self.current_double, chips, self.player_names)

    def end_round(self) -> None:
        global_best_score = math.inf
        round_winner = None

        for player in self.players:
            player.add_up_points()
            if player.is_round_winner():
                round_winner = player
            if player.get_total_points() < global_best_score:
                global_best_score = player.get_total_points()
                self.global_winner = [player]
            elif player.get_total_points() == global_best_score:
                self.global_winner.append(player)

        if not round_winner:
            min_score = math.inf
            for player in self.players:
                if player.get_current_points() < min_score:
                    round_winner = player
                    min_score = player.get_current_points()
                elif player.get_current_points() == min_score:
                    if player.get_total_points() < round_winner.get_total_points():
                        round_winner = player

        self.current_double += self.round_direction
        self.turn_offset = round_winner.get_index()

    def has_next_round(self) -> bool:
        return self.current_double >= 0 if self.round_direction == -1 else self.current_double <= self.highest_double

    def has_next_turn(self) -> bool:
        # Breaks stalemates when there are no more moves left to make.
        if not self.board.can_draw():
            self.endgame = True
            if self.endgame_countdown <= 0:
                return False
            # Rare condition where a player is eligible to win but hasn't because the board used to be forced
            # due to their fault. Can only happen when there are no chips to draw and the board is no longer forced.
            if not self.board.is_forced():
                for player in self.players:
                    if player.is_eligible_to_win():
                        player.declare_as_round_winner()
                        return False

        return not self.players[self.previous_player_id()].is_round_winner()

    def next_turn(self) -> None:
        active_player = self.players[self.current_player_id()]
        active_player.init_turn(self.board)

        can_play = active_player.can_play(self.board)
        if not can_play:
            self.validate_pass()
            if self.board.can_draw():
                self.draw_chip()
                can_play = active_player.can_play(self.board)

        if can_play:
            self.play()
            if self.endgame:
                self.endgame_countdown = self.n_players
        else:
            self.validate_pass()
            self.board.set_train(self.current_player_id())
            if self.endgame:
                self.endgame_countdown -= 1

        if active_player.get_chip_count() == 1 and self.board.can_draw() and not active_player.will_say_one():
            logging.info(f"{active_player.get_name()} did not say one.")
            self.draw_chip()

        active_player.end_turn(self.board)
        self.turn += 1

    def play(self) -> None:
        active_player = self.players[self.current_player_id()]
        logging.info(f"{active_player.get_name()} plays: ")
        playable_chip_node = active_player.play(self.board, self.players)
        self.validate_play(playable_chip_node)
        self.make_move(playable_chip_node)
        if playable_chip_node.ends_in_double():
            self.validate_unresolved_double(playable_chip_node)
            self.handle_unresolved_doubles(playable_chip_node)

    def handle_unresolved_doubles(self, playable_chip_node: PlayableChipNode) -> None:
        active_player = self.players[self.current_player_id()]
        logging.info(f"{active_player.get_name()} ends in unresolved double.")
        row = playable_chip_node.get_row()
        forced_numbers = playable_chip_node.get_chip_node().get_ending_doubles()
        self.board.set_forced(row, forced_numbers, self.current_player_id())

        if self.board.can_draw():
            self.draw_chip()
        if active_player.can_play(self.board):
            logging.info("Drew necessary number.")
            playable_chip_node = active_player.play(self.board, self.players)
            self.validate_play(playable_chip_node)
            self.make_move(playable_chip_node)
        else:
            logging.info("Did not draw necessary number.")
            self.validate_unresolved_double(playable_chip_node)

    def make_move(self, playable_chip_node: PlayableChipNode) -> None:
        active_player = self.players[self.current_player_id()]
        logging.info(f"{active_player.get_name()} plays: {playable_chip_node}")

        # Remove forced.
        if self.board.is_forced():
            self.board.remove_forced(playable_chip_node.get_chip_node().get_chip_side_to_play())

        # Remove train.
        if (self.current_player_id() == playable_chip_node.get_row
                and not playable_chip_node.ends_in_double()
                and not self.board.is_forced()
                and active_player.will_remove_train()):
            self.board.remove_train(self.current_player_id())

        # Play chips.
        active_player.remove_chips(playable_chip_node.get_chip_node().get_chipset())
        self.board.play_playable_chip_node(playable_chip_node)

    def validate_play(self, playable_chip_node: PlayableChipNode) -> None:
        chip_node = playable_chip_node.get_chip_node()
        row = playable_chip_node.get_row()

        tl = TurnLog(self.turn, self.current_player_id(), TurnAction.PLAYED_CHIPS, playable_chip_node.get_chipset(), None)
        self.update_turn_history(tl)

        if not chip_node:
            raise Exception("Empty move.")
        if not self.players[self.current_player_id()].has_chips(chip_node.get_chipset()):
            logging.info(playable_chip_node)
            raise Exception("Player tried to play a chip they do not have.")
        if chip_node.get_chipset() & self.seen_chips:
            raise Exception(f"Chip(s) {chip_node.get_chipset() & self.seen_chips} have been played before.")
        else:
            self.seen_chips.update(chip_node.get_chipset())

        if self.board.is_forced():
            if row != self.board.get_forced_row_index():
                logging.info(playable_chip_node)
                raise Exception("Board is forced but player is trying to play somewhere else.")
            if chip_node.get_chip_side_to_play() not in self.board.get_forced_numbers():
                logging.info(playable_chip_node)
                raise Exception("Chip does not contain forced number.")
            if len(chip_node) > 1:
                logging.info(playable_chip_node)
                raise Exception("Player tried to play too many chips.")
            return

        if chip_node.get_chip_side_to_play() not in self.board.get_row(row).get_open_positions():
            logging.info(playable_chip_node)
            raise Exception("Player tried to play a chip that does not match the numbers in the row.")
        if row != self.current_player_id() and self.board.get_row(self.current_player_id()).has_train():
            logging.info(playable_chip_node)
            raise Exception("Player tried to play elsewhere, but their row has a train.")
        if row != self.current_player_id() and not self.board.get_row(row).has_train():
            logging.info(playable_chip_node)
            raise Exception("Player tried to play in a row without train.")
        if len(chip_node) > 1:
            if row == self.current_player_id() and self.board.get_row(self.current_player_id()).can_play_many():
                pass
            elif len(chip_node) == 2 and chip_node.is_chip_double():
                pass
            else:
                logging.info(str(playable_chip_node))
                raise Exception("Player tried to play too many chips.")
        if playable_chip_node.ends_in_double():
            doubles = playable_chip_node.get_ending_doubles()
            for chip in self.players[self.current_player_id()].chips:
                if chip not in chip_node.get_chipset():
                    if doubles & chip.get_sides():
                        logging.info(str(playable_chip_node))
                        raise Exception("Player played a double but withheld from resolving it.")

    def validate_pass(self) -> None:
        player_numbers = {number for chip in self.players[self.current_player_id()].get_chips() for number in chip.get_sides()}

        if self.board.is_forced():
            open_positions = self.board.get_forced_numbers()
        else:
            if self.board.get_row(self.current_player_id()).has_train():
                open_positions = set(self.board.get_row(self.current_player_id()).get_open_positions())
            else:
                open_positions = set()
                for row in self.board.get_rows():
                    if row.has_train() or row.get_index() == self.current_player_id():
                        open_positions.update(row.get_open_positions())

        tl = TurnLog(self.turn, self.current_player_id(), TurnAction.PASS, None, open_positions)
        self.update_turn_history(tl)

        if player_numbers & open_positions:
            raise Exception(f"Player has numbers to play: {player_numbers & open_positions} but did not play them.")

    def validate_unresolved_double(self, playable_chip_node: PlayableChipNode) -> None:
        doubles = playable_chip_node.get_ending_doubles()
        chipset = playable_chip_node.get_chipset()

        for chip in self.players[self.current_player_id()].chips:
            if chip not in chipset and (chip.get_sides() & doubles):
                raise Exception(f"Player can resolve double but did not: {chip.get_sides() & doubles}.")

    def previous_player_id(self) -> int:
        return (self.turn + self.turn_offset - 1) % self.n_players

    def next_player_id(self) -> int:
        return (self.turn + self.turn_offset + 1) % self.n_players

    def current_player_id(self) -> int:
        return (self.turn + self.turn_offset) % self.n_players

    def update_turn_history(self, turn_log: TurnLog):
        self.board.update_turn_history(turn_log)

    def draw_chip(self) -> None:
        logging.info(f"{self.players[self.current_player_id()].get_name()} draws chip.")
        self.players[self.current_player_id()].add_chip(self.board.draw())
        tl = TurnLog(self.turn, self.current_player_id(), TurnAction.DREW, None, None)
        self.update_turn_history(tl)

    def play_game(self) -> List[int]:
        start_time = time.time() * 1000

        while self.has_next_round():
            self.init_round()
            while self.has_next_turn():
                self.next_turn()
                logging.info(self)
            self.end_round()

        end_time = time.time() * 1000

        logging.info(self)
        print(f"{end_time - start_time:.0f} ms")

        return [player.get_index() for player in self.global_winner]

    def __str__(self) -> str:
        s = [f"Turn #{self.turn}. The board looks like this:\n{self.board} \nPlayers: "]
        s.extend(f"\n{str(player)}" for player in self.players)

        s.append(f"\nPlayer's turn: {self.players[self.current_player_id()].get_name()}\n")

        s.append("Player(s) in the lead: ")
        s.extend(f"{player.get_name()} " for player in self.global_winner)

        s.append("\n\n\n")
        return "".join(s)

