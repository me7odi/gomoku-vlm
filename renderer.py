import numpy as np
from PIL import Image
import numpy.typing as npt
from typing import Callable
from enum import Enum


class Anchor(Enum):
    """
    Anchor of the image to adjust the (x, y) coordinates.
    """

    MIN = 0.0
    CENTER = 0.5
    MAX = 1.0


CalcCoordsFn = Callable[[int, int], tuple[int, int, int, int, Anchor, Anchor]]


def calc_coords_gomoku(
    i: int, j: int, cell_size: int = 40, board_origin: tuple[int, int] = (0, 0)
):
    """
    Calculate the coordinates of a piece on the game board.
    """
    x0, y0 = board_origin
    w = h = cell_size

    x = x0 + j * cell_size
    y = y0 + i * cell_size
    return x, y, w, h, Anchor.CENTER, Anchor.CENTER


def adjust_xy(
    x: int, y: int, w: int, h: int, x_anchor: Anchor, y_anchor: Anchor
) -> tuple[int, int]:
    """
    Shifts the x and y coordinates of the image by multiplying with the provided anchor value.
    """
    x = int(x - w * x_anchor.value)
    y = int(y - h * y_anchor.value)

    return x, y


def render_single(
    img: Image.Image, i: int, j: int, piece: Image.Image, calc_coords: CalcCoordsFn
) -> Image.Image:
    """
    Render a single piece on the game board.
    """
    x, y, w, h, x_a, y_a = calc_coords(i, j)
    x, y = adjust_xy(x, y, w, h, x_a, y_a)
    piece = piece.resize((w, h), Image.LANCZOS) if img.size != (w, h) else piece
    img.paste(piece, (x, y), piece if piece.mode == "RGBA" else None)
    return img


def render(
    img: Image.Image,
    pieces: list[Image.Image],
    points: npt.NDArray[np.int8],
    old_points: npt.NDArray[np.int8] | None = None,
    calc_coords: CalcCoordsFn = calc_coords_gomoku,
) -> Image.Image:
    """
    Main render function
    """
    assert points.ndim == 2, f"Expected 2D array, got {points.ndim}D array"
    assert points.shape[0] == points.shape[1], (
        f"Expected square array, got {points.shape}"
    )
    assert points.dtype == np.int8, f"Expected int8 array, got {points.dtype}"
    if old_points is not None:
        assert old_points.shape == points.shape, f"{old_points.shape} != {points.shape}"
        assert points.dtype == old_points.dtype, f"{points.dtype} != {old_points.dtype}"
        indices = np.argwhere((points != old_points) & (points != 0))
    else:
        indices = np.argwhere(points != 0)
    for i, j in indices:
        img = render_single(img, i, j, pieces[points[i, j] - 1], calc_coords)
    return img