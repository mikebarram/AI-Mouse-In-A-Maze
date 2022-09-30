import numpy as np
import pygame

import config
from mouse import MouseStatus
from mouse_icon import MouseIcon


class MouseDrawer:
    """draws a mouse"""

    """
        *** fixed globals used in the MouseDrawer class ***
        MAZE_SQUARE_SIZE
        GREEN
        WHITE
        BLACK
    """

    def __init__(
        self,
        screen,
        visited_by_mouse_screen,
        maze_wall_distances_screen,
    ):
        self.screen = screen
        self.visited_by_mouse_screen = visited_by_mouse_screen
        self.maze_wall_distances_screen = maze_wall_distances_screen
        self.position_rounded = None

        self.mouse_icon = MouseIcon()
        self.mouse_icon_group = pygame.sprite.Group()
        self.mouse_icon_group.add(self.mouse_icon)

    def draw_mouse_trail(self, position_rounded, speed, speed_max):
        mouse_speed_colour = round(255 * speed / speed_max)
        mouse_colour = (255 - mouse_speed_colour, mouse_speed_colour, 0)
        self.screen.set_at(position_rounded, mouse_colour)

    def draw_mouse(
        self, status, position_rounded, direction_radians, visited_alpha, whiskers
    ):
        self.mouse_icon_group.update(
            position_rounded[0],
            position_rounded[1],
            direction_radians,
        )

        if status is not MouseStatus.CRASHED:
            # if crashed into a corner, all whiskers might be zero length
            # which would give an error of "points argument must contain 2 or more points"
            self.draw_lines_to_maze_edge(whiskers)

        if status is MouseStatus.SUCCESSFUL:
            self.draw_mouse_finish_location(config.GREEN)
        elif status is MouseStatus.TIMEDOUT:
            self.draw_mouse_finish_location(config.RED)
        elif status is MouseStatus.CRASHED:
            self.draw_mouse_finish_location(config.RED)

        # from https://github.com/pygame/pygame/issues/1244
        surface_alpha = np.array(self.visited_by_mouse_screen.get_view("A"), copy=False)
        surface_alpha[:, :] = visited_alpha

    def draw_lines_to_maze_edge(self, whiskers):
        """draw lines from the mouse to the edge of the maze"""
        self.maze_wall_distances_screen.fill((0, 0, 0, 0))
        pygame.draw.lines(
            self.maze_wall_distances_screen, config.WHITE, False, whiskers
        )

    def draw_mouse_finish_location(self, highlight_colour):
        """draw where the mouse finishes"""
        if self.position_rounded is None:
            return
        finish_radius = config.MAZE_SQUARE_SIZE // 2
        pygame.draw.circle(
            self.screen, highlight_colour, self.position_rounded, finish_radius, width=2
        )
        finish_zone = pygame.Rect(
            self.position_rounded[0] - finish_radius,
            self.position_rounded[1] - finish_radius,
            2 * finish_radius,
            2 * finish_radius,
        )
        pygame.display.update(finish_zone)
