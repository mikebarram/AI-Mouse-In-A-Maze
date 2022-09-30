import json
import os
import os.path
import time

import pygame

import config
from mouse import MouseStatus


def stats_info_global_update(stats_info_global, start_time, mouse):
    elapsed_time = time.monotonic() - start_time
    stats_info_global["FPS"] = stats_info_global["Total frames"] // elapsed_time
    stats_info_global["Total mazes"] += 1
    if mouse.status is MouseStatus.SUCCESSFUL:
        stats_info_global["Success count"] += 1
        stats_info_global["Total successes"] += 1
        stats_info_global["Max successes in a row"] = max(
            stats_info_global["Max successes in a row"],
            stats_info_global["Success count"],
        )
    elif mouse.status is MouseStatus.CRASHED or mouse.status is MouseStatus.TIMEDOUT:
        stats_info_global["Max successes in a row"] = max(
            stats_info_global["Max successes in a row"],
            stats_info_global["Success count"],
        )
        stats_info_global["Success count"] = 0
    if mouse.status is MouseStatus.CRASHED:
        stats_info_global["Total crashed"] += 1
    if mouse.status is MouseStatus.TIMEDOUT:
        stats_info_global["Total timed out"] += 1
    stats_info_global["Success ratio"] = (
        stats_info_global["Total successes"] / stats_info_global["Total mazes"]
    )
    stats_info_global["Average frames per maze"] = (
        stats_info_global["Total frames"] / stats_info_global["Total mazes"]
    )


def stats_update(stats_surface, stats_info_mouse, stats_info_global):
    """updates the stats surface with global and local stats"""
    stats_surface.fill((0, 0, 0, 0))
    font = pygame.font.SysFont("Arial", 12, bold=False)
    text_top = 0

    for stats in (stats_info_mouse, stats_info_global):
        for stats_key, stats_value in stats.items():
            if stats_value > 10:
                stats_value = round(stats_value)
            img = font.render(
                stats_key + ": " + str(stats_value),
                True,
                pygame.Color(config.BLACK),
                pygame.Color(config.WHITE),
            )
            img_size = img.get_size()
            text_top += img_size[1] + 10
            stats_surface.blit(img, (10, text_top))


class MazeStats:
    def __init__(self):
        self.maze_stats = []

    def add_maze(self, maze, mouse):
        self.maze_stats.append(
            {
                "frames": mouse.stats_info_mouse["frames"],
                "distance": mouse.stats_info_mouse["distance"],
                "maze_min_path_distance": mouse.maze_min_path_distance,
                "max_happy_path_reached": mouse.max_happy_path_reached,
                "status": mouse.status.name,
                "score": mouse.score,
                "filename": maze.file_name,
            }
        )

    def save_to_file(self, stats_info_global):
        if not os.path.exists(config.MAZE_STATS_DIRECTORY):
            os.makedirs(config.MAZE_STATS_DIRECTORY)
        with open(config.MAZE_STATS_DIRECTORY + "maze_stats.json", "w") as fout:
            fout.write("{\n")
            fout.write('"global":')
            json.dump(stats_info_global, fout, indent=0)
            fout.write(",\n")
            fout.write('"mazes":[\n')
            for id, statsDict in enumerate(self.maze_stats):
                if id != 0:
                    fout.write(",\n")
                json.dump(statsDict, fout)
            fout.write("\n]\n}")
