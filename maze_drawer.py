import pygame


class MazeDrawer:
    """draw the maze with pygame and add graphical elements like the start and finish"""

    def __init__(self, maze, window_size, maze_surface, maze_path_surface) -> None:
        self.maze = maze
        self.window_size = window_size
        self.maze_surface = maze_surface
        self.maze_path_surface = maze_path_surface

    def draw_start(self, maze_surface, square_size, start_colour):
        rect_start = pygame.Rect(square_size, square_size, square_size, square_size)
        pygame.draw.rect(maze_surface, start_colour, rect_start)

    def draw_finish(self, window_size, maze_surface, square_size, finish_colour):
        # might be better to define the finish in terms of the maze size,
        # rather than window size, in case the maze doesn't fill the window
        rect_finish = pygame.Rect(
            window_size[0] - 2 * square_size,
            window_size[1] - 2 * square_size,
            square_size,
            square_size,
        )
        pygame.draw.rect(maze_surface, finish_colour, rect_finish)

    def draw_maze(self, maze_tiny, wall_colour, passage_colour):
        """create a tiny maze with just one pixel per segment of the maze, then scale it up"""
        surf = pygame.Surface((self.maze.cols, self.maze.rows))
        surf.fill(wall_colour)  # BLACK
        for i in range(0, maze_tiny.shape[1]):
            for j in range(0, maze_tiny.shape[0]):
                if maze_tiny[j][i] == 0:
                    surf.set_at((i, j), passage_colour)

        pygame.transform.scale(surf, self.window_size, self.maze_surface)

    def draw_shortest_path(self, maze_path):
        surf = pygame.Surface((self.maze.cols, self.maze.rows))
        for i in range(0, maze_path.shape[1]):
            for j in range(0, maze_path.shape[0]):
                path_colour_r = maze_path[j][i]
                if path_colour_r > 0:
                    path_colour = (path_colour_r, 0, 0)
                    surf.set_at((i, j), path_colour)
        pygame.transform.scale(surf, self.window_size, self.maze_path_surface)
