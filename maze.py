import time

import numpy as np

from backtracking import Backtracking


class Maze:
    """create and manage mazes
    Wiht the Backtracking algorithm, the start point for creating the maze
    is chosen randomly but every part of the generated maze can be visited
    from any other and the corners are always free,
    so the top left is the start and the bottom right is the end"""

    def __init__(self, rows, cols, square_size, maze_directory) -> None:
        self.rows = rows
        self.cols = cols
        self.square_size = square_size
        self.maze_directory = maze_directory
        self.maze_title = None
        self.maze_tiny = []
        self.maze_big = []
        self.from_saved = None
        self.file_name = None
        self.path_distance = None

    def create(self):
        """create a new maze"""
        self.maze_title = "New maze"
        self.from_saved = False
        self.maze_tiny = self.get_new_maze(self.rows, self.cols)
        self.maze_big = self.get_big_bool_maze(self.maze_tiny, self.square_size)

    def save(self, save_reason):
        """save a maze. It will save to a folder based on the height and width of the
        maze. The file name will include the reason the file was saved, the date/time
        and the length of the path"""
        filename = "maze.txt"
        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = self.maze_directory + "maze_" + save_reason + "_" + timestr
        if self.path_distance is not None:
            filename += "_path-" + str(self.path_distance)
        filename += ".txt"
        np.savetxt(filename, self.maze_tiny, fmt="%s")
        self.file_name = filename

    def load(self, filename):
        """load a previously saved maze"""
        self.maze_title = "Maze: " + filename
        self.from_saved = True
        self.file_name = filename
        self.maze_tiny = np.loadtxt(filename, dtype=int)
        self.maze_big = self.get_big_bool_maze(self.maze_tiny, self.square_size)

    @staticmethod
    def get_new_maze(rows, cols):
        """get a new maze"""
        backtracking = Backtracking(height=rows + 1, width=cols + 1)
        maze = backtracking.create_maze()
        # remove the outer elements of the array
        maze = np.delete(maze, [0, maze.shape[0] - 1], axis=0)
        maze = np.delete(maze, [0, maze.shape[1] - 1], axis=1)

        return maze

    @staticmethod
    def get_big_bool_maze(tiny_maze, scale_factor):
        """stretch maze"""
        maze_bool = tiny_maze.astype(dtype=bool)
        # from https://stackoverflow.com/a/4227280
        return np.repeat(
            np.repeat(maze_bool, scale_factor, axis=0), scale_factor, axis=1
        )
