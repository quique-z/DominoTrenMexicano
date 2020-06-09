from DominoCubano.players.BasicPlayer import *
from DominoCubano.game.ChipFactory import *
from DominoCubano.game.Board import *
import random
import math
import time


class GameManager:

    def __init__(self, n_players, n_chips_per_player, highest_double, initial_double):
        self.chips = []
        self.n_chips_per_player = n_chips_per_player
        self.highest_double = highest_double
        self.current_double = initial_double
        self.board = None
        self.turn = 0
        self.endgame = False
        self.endgame_counter = 0
        players = []
        for i in range(n_players):
            players.append(Player(i))
        self.players = players

    def init_round(self):
        self.end_round()
        self.chips = create_chips_without_double(self.highest_double, self.current_double)
        random.shuffle(self.chips)

        for player in self.players:
            chips = []
            for i in range(self.n_chips_per_player):
                chips.append(self.chips.pop())
            player.init_turn(chips)

        self.board = Board(len(self.players), self.current_double, self.chips)
        self.current_double -= 1

    def end_round(self):
        min_score = math.inf
        winner = None
        for player in self.players:
            player.add_up_points()
            if player.get_current_points() < min_score:
                winner = player
                min_score = player.get_current_points()
            elif player.get_current_points() == min_score:
                if player.get_total_points() < winner.get_total_points():
                    winner = player
        self.turn = winner.get_index()

    def has_next_round(self):
        return self.current_double >= 0

    def name_players(self, *names):
        if len(names) == len(self.players):
            for i in range(len(names)):
                self.players[i].set_name(names[i])

    def has_next_turn(self):
        if not self.board.can_draw():
            self.endgame = True
            if self.endgame_counter >= len(self.players):
                return False
        return not self.players[self.previous_player_id()].is_round_winner()

    def next_turn(self):
        can_play = self.players[self.turn].can_play_any(self.board)

        if not can_play and self.board.can_draw():
            self.players[self.turn].add_chip(self.board.draw())
            can_play = self.players[self.turn].can_play_any(self.board)

        if can_play:
            self.players[self.turn].play_any(self.board)
            if self.endgame:
                self.endgame_counter = 0
        else:
            self.board.set_train(self.turn)
            if self.endgame:
                self.endgame_counter += 1

        self.turn = self.next_player_id()

    def previous_player_id(self):
        return (self.turn - 1) % len(self.players)

    def next_player_id(self):
        return (self.turn + 1) % len(self.players)

    def play_ai_game(self):
        millis = time.time() * 1000
        while self.has_next_round():
            self.init_round()
            while self.has_next_turn():
                print(self)
                self.next_turn()
        self.end_round()
        print(self)
        print(time.time() * 1000 - millis)

    def __str__(self):
        s = ["El tablero está así:\n", self.board.__str__(), "\nLos jugadores están así"]
        winner = ""
        min_points = math.inf
        for player in self.players:
            s.append("\n")
            s.append(player.__str__())
            if player.get_total_points() == min_points:
                winner = winner + ", " + player.get_name()
            elif player.get_total_points() < min_points:
                min_points = player.get_total_points()
                winner = player.get_name()
        s.append("\nEs turno de ")
        s.append(self.players[self.turn].get_name())
        s.append("\nVa ganando: ")
        s.append(winner)
        s.append("\n\n\n")
        return ''.join(s)
