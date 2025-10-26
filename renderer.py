import numpy as np
from PIL import Image
import numpy.typing as npt
from typing import Callable, Literal
from enum import Enum

class Anchor(Enum):
    """
    Anchor of the image as (fx, fy)
    TL = Top_Left, etc.
    """
    TL = (0.0, 0.0)
    TC = (0.5, 0.0)
    TR = (1.0, 0.0)
    CL = (0.0, 0.5)
    CC = (0.5, 0.5)
    CR = (1.0, 0.5)
    BL = (0.0, 1.0)
    BC = (0.5, 1.0)
    BR = (1.0, 1.0)

CalcCoordsFn = Callable[[int, int], tuple[int, int, int, int, Anchor]]


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
    return x, y, w, h, Anchor.TL


def adjust_xy(x: int, y: int, w: int, h: int, image_anchor: Anchor) -> tuple[int, int]:
    x = int(x - w * image_anchor.value[0])
    y = int(y - h * image_anchor.value[1])

    return x, y


def render_single(
    img: Image.Image, i: int, j: int, piece: Image.Image, calc_coords: CalcCoordsFn
) -> Image.Image:
    """
    Render a single piece on the game board.
    """
    x, y, w, h, center = calc_coords(i, j)
    x, y = adjust_xy(x, y, w, h, center)
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
        indices = np.nonzero(points)
    for i, j in zip(*indices):
        img = render_single(img, i, j, pieces[points[i, j] - 1], calc_coords)
    return img
