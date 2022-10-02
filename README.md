# AI-Mouse-In-A-Maze - uses the NEAT algorithm

To run, execute main_maze_neat.py

To change algorithm settings, edit maze_mouse_neat.config

Finally, after getting a [car to drive around a track without AI](https://github.com/mikebarram/Not-AI-Car), then getting a [mouse to solve a maze 99% of the time without AI](https://github.com/mikebarram/Not-AI-Mouse-In-A-Maze), in this project I use AI to try to get mice to solve a maze.

The code is largely the same as the non-AI version but, when a mouse has to decide what changes to make to speed and direction based on how far away the walls are and it's scent trail, it now uses values provided by the [NEAT algorithm](https://neat-python.readthedocs.io/).

Feedback to the algorithm is provided only when a mouse stops (gets to the end or crashes) or is stopped (takes too long, spins around too much or doesn't move enough (potters)). It gets a very high score for success, otherwise a score for how many different squares it's visited. It did get a score for how far along the path to the end it had gone but, as there's no way to know if any given path is on the way to the end, it's better to reward an adventurous mouse than one that's lucky. See update_score() in mouse.py for details.

On my laptop, which has an AMD Ryzen 7 PRO 3700U processor, each generation takes about 20 seconds with a 21x13 maze, a population size of 300 and the FRAME_DISPLAY_RATE set to 100 (only has to render all of the mice once every 100 steps).

First 3 generations of mice trying to find their way:

https://user-images.githubusercontent.com/13784388/193431284-aa68a77d-72c0-4cf9-830f-baf10dff3d39.mp4

After 107 generations, it looks a lot better but is still not very successful, averaging a roughly 1% success rate:

![ai_mice_gen107](https://user-images.githubusercontent.com/13784388/193431552-e688ddef-d903-42ad-88b9-844d9c4506c7.png)

After 1996 generations, it was more successful through following the right hand wall but it was still rare to get a success rate above 50%:

![ai_mice_gen1996](https://user-images.githubusercontent.com/13784388/193475783-53c303d9-fa1d-48cc-9765-ac4d2ff69000.png)

## Problems to solve
- It's nothing like as good as non-AI version
- It doesn't seem to learn how to get away from the start. Even after many generations, lots of mice crash into the walls at the start.
- The algorithm only receives feedback at the end of each generation and so a mouse can make 2,000 moves (instructions from the algorithm) before anything is fed back to the algorithm to influence the next generation.
- The NEAT algorithm has a lot of parameters and, while it's easy enough to understand what they mean, it's very hard to understand the impacts of changing them.

Maybe a multi-stage algorithm would work better - for each step, first the mouse would decide what category of situation it is in, then it would use a NEAT algorithm for that category. Maybe it could recognise and categorise straights, corners, junctions and dead ends, perhaps with variations based on the scent trail...

The maze generation algorithm used creates a simply connected maze (just one route from start to finish and no loops). This makes wall following the best strategy (I believe) in this situation and so getting a mouse to follow a wall isn't really any harder than getting a car to follow a track, as there are no route finding decisions to make. It also means that there is no need to make use of the "scent trail". It would be interesting to try this with a different maze algorithm, which creates loops, and then the route finding algorithm may need to make use of the scent trail.
