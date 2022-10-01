MAZES_TO_ATTEMPT = 10000
FRAME_DISPLAY_RATE = 100
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
PURE_WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
MAZE_SQUARE_SIZE = 70
MAZE_ROWS = 13
MAZE_COLS = 21

# ROWS AND COLS must be odd for a maze
if MAZE_ROWS % 2 == 0:
    MAZE_ROWS += 1
if MAZE_COLS % 2 == 0:
    MAZE_COLS += 1

# mouse will "crash" if it takes more than this distance to complete the maze
MAZE_MAX_DISTANCE_TO_COMPLETE = MAZE_ROWS * MAZE_COLS * MAZE_SQUARE_SIZE**1.5
MAZE_MAX_DISTANCE_TO_COMPLETE = MAZE_ROWS * MAZE_COLS * MAZE_SQUARE_SIZE // 35
# mazes that the mouse fails to solve are saved here.
# Any mazes in here are reloaded at the start of session.
MAZE_DIRECTORY = f"mazes\\{MAZE_COLS}x{MAZE_ROWS}\\"
MAZE_STATS_DIRECTORY = f"maze_stats\\{MAZE_COLS}x{MAZE_ROWS}\\"

WINDOW_WIDTH = MAZE_COLS * MAZE_SQUARE_SIZE
WINDOW_HEIGHT = MAZE_ROWS * MAZE_SQUARE_SIZE
