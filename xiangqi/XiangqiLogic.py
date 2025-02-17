import os
import sys

import numpy as np

from ctypes import *

BOARD_SIZE = 90
MAX_POSSIBLE_MOVES = 112

_LIBC_PATH = "lib/xiangqi_libc.so"

if not os.path.exists(_LIBC_PATH) and os.path.isfile(_LIBC_PATH):
    print("Cannot find lib/xiangqi_libc.so.", file=sys.stderr)
    sys.exit(1)

_libc = CDLL(_LIBC_PATH)
_libc.ResetBoard_C.argtypes = [c_uint8 * BOARD_SIZE]
_init_board = (c_uint8 * BOARD_SIZE)()
_libc.ResetBoard_C(_init_board)
_np_init_board = np.ctypeslib.as_array(_init_board)


def get_init_board() -> np.ndarray:
    return _np_init_board.copy()


class XiangqiBoard:
    board = (c_uint8 * BOARD_SIZE)()
    possible_moves = (c_uint16 * MAX_POSSIBLE_MOVES)()
    possible_boards = (c_uint8 * MAX_POSSIBLE_MOVES * BOARD_SIZE)()

    def __init__(self):
        _libc.ResetBoard_C(self.board)

    def get_board(self) -> np.ndarray:
        return np.ctypeslib.as_array(self.board)


print(XiangqiBoard().get_board())
