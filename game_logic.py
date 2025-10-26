import random

import numpy as np
import numpy.typing as npt

def create_game(size: int = 15):
    return np.zeros((size, size), dtype=np.int8)


def position_is_empty(board: npt.NDArray, y: int, x: int) -> bool:
    return board[y, x] == 0


def make_move(board: npt.NDArray, y: int, x: int, player: int):
    if not (0 <= y < board.shape[0]):
        raise ValueError("y value out of board range")
    if not (0 <= x < board.shape[1]):
        raise ValueError("x value out of board range")
    if player not in [1, 2]:
        raise ValueError("player must be either 1 or 2")
    if not (position_is_empty(board, y, x)):
        raise RuntimeError("position already occupied")
    board[y, x] = player


def _get_random_empty_position(board: npt.NDArray, rng: random.Random) -> tuple[int, int]:
    """Return a random (y, x) that is currently empty."""
    if not isinstance(board, np.ndarray):
        raise RuntimeError("board must be a numpy array.")
    if not isinstance(rng, random.Random):
        raise TypeError('rng must be a Random.')

    empties = np.argwhere(board == 0)  # shape: (k, 2) rows of empty [y, x] points
    if len(empties) == 0:
        raise RuntimeError("board is full")

    # Draw random [y, x] from empties,
    i = rng.randint(0, len(empties) - 1) # randint is inclusive for upper-bound as well, keep -1
    y, x = empties[i] # Otherwise not plain python ints
    return y, x


def perform_random_valid_move(board: npt.NDArray, player: int, rng: random.Random) -> tuple[int, int]:
    """
    Perform a random, but valid move for the given player.
    Returns the (y, x) position where the move was performed.
    """
    if not isinstance(board, np.ndarray):
        raise RuntimeError("board must be a numpy array.")
    if not (player in [1, 2]):
        raise RuntimeError("player must be either 1 or 2")

    y, x = _get_random_empty_position(board, rng)
    make_move(board, y, x, player)
    return y, x

def _has_won_helper(board: npt.NDArray, n: int, player: int):
    mask = (board == player).astype(int)
    kernel = np.ones(n, dtype=int)  # dim of win condition

    conv = np.convolve(mask, kernel, mode="valid")
    return np.any(conv == n)


def has_won(board, n: int, player: int) -> bool:
    """
    returns true if the win condition is satisfied by the given player (n in a row), otherwise false
    """

    # Check horizontals
    size = board.shape[0]
    for i in range(0, size):
        col = board[:, i]
        if _has_won_helper(col, n, player):
            return True
        row = board[i, :]
        if _has_won_helper(row, n, player):
            return True

    # Check diagonals
    for offset in range(-size + n, size - n + 1):
        diag1 = np.diag(board, k=offset)
        if _has_won_helper(diag1, n, player):
            return True
        diag2 = np.diag(np.fliplr(board), k=offset)
        if _has_won_helper(diag2, n, player):
            return True
    return False
