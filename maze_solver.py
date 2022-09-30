import numpy as np


class MazeSolver:
    """solve the maze
    based on https://www.101computing.net/backtracking-maze-path-finder/
    """

    def __init__(self, maze_tiny) -> None:
        self.maze_tiny = maze_tiny

    def solve_maze(self):
        """
        maze_tiny has walls=0 and paths=1. change this to:
        walls = -1
        paths = 0
        end = -2
        shortest path will then count up from 1
        """
        maze = self.maze_tiny
        rows = len(maze)
        cols = len(maze[0])
        maze = maze - 1
        maze[rows - 2][cols - 2] = -2
        solved = self.explore_maze(maze, 1, 1, 1)

        min_path_distance = 0
        maze_path = None
        if solved:
            min_path_distance = int(np.max(maze))
            # change negative values to 0
            maze[maze < 0] = 0
            # scale the array values 100 to 255
            maze_path = np.trunc(maze * 155 / min_path_distance)
            maze_path[maze_path > 0] += 100

        return solved, min_path_distance, maze, maze_path

    # A backtracking/recursive function to check all possible paths until the exit is
    def explore_maze(self, maze, row, col, distance):
        if maze[row][col] == -2:
            # We found the exit
            return True
        elif maze[row][col] == 0:  # Empty path, not explored
            maze[row][col] = distance
            if row < len(maze) - 1:
                # Explore path below
                if self.explore_maze(maze, row + 1, col, distance + 1):
                    return True
            if row > 0:
                # Explore path above
                if self.explore_maze(maze, row - 1, col, distance + 1):
                    return True
            if col < len(maze[row]) - 1:
                # Explore path to the right
                if self.explore_maze(maze, row, col + 1, distance + 1):
                    return True
            if col > 0:
                # Explore path to the left
                if self.explore_maze(maze, row, col - 1, distance + 1):
                    return True
            # Backtrack
            maze[row][col] = -3
