import tkinter as tk
import random
from threading import Lock

COLORS = ['gray', 'lightgreen', 'pink', 'blue', 'orange', 'purple', 'red', 'yellow', 'cyan']


class Columns():
    GAME_HEIGHT = 20
    GAME_WIDTH = 10
    #initial scores
    SCORE_PER_ELIMINATED_LINES = (0, 40, 100, 300, 1200)
    TETROMINOS = [
        [(0, 0), (0, 1), (1, 0), (1, 1)],  # O
        [(0, 0), (0, 1), (1, 1), (2, 1)],  # L
        [(0, 1), (1, 1), (2, 1), (2, 0)],  # J
        [(0, 1), (1, 0), (1, 1), (2, 0)],  # Z
        [(0, 1), (1, 0), (1, 1), (2, 1)],  # T
        [(0, 0), (1, 0), (1, 1), (2, 1)],  # S
        [(0, 1), (1, 1), (2, 1), (3, 1)],  # I
    ]