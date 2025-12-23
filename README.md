Class Project: Battleship Opponent
=========================================================

HOW TO RUN THE PROGRAM
----------------------
1. Open your terminal or command prompt.
2. Navigate to the folder containing 'battleship_project.py'.
3. Run the file by clicking the run button, or run it by typing the following command and pressing enter:
   python battleship_project.py

By default, this runs a benchmark simulation comparing 4 different AI strategies.

ALGORITHMS
-------------------------
1. Random: Shoots randomly. No intelligence.
2. BFS: Shoots randomly but never repeats a shot.
3. Standard: Searches in a checkerboard pattern. When it hits a ship, it looks up/down/left/right to finish it.
4. A* (Advanced): Calculates the mathematical probability of where ships are located based on the remaining open space.


HOW TO CHANGE BOARD SIZE (BOUNDS)
---------------------------------
To change the size of the board for the simulation:
1. Open 'battleship_project.py' in your text editor.
2. Scroll down to approximately line 260.
3. Look for the variable:
   CUSTOM_BOARD_SIZE = 30
4. Change the number 30 to whatever size you want (e.g., 10 for a standard game).
5. Save the file and run it again.


HOW TO PLAY AGAINST THE AI (1v1 MODE)
-------------------------------------
The game includes an interactive mode hidden at the bottom of the file. To play:

1. Open 'battleship_project.py'.
2. Scroll to the very bottom of the file.
3. You will see a block of code surrounded by triple quotes (''' ... ''').
4. DELETE the triple quotes at the start (before "player_board = Board()") and at the very end. 

You can also choose which type of algorithm you want the AI opponent to use by replacing the algorithm function name in the "AI's turn" section.

5. (Optional) Add a # symbol in front of the simulation code above it so the benchmarks don't run before your game.
6. Save and run the file. You will now be prompted to enter coordinates.
