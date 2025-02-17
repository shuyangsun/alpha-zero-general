from __future__ import print_function
import sys

sys.path.append("..")

from Game import Game
import numpy as np

from ctypes import *

from .XiangqiLogic import (
    NUM_COLS,
    NUM_ROWS,
    BOARD_SIZE,
    MAX_POSSIBLE_MOVES,
    get_init_board,
    move,
    valid_moves,
    get_winner,
    flip_board,
    mirror_horizontal,
    encode_board_state,
    board_str,
)


class XiangqiGame(Game):

    def __init__(self):
        pass

    def getInitBoard(self):
        # return initial board (numpy board)
        return get_init_board()

    def getBoardSize(self):
        return (1, BOARD_SIZE)

    def getActionSize(self):
        # return number of actions
        return MAX_POSSIBLE_MOVES + 1

    def getNextState(self, board, player, action):
        if action == 0xFFFF:
            # Invalid move
            return (board, -player)
        return (move(board, action), -player)

    def getValidMoves(self, board, player):
        res = np.zeros(self.getActionSize())
        n, _ = valid_moves(board, player)
        if n == 0:
            res[-1] = 1
            return res
        res[:n] = 1
        return res

    def getGameEnded(self, board, player):
        winner = get_winner(board)
        if winner == -2:
            return 0
        return winner

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        if player == 1:
            return board
        return flip_board(board)

    def getSymmetries(self, board, pi):
        assert len(pi) == MAX_POSSIBLE_MOVES + 1  # 1 for pass
        mirror_lr = mirror_horizontal(board)
        pi_lr = pi.copy()
        for row in range(NUM_ROWS):
            row_start = row * NUM_COLS
            for col in range(NUM_COLS // 2):
                left = pi_lr[row_start + col]
                pi_lr[row_start + col] = pi_lr[row_start + NUM_COLS - 1 - col]
                pi_lr[row_start + NUM_COLS - 1 - col] = left
        # TODO: add flip and mirror vertical.
        return [(mirror_lr, pi_lr)]

    def stringRepresentation(self, board):
        return encode_board_state(board)

    @staticmethod
    def display(board: np.ndarray):
        print(board_str(board))
