import math
from enum import Enum, auto

import numpy as np
import pygame
from numba import jit

import config

# Mice can only look so far ahead. Needs to be larger than grid size for the maze
MOUSE_VISION_DISTANCE = round(2.0 * config.MAZE_SQUARE_SIZE)
MOUSE_ACCELERATION_MIN = -3  # change in speed in pixels per frame
MOUSE_ACCELERATION_MAX = 2  # change in speed in pixels per frame
MOUSE_STEERING_RADIANS_MAX = math.radians(45)
MOUSE_STEERING_RADIANS_DELTA_MAX = math.radians(45)
MOUSE_TRAIL_CIRCLE_ALPHA = None
MOUSE_MAX_SPIN_RADIANS = 30

# The following globals are to be set individually for each mouse
# to try to optimise their values
OPTIMISE_MOUSE_VISITED_PATH_RADIUS = 20
OPTIMISE_MOUSE_SPEED_MIN_INITIAL = 2  # pixels per frame
OPTIMISE_MOUSE_SPEED_MAX_INITIAL = 5  # pixels per frame
OPTIMISE_MOUSE_WEIGHTS_15 = 1.0 / 5.0
OPTIMISE_MOUSE_WEIGHTS_30 = 1.0 / 6.0
OPTIMISE_MOUSE_WEIGHTS_45 = 1.0 / 6.0
OPTIMISE_MOUSE_WEIGHTS_60 = 1.0 / 7.0
OPTIMISE_MOUSE_WEIGHTS_90 = 1.0 / 7.0
OPTIMISE_MOUSE_VISION_ANGLES_AND_WEIGHTS = (
    (math.radians(0.0), 1.0 / 2.0),
    (math.radians(-15.0), -OPTIMISE_MOUSE_WEIGHTS_15),
    (math.radians(15.0), OPTIMISE_MOUSE_WEIGHTS_15),
    (math.radians(-30.0), -OPTIMISE_MOUSE_WEIGHTS_30),
    (math.radians(30.0), OPTIMISE_MOUSE_WEIGHTS_30),
    (math.radians(-45.0), -OPTIMISE_MOUSE_WEIGHTS_45),
    (math.radians(45.0), OPTIMISE_MOUSE_WEIGHTS_45),
    (math.radians(-60.0), -OPTIMISE_MOUSE_WEIGHTS_60),
    (math.radians(60.0), OPTIMISE_MOUSE_WEIGHTS_60),
    (math.radians(-90.0), -OPTIMISE_MOUSE_WEIGHTS_90),
    (math.radians(90.0), OPTIMISE_MOUSE_WEIGHTS_90),
)  # 0 must be first, 90 degrees needed to get out of dead ends
OPTIMISE_MOUSE_STEERING_MULTIPLIER = 2.5
OPTIMISE_MOUSE_VISITED_PATH_AVOIDANCE_FACTOR = (
    1.25 * config.MAZE_SQUARE_SIZE / (2 * OPTIMISE_MOUSE_VISITED_PATH_RADIUS)
)
# the bigger the maze, the longer it could be before returning to a visited bit of maze
OPTIMISE_MOUSE_FRAMES_BETWEEN_BLURRING_VISITED = (
    config.MAZE_ROWS * config.MAZE_COLS
) // 10


class MouseStatus(Enum):
    """statuses that a mouse can have when hunting to find the end of a maze"""

    HUNTING = auto()
    SUCCESSFUL = auto()
    CRASHED = auto()
    TIMEDOUT = auto()
    SPUNOUT = auto()


class Mouse:
    """a mouse"""

    def __init__(
        self,
        window_size,
        maze_big,
        maze_min_path_distance,
        maze_distance_score,
        visited_path_radius,
        speed_min_initial,
        speed_max_initial,
        vision_angles_and_weights,
        steering_multiplier,
        visited_path_avoidance_factor,
        frames_between_blurring_visited,
        max_distance,
    ):
        self.window_size = window_size
        self.maze_big = (
            maze_big  # when accessing an element of maze_big, it's maze_big[y][x]
        )
        self.maze_min_path_distance = maze_min_path_distance
        self.maze_distance_score = maze_distance_score
        self.visited_path_radius = visited_path_radius
        self.speed_min_initial = speed_min_initial
        self.speed_max_initial = speed_max_initial
        self.vision_angles_and_weights = vision_angles_and_weights
        self.steering_multiplier = steering_multiplier
        self.visited_path_avoidance_factor = visited_path_avoidance_factor
        self.frames_between_blurring_visited = frames_between_blurring_visited
        self.max_distance = max_distance

        """
        *** fixed globals used in the Mouse class ***
        config.MAZE_SQUARE_SIZE
        MAZE_COLS
        MAZE_ROWS
        MOUSE_STEERING_RADIANS_DELTA_MAX
        MOUSE_STEERING_RADIANS_MAX
        MOUSE_VISION_DISTANCE
        MOUSE_ACCELERATION_MIN
        MOUSE_ACCELERATION_MAX

        *** globals used in the Mouse class that will become variables, set for each instance by 'AI' ***
        OPTIMISE_MOUSE_VISITED_PATH_RADIUS
        OPTIMISE_MOUSE_SPEED_MIN_INITIAL
        OPTIMISE_MOUSE_SPEED_MAX_INITIAL
        OPTIMISE_MOUSE_WEIGHTS_15
        OPTIMISE_MOUSE_WEIGHTS_30
        OPTIMISE_MOUSE_WEIGHTS_45
        OPTIMISE_MOUSE_WEIGHTS_60
        OPTIMISE_MOUSE_WEIGHTS_90
        OPTIMISE_MOUSE_VISION_ANGLES_AND_WEIGHTS
        OPTIMISE_MOUSE_STEERING_MULTIPLIER
        OPTIMISE_MOUSE_VISITED_PATH_AVOIDANCE_FACTOR
        OPTIMISE_MOUSE_FRAMES_BETWEEN_BLURRING_VISITED

        """

        # actual position is recorded as a tuple of floats
        # position is rounded just for display
        # and to see if the mouse is still on the maze
        # starting position is in the middle of top left square inside the border
        self.frames = 0
        self.distance_travelled = 0
        self.position = (config.MAZE_SQUARE_SIZE * 1.5, config.MAZE_SQUARE_SIZE * 1.5)
        self.position_rounded = (round(self.position[0]), round(self.position[1]))
        self.speed = config.MAZE_SQUARE_SIZE / 50  # pixels per frame
        self.speed_min = speed_min_initial
        self.speed_max = speed_max_initial
        self.status = MouseStatus.HUNTING
        # could try to set initial direction based on the shape of the
        # maze that's generated but this is fine
        self.direction_radians = math.pi / 6
        self.steering_radians = 0
        self.position_previous_rounded = self.position_rounded
        self.visited_alpha = np.zeros(window_size, dtype=np.int16)
        self.maze_wall_distances = None
        self.whiskers = None

        self.trail_circle_alpha = self.create_trail_circle_alpha(
            self.visited_path_radius, 10
        )

        """
        self.stats_info_mouse = {
            "distance": 0.0,
            "frames": 0,
            "average speed": 0.0,
            "speed min": self.speed_min,
            "speed max": self.speed_max,
            "maze progress": 0,
        }
        """

        self.score = 0
        self.max_happy_path_reached = 0

        """
        self.instructions = {
            "speed": 0.0,
            "speed_delta": 0.0,
            "direction_radians": 0.0,
            "steering_radians": 0.0,
        }
        # keep a list of the 20 last instructions, so we can see where it went wrong
        self.latest_instructions = deque(maxlen=20)
        """

    @staticmethod
    def create_trail_circle_alpha(circle_radius, trail_alpha):
        """create a 2D array of integers that have a given value if they are in a circle,
        otherwise they are zero, except for those around the edge of the circle"""
        x_list = np.arange(-circle_radius, circle_radius)
        y_list = np.arange(-circle_radius, circle_radius)
        array_alpha = np.zeros((y_list.size, x_list.size), dtype=np.int16)

        # the circle will mostly have opacity trail_alpha
        # but be 1/3 and 2/3 that around the outside
        mask_outer = (x_list[np.newaxis, :]) ** 2 + (
            y_list[:, np.newaxis]
        ) ** 2 < circle_radius**2
        mask_middle = (x_list[np.newaxis, :]) ** 2 + (y_list[:, np.newaxis]) ** 2 < (
            circle_radius - 4
        ) ** 2
        mask_inner = (x_list[np.newaxis, :]) ** 2 + (y_list[:, np.newaxis]) ** 2 < (
            circle_radius - 8
        ) ** 2

        array_alpha[mask_outer] = trail_alpha // 3
        array_alpha[mask_middle] = (2 * trail_alpha) // 3
        array_alpha[mask_inner] = trail_alpha

        return array_alpha

    def get_data(self):
        data = []
        for angles in self.maze_wall_distances:
            for x in angles[1:4]:
                data.append(x)
        return data

    def speed_increase(self):
        """increase speed by 1 pixel per frame"""
        self.speed_min += 1
        self.speed_max += 1

    def speed_decrease(self):
        """decrease speed by 1 pixel per frame to a minimum of 1"""
        self.speed_min = min(1, self.speed_min - 1)
        self.speed_max = min(1, self.speed_max - 1)

    def update_happy_path_progress(self):
        # get the position of the mouse on a scale where each sqaure of the maze is 1 pixel (as in maze_path and maze_tiny)
        position_tiny_x = round(self.position[0] / config.MAZE_SQUARE_SIZE)
        position_tiny_y = round(self.position[1] / config.MAZE_SQUARE_SIZE)
        # get the value of maze_path at that position
        progress_for_position = self.maze_distance_score[position_tiny_y][
            position_tiny_x
        ]
        # update max_happy_path_reached if further progress has been reached than ever before
        if progress_for_position > self.max_happy_path_reached:
            self.max_happy_path_reached = round(progress_for_position)

    def update_score(self):
        """
        the  mouse's score is updated when it stops hunting - it's successful, crashes or times out.
        """
        if self.status is MouseStatus.SUCCESSFUL:
            # nice high score. Multiply by min-path distance. Divide by number of steps (frames) taken.
            self.score = (
                1000
                * self.maze_min_path_distance
                * config.MAZE_SQUARE_SIZE
                / self.frames
            )
        elif self.status is MouseStatus.SPUNOUT:
            self.score = -1
        elif self.status is not MouseStatus.HUNTING:
            # score based on how far the mouse got through the maze along the path to the end
            # mouse could have reached much further along the path to the end than where it crashed, so need to calculate how far it got with each step.
            # penalise for having rotated lots of times
            self.score = 100 * self.max_happy_path_reached / self.maze_min_path_distance

    def get_driving_changes_with_ai():
        new_steering_radians = 0
        speed_delta = 0
        return new_steering_radians, speed_delta

    def get_driving_changes_with_real_intelligence(self):
        steering_radians_previous = self.steering_radians
        new_steering_radians = 0
        speed_delta = 0
        is_dead_end = self.check_if_dead_end(self.maze_wall_distances)

        if is_dead_end:
            new_steering_radians = self.get_steering_radians_for_dead_end(
                self.maze_wall_distances
            )
        else:
            new_steering_radians = self.get_steering_radians(
                self.maze_wall_distances,
                self.steering_multiplier,
                self.visited_path_avoidance_factor,
            )

        # restrict how much the steering can be changed per frame
        new_steering_radians = self.restrict_steering_changes(
            new_steering_radians, steering_radians_previous
        )

        # restrict how much the steering can be per frame
        new_steering_radians = self.restrict_steering(new_steering_radians)

        # check how far away the wall is when going in the new direction
        # and alter the speed based on the distance
        (maze_wall_distance, _, _, _, _,) = self.get_maze_wall_distance(
            self.maze_big,
            self.visited_alpha,
            self.direction_radians,
            self.position_rounded[0],
            self.position_rounded[1],
            new_steering_radians,
        )

        speed_delta = 4 * (maze_wall_distance / MOUSE_VISION_DISTANCE) - 2

        return new_steering_radians, speed_delta

    def get_changes(self, use_ai):
        """to be called every frame to move the mouse along"""

        new_steering_radians = 0
        speed_delta = 0

        if use_ai:
            new_steering_radians, speed_delta = self.get_driving_changes_with_ai()
        else:
            (
                new_steering_radians,
                speed_delta,
            ) = self.get_driving_changes_with_real_intelligence()
        return new_steering_radians, speed_delta

    def move(self, draw_frame, new_steering_radians, speed_delta):
        if self.status is not MouseStatus.HUNTING:
            return

        self.frames += 1

        new_direction_radians = self.direction_radians + new_steering_radians

        if speed_delta < MOUSE_ACCELERATION_MIN:
            speed_delta = MOUSE_ACCELERATION_MIN

        if speed_delta > MOUSE_ACCELERATION_MAX:
            speed_delta = MOUSE_ACCELERATION_MAX

        new_speed = self.speed + speed_delta

        if new_speed < self.speed_min:
            new_speed = self.speed_min

        if new_speed > self.speed_max:
            new_speed = self.speed_max

        new_position = (
            self.position[0] + new_speed * math.cos(new_direction_radians),
            self.position[1] + new_speed * math.sin(new_direction_radians),
        )

        self.speed = new_speed
        self.distance_travelled += new_speed
        self.steering_radians = new_steering_radians
        self.direction_radians = new_direction_radians

        self.position = new_position
        self.position_rounded = (round(self.position[0]), round(self.position[1]))
        self.position_previous_rounded = self.position_rounded

        if draw_frame:
            pygame.display.update(
                pygame.Rect(self.position_rounded[0], self.position_rounded[1], 1, 1)
            )
            pygame.display.update()

        self.update_visited(
            self.position,
            self.direction_radians,
            self.visited_alpha,
            self.trail_circle_alpha,
            self.visited_path_radius,
        )

        # self.stats_info_mouse["frames"] += 1
        # self.stats_info_mouse["distance"] += new_speed
        # self.stats_info_mouse["average speed"] = (
        #     self.stats_info_mouse["distance"] // self.stats_info_mouse["frames"]
        # )
        # self.stats_info_mouse["speed min"] = self.speed_min
        # self.stats_info_mouse["speed max"] = self.speed_max
        # self.stats_info_mouse["maze progress"] = self.max_happy_path_reached

        """
        self.instructions = {
            "speed": self.speed,
            "speed_delta": speed_delta,
            "direction_radians": self.direction_radians,
            "steering_radians": self.steering_radians,
            "maze_wall_distances": maze_wall_distances,
        }
        self.latest_instructions.appendleft(self.instructions)
        """

        if self.frames % self.frames_between_blurring_visited == 0:
            self.fade_visited(self.visited_alpha)

        # decided that the mouse has "crashed" if it has taken more than this
        # distance to complete the maze - better to create a "crashed" status
        if self.distance_travelled > self.max_distance:
            self.status = MouseStatus.TIMEDOUT
            self.update_score()
            return

        if self.status is MouseStatus.HUNTING:
            self.update_happy_path_progress()

        if self.check_if_position_wins(self.position[0], self.position[1]):
            self.status = MouseStatus.SUCCESSFUL
            self.update_score()
            return

        if self.check_if_spun_out(self.direction_radians):
            self.status = MouseStatus.SPUNOUT
            self.update_score()
            return

    @staticmethod
    def get_steering_radians_for_dead_end(maze_wall_distances):
        # old code from maze v3 that doesn't take into account
        # whether pixels have been visited
        new_steering_angle = 0
        max_maze_distance = 1
        for ted in maze_wall_distances:
            if ted[0][0] == 0:
                continue

            new_steering_angle += ted[1] * ted[0][1]
            if ted[1] > max_maze_distance:
                max_maze_distance = ted[1]

        return 5 * new_steering_angle / max_maze_distance

    @staticmethod
    def get_steering_radians(
        maze_wall_distances, steering_multiplier, visited_path_avoidance_factor
    ):
        new_steering_angle = 0
        max_maze_distance = 1
        min_maze_distance = 1000
        for ted in maze_wall_distances:
            if ted[0][0] == 0:
                continue

            # this takes into account the sum of the alpha channel of the pixels
            # that have been visited, rather than just the number of visited pixels
            distance_for_angle = max(
                0,
                ted[1]
                * (1 - (ted[3] * visited_path_avoidance_factor) / (255 * ted[1])),
            )

            new_steering_angle += distance_for_angle * ted[0][1]
            if distance_for_angle > max_maze_distance:
                max_maze_distance = distance_for_angle
            if distance_for_angle < min_maze_distance:
                min_maze_distance = distance_for_angle

        return new_steering_angle * steering_multiplier / max_maze_distance

    @staticmethod
    def restrict_steering_changes(new_steering_radians, steering_radians_previous):
        # restrict how much the steering can be changed per frame
        if (
            new_steering_radians
            < steering_radians_previous - MOUSE_STEERING_RADIANS_DELTA_MAX
        ):
            new_steering_radians = (
                steering_radians_previous - MOUSE_STEERING_RADIANS_DELTA_MAX
            )
        elif (
            new_steering_radians
            > steering_radians_previous + MOUSE_STEERING_RADIANS_DELTA_MAX
        ):
            new_steering_radians = (
                steering_radians_previous + MOUSE_STEERING_RADIANS_DELTA_MAX
            )
        return new_steering_radians

    @staticmethod
    def restrict_steering(new_steering_radians):
        # restrict how much the steering can be per frame
        if new_steering_radians > MOUSE_STEERING_RADIANS_MAX:
            new_steering_radians = MOUSE_STEERING_RADIANS_MAX
        elif new_steering_radians < -MOUSE_STEERING_RADIANS_MAX:
            new_steering_radians = -MOUSE_STEERING_RADIANS_MAX
        return new_steering_radians

    @staticmethod
    @jit(nopython=True)
    def update_visited(
        position,
        direction_radians,
        visited_alpha,
        trail_circle_alpha,
        visited_path_radius,
    ):
        """Updates a mouses 2D array to record that the mouse has been
        in a particular area"""
        # update a 2d numpy array that represents visited pixels.
        # it should add a circular array behind itself.
        # needs to know the angle of travel
        # needs to add but only to a level of saturation (max 255)
        circle_top_left_x = round(
            position[0]
            - visited_path_radius * math.cos(direction_radians)
            - visited_path_radius
        )
        circle_top_left_y = round(
            position[1]
            - visited_path_radius * math.sin(direction_radians)
            - visited_path_radius
        )
        # https://stackoverflow.com/questions/9886303/adding-different-sized-shaped-displaced-numpy-matrices
        section_to_update = visited_alpha[
            circle_top_left_x : circle_top_left_x + 2 * visited_path_radius,
            circle_top_left_y : circle_top_left_y + 2 * visited_path_radius,
        ]
        section_to_update += trail_circle_alpha  # use array slicing
        # section_to_update[section_to_update > 255] = 255 -- this doesn't work. No idea why
        np.clip(section_to_update, 0, 255, out=section_to_update)

    @staticmethod
    # @jit(nopython=True)
    def fade_visited(visited_alpha):
        """fades the mouses 2D array of records of where it has been - like
        a scent fading away"""
        # subtract from the alpha channel but stop it going below zero
        visited_alpha[visited_alpha >= 1] -= 1
        return

    @staticmethod
    # @jit(nopython=True)
    def check_if_spun_out(direction_radians):
        """check if the mouse has reached the end of the maze"""
        if abs(direction_radians > MOUSE_MAX_SPIN_RADIANS):
            return True
        else:
            return False

    @staticmethod
    # @jit(nopython=True)
    def check_if_position_wins(position_x, position_y):
        """check if the mouse has reached the end of the maze"""
        if (
            -2 < position_x / config.MAZE_SQUARE_SIZE - config.MAZE_COLS < -1
            and -2 < position_y / config.MAZE_SQUARE_SIZE - config.MAZE_ROWS < -1
        ):
            return True
        else:
            return False

    @staticmethod
    # @jit(nopython=True)
    def check_if_dead_end(maze_wall_distances):
        """check if the mouse is in a dead end"""
        # if any of the distances is more than the size of a square,
        # then it's not a dead end
        for ted in maze_wall_distances:
            if (
                math.pi / -2.0 <= ted[0][0] <= math.pi / 2.0
                and ted[1] > config.MAZE_SQUARE_SIZE
            ):
                return False

        return True

    def get_maze_wall_distances(self):
        """get the distance of the mouse from the edges of the maze along
        a defined list of angles from its direction of travel"""
        mouse_in_maze_passage = self.maze_big[self.position_rounded[1]][
            self.position_rounded[0]
        ]
        if not mouse_in_maze_passage:
            self.status = MouseStatus.CRASHED
            self.update_score()
            return [], []

        maze_wall_distances = []
        whiskers = []

        for vision_angle_and_weight in self.vision_angles_and_weights:
            (
                maze_wall_distance,
                visited_count,
                visited_alpha_total,
                edge_x,
                edge_y,
            ) = self.get_maze_wall_distance(
                self.maze_big,
                self.visited_alpha,
                self.direction_radians,
                self.position_rounded[0],
                self.position_rounded[1],
                vision_angle_and_weight[0],
            )
            whiskers += [self.position_rounded, (edge_x, edge_y)]

            maze_wall_distances.append(
                (
                    vision_angle_and_weight,
                    maze_wall_distance,
                    visited_count,
                    visited_alpha_total,
                )
            )

        self.maze_wall_distances = maze_wall_distances
        self.whiskers = whiskers

        return

    @staticmethod
    @jit(nopython=True)
    def get_maze_wall_distance(
        maze_big,
        visited_alpha,
        direction_radians,
        position_rounded_x,
        position_rounded_y,
        vision_angle,
    ):
        """get the distance of the mouse from the edges of the maze along a
        single angle from its direction of travel"""
        # from x,y follow a line at vision_angle until no longer on the maze passage
        # or until MOUSE_VISION_DISTANCE has been reached
        search_angle_radians = direction_radians + vision_angle
        delta_x = math.cos(search_angle_radians)
        delta_y = math.sin(search_angle_radians)

        edge_distance = np.int64(0)
        visited_count = np.int64(0)
        visited_alpha_total = np.int64(0)

        for i in range(1, MOUSE_VISION_DISTANCE):
            edge_distance = i
            # incrementing test_x e.g. test_x += delta_x
            # makes the function slower by ~10%
            test_x = position_rounded_x + i * delta_x
            test_y = position_rounded_y + i * delta_y
            # saving the rounded values, rather than rounding twice
            # improves performance of this function by ~5% and by ~3% overall
            test_x_round = round(test_x)
            test_y_round = round(test_y)
            if maze_big[test_y_round][test_x_round] is False:
                break

            visited_alpha_pixel = visited_alpha[test_x_round, test_y_round]
            visited_alpha_total += visited_alpha_pixel
            if visited_alpha_pixel > 0:
                visited_count += 1

        return (
            edge_distance,
            visited_count,
            visited_alpha_total,
            test_x_round,
            test_y_round,
        )
