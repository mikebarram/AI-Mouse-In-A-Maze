import random
from enum import Enum

import numpy as np


class Directions(Enum):
    """Directions a maze can go in"""

    DIRECTION_UP = 1
    DIRECTION_DOWN = 2
    DIRECTION_LEFT = 3
    DIRECTION_RIGHT = 4


class Backtracking:
    """backtracking algorithm for creating a maze"""

    def __init__(self, height, width):
        """heigth and width of maze should be odd, so add one if even"""
        if width % 2 == 0:
            width += 1
        if height % 2 == 0:
            height += 1

        self.width = width
        self.height = height

    def create_maze(self):
        """create a maze"""
        maze = np.ones((self.height, self.width), dtype=float)

        for i in range(self.height):
            for j in range(self.width):
                if i % 2 == 1 or j % 2 == 1:
                    maze[i, j] = 0
                if i == 0 or j == 0 or i == self.height - 1 or j == self.width - 1:
                    maze[i, j] = 0.5

        maze_sx = random.choice(range(2, self.width - 2, 2))
        maze_sy = random.choice(range(2, self.height - 2, 2))

        self.generator(maze_sx, maze_sy, maze)

        for i in range(self.height):
            for j in range(self.width):
                if maze[i, j] == 0.5:
                    maze[i, j] = 1

        return maze

    def generator(self, maze_cx, maze_cy, grid):
        """maze generator"""
        grid[maze_cy, maze_cx] = 0.5

        if (
            grid[maze_cy - 2, maze_cx] == 0.5
            and grid[maze_cy + 2, maze_cx] == 0.5
            and grid[maze_cy, maze_cx - 2] == 0.5
            and grid[maze_cy, maze_cx + 2] == 0.5
        ):
            pass
        else:
            maze_li = [1, 2, 3, 4]
            while len(maze_li) > 0:
                direction = random.choice(maze_li)
                maze_li.remove(direction)

                if direction == Directions.DIRECTION_UP.value:
                    maze_ny = maze_cy - 2
                    maze_my = maze_cy - 1
                elif direction == Directions.DIRECTION_DOWN.value:
                    maze_ny = maze_cy + 2
                    maze_my = maze_cy + 1
                else:
                    maze_ny = maze_cy
                    maze_my = maze_cy

                if direction == Directions.DIRECTION_LEFT.value:
                    maze_nx = maze_cx - 2
                    maze_mx = maze_cx - 1
                elif direction == Directions.DIRECTION_RIGHT.value:
                    maze_nx = maze_cx + 2
                    maze_mx = maze_cx + 1
                else:
                    maze_nx = maze_cx
                    maze_mx = maze_cx

                if grid[maze_ny, maze_nx] != 0.5:
                    grid[maze_my, maze_mx] = 0.5
                    self.generator(maze_nx, maze_ny, grid)
