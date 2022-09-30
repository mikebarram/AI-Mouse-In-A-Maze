"""
*** HOW TO PROFILE ***
Install gprof2dot and dot
On Windows, to install dot, install Graphviz and make sure the path to the bin folder
that contains dot.exe is in the PATH environment variable (or include the full path to
dot when you call it)

Get the programme to start and end e.g. in main add
if statsInfoGlobal["Total frames"] > 10000:
            break
In the terminal run
python -m cProfile -o output.pstats maze_23_mouse_refactor.py
gprof2dot -f pstats output.pstats | "C:\\Program Files\\Graphviz\\bin\\dot.exe" -Tpng -o output23.png
Have a look at output.png
"""

# A program which uses recursive backtracking to generate a maze
# https://aryanab.medium.com/maze-generation-recursive-backtracking-5981bc5cc766
# https://github.com/AryanAb/MazeGenerator/blob/master/backtracking.py
# A good alternative might be https://github.com/AryanAb/MazeGenerator/blob/master/hunt_and_kill.py

import gzip
import math
import os
import os.path
import pickle
import random

# import the pygame module, so you can use it
import sys

import neat
import pygame

import config
import maze
import mouse
import stats
from maze_drawer import MazeDrawer
from maze_solver import MazeSolver
from mouse_drawer import MouseDrawer

generation = 0
SINGLE_MAZE_FILE = ""
# SINGLE_MAZE_FILE = "mazes\19x13\maze_CRASHED_20220601-215248_path-46.txt"
CHECKPOINT_FILE_TO_LOAD = None
# CHECKPOINT_FILE_TO_LOAD = "neat-checkpoint-86"

sys.setrecursionlimit(8000)


def run_maze(genomes, neat_config):
    global SINGLE_MAZE_FILE
    global generation
    generation += 1

    # initialize the pygame module
    pygame.init()
    # clock = pygame.time.Clock()
    # start_time = time.monotonic()
    # load and set the logo
    logo = pygame.image.load("logo32x32.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("Not AI mouse")

    window_size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

    # create a surface on screen that has the size defined globally
    screen = pygame.display.set_mode(window_size)
    background = pygame.Surface(window_size)

    maze_path_surface = pygame.Surface(window_size)  # , pygame.SRCALPHA, 32)
    maze_path_surface.set_alpha(60)
    maze_path_surface.fill((255, 255, 255))

    visited_by_mouse_screen = pygame.Surface(window_size, pygame.SRCALPHA, 32)
    visited_by_mouse_screen = visited_by_mouse_screen.convert_alpha()
    visited_by_mouse_screen.fill((0, 0, 0, 0))

    maze_wall_distances_screen = pygame.Surface(window_size, pygame.SRCALPHA, 32)
    maze_wall_distances_screen = maze_wall_distances_screen.convert_alpha()

    stats_surface = pygame.Surface(window_size)
    stats_surface = stats_surface.convert_alpha()
    stats_surface.fill((0, 0, 0, 0))

    # define a variable to control the main loop
    running = True
    paused = False
    frame_number = 0
    draw_frame = True
    maze_area = config.MAZE_ROWS * config.MAZE_COLS * config.MAZE_SQUARE_SIZE
    max_distance = 1.3 * round(maze_area / 20 + 200 * math.sqrt(generation))
    initial_direction_radians = random.uniform(-math.pi, math.pi)

    maze1 = maze.Maze(
        config.MAZE_ROWS,
        config.MAZE_COLS,
        config.MAZE_SQUARE_SIZE,
        config.MAZE_DIRECTORY,
    )

    if SINGLE_MAZE_FILE == "":
        maze1.create()
        maze1.save("NEW")
        SINGLE_MAZE_FILE = maze1.file_name
    else:
        maze1.load(SINGLE_MAZE_FILE)

    maze_solver = MazeSolver(maze1.maze_tiny)
    (
        maze_is_solved,
        maze_min_path_distance,
        maze_distance_score,
        maze_path,
    ) = maze_solver.solve_maze()
    maze1.path_distance = maze_min_path_distance

    maze_drawer = MazeDrawer(maze1, window_size, background, maze_path_surface)
    maze_drawer.draw_maze(maze1.maze_tiny, config.PURE_WHITE, config.BLACK)
    maze_drawer.draw_shortest_path(maze_path)
    maze_drawer.draw_start(background, config.MAZE_SQUARE_SIZE, (100, 100, 100))
    maze_drawer.draw_finish(
        window_size, background, config.MAZE_SQUARE_SIZE, (100, 100, 100)
    )

    mouse_drawer = MouseDrawer(
        background,
        visited_by_mouse_screen,
        maze_wall_distances_screen,
    )

    # Init NEAT
    nets = []
    mice = []

    stats_info_global = {
        "max distace": max_distance,
        "generation": generation,
        "frame": 0,
        "mice hunting": 0,
        "mice successful": 0,
        "mice crashed": 0,
        "mice spun out": 0,
        "mice timed out": 0,
        "mice pottering": 0,
    }

    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, neat_config)
        nets.append(net)
        g.fitness = 0

        # Init mice
        mouse_to_add = mouse.Mouse(
            window_size,
            maze1.maze_big,
            maze_min_path_distance,
            maze_distance_score,
            mouse.OPTIMISE_MOUSE_VISITED_PATH_RADIUS,
            mouse.OPTIMISE_MOUSE_SPEED_MIN_INITIAL,
            mouse.OPTIMISE_MOUSE_SPEED_MAX_INITIAL,
            mouse.OPTIMISE_MOUSE_VISION_ANGLES_AND_WEIGHTS,
            mouse.OPTIMISE_MOUSE_STEERING_MULTIPLIER,
            mouse.OPTIMISE_MOUSE_VISITED_PATH_AVOIDANCE_FACTOR,
            mouse.OPTIMISE_MOUSE_FRAMES_BETWEEN_BLURRING_VISITED,
            max_distance,
            initial_direction_radians,
        )
        mice.append(mouse_to_add)

    # main loop
    while running:
        frame_number += 1
        stats_info_global["frame"] = frame_number
        if frame_number % config.FRAME_DISPLAY_RATE == 0:
            draw_frame = True
        else:
            draw_frame = False

        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
                sys.exit()
                break

            # for the next bit, on windows, you need to:
            # pip install windows-curses
            # https://stackoverflow.com/questions/35850362/importerror-no-module-named-curses-when-trying-to-import-blessings
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    sys.exit()
                    break
                elif event.key == pygame.K_SPACE:
                    paused = not paused

        if paused:
            continue

        mice_hunting = 0
        for index, mousei in enumerate(mice):
            mouse_status_previous = mousei.status
            mousei.get_maze_wall_distances()
            output = nets[index].activate(mousei.get_data())

            steering_radians = output[0] * mouse.MOUSE_STEERING_RADIANS_DELTA_MAX
            speed_delta = output[1] * 2.0
            mousei.move(draw_frame, steering_radians, speed_delta)

            # check if the status has changes
            if mousei.status is not mouse_status_previous:
                if mousei.status is not mouse.MouseStatus.HUNTING:
                    genomes[index][1].fitness = mousei.score
                    if mousei.status is mouse.MouseStatus.SUCCESSFUL:
                        stats_info_global["mice successful"] += 1
                    elif mousei.status is mouse.MouseStatus.CRASHED:
                        stats_info_global["mice crashed"] += 1
                    elif mousei.status is mouse.MouseStatus.SPUNOUT:
                        stats_info_global["mice spun out"] += 1
                    elif mousei.status is mouse.MouseStatus.TIMEDOUT:
                        stats_info_global["mice timed out"] += 1
                    elif mousei.status is mouse.MouseStatus.POTTERING:
                        stats_info_global["mice pottering"] += 1
                    continue

            # the trail is drawn to its surface (but not necessarily rendered) on every frame
            mouse_drawer.draw_mouse_trail(
                mousei.position_rounded, mousei.speed, mousei.speed_max
            )
            if mousei.status is mouse.MouseStatus.HUNTING:
                mice_hunting += 1

            """
            if draw_frame:
                mouse_drawer.draw_mouse(
                    mousei.status,
                    mousei.position_rounded,
                    mousei.direction_radians,
                    mousei.visited_alpha,
                    mousei.whiskers,
                )
            """

        stats_info_global["mice hunting"] = mice_hunting

        if draw_frame:
            stats.stats_update(stats_surface, {}, stats_info_global)
            pygame.display.flip()
            screen.blit(background, (0, 0))
            screen.blit(maze_path_surface, (0, 0))
            # screen.blit(mouse_drawer.visited_by_mouse_screen, (0, 0))
            screen.blit(mouse_drawer.maze_wall_distances_screen, (0, 0))
            # mouse_drawer.mouse_icon_group.draw(screen)
            screen.blit(stats_surface, (0, 0))
            pygame.display.update()

        if mice_hunting == 0:
            break
        # clock.tick(400)


def run_neat(config):
    global generation
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-85')
    p = neat.Population(config)
    if CHECKPOINT_FILE_TO_LOAD is not None:
        with gzip.open(CHECKPOINT_FILE_TO_LOAD) as f:
            generation, loaded_config, population, species_set, rndstate = pickle.load(
                f
            )
            random.setstate(rndstate)
            p = neat.Population(config, (population, species_set, generation))

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(generation_interval=1))

    winner = p.run(run_maze, 1000)
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)
    print("done")


# define a main function
def main():
    """main function"""

    local_dir = os.path.dirname(__file__)
    config_file = os.path.join(local_dir, "maze_mouse_neat.config")
    neat_config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file,
    )
    run_neat(neat_config)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__ == "__main__":
    # call the main function
    main()
