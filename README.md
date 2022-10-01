# AI-Mouse-In-A-Maze - uses the NEAT algorithm

To run, execute main_maze_neat.py

To change algorithm settings, edit maze_mouse_neat.config

Finally, after getting a [car to drive around a track without AI](https://github.com/mikebarram/Not-AI-Car), then getting a [mouse to solve a maze 99% of the time without AI](https://github.com/mikebarram/Not-AI-Mouse-In-A-Maze), in this project I use AI to try to get mice to solve a maze.

The code is largely the same as the non-AI version but, when a mouse has to decide what changes to make to speed and direction based on how far away the walls are and it's scent trail, it now uses values provided by the [NEAT algorithm](https://neat-python.readthedocs.io/).

Feedback to the algorithm is provided only when a mouse stops (gets to the end or crashes) or is stopped (takes too long, spins around too much or doesn't move enough (potters)). It gets a very high score for success, otherwise a score for how many different squares it's visited. It did get a score for how far along the path to the end it had gone but, as there's no way to know if any given path is on the way to the end, it's better to reward an adventurous mouse than one that's lucky. See update_score() in mouse.py for details.

On my laptop, which has an AMD Ryzen 7 PRO 3700U processor, each generation takes about 30 seconds with a 21x13 maze and a population size of 300.

First 3 generations of mice trying to find their way:

https://user-images.githubusercontent.com/13784388/193431284-aa68a77d-72c0-4cf9-830f-baf10dff3d39.mp4

After 107 generations, it looks a lot better but is still not very successful, averaging a roughly 1% success rate:

![ai_mice_gen107](https://user-images.githubusercontent.com/13784388/193431552-e688ddef-d903-42ad-88b9-844d9c4506c7.png)

## Problems to solve
- It's nothing like as good as non-AI version
- It doesn't seem to learn how to get away from the start. Even after many generations, lots of mice crash into the walls at the start.
- The algorithm only receives feedback at the end of each generation.

Maybe a multi-stage algorithm would work better - for each step, first the mouse would decide what category of situation it is in, then it would use a NEAT algorithm for that category. Maybe it could recognise and categorise straights, corners, junctions and dead ends, perhaps with variations based on the scent trail...
