# Battleship-Solitaire-Solver
A friendly AI will solve a Battleship Solitaire puzzle for you! (CSP)

## Description

This project was to implement a Constraint Satisfaction Problem solver for the domain of Battleship Solitaire puzzles, using forward checking, general arc consistency, and backtracking search.

To fully understand the puzzle, here are links to the more detailed description Battleship (puzzle) - Wikipedia and the website that you can play games of battleship solitaire for free Battleship Solitaire: Mindless Podcast Companion.

Basically, the main rules we follow are:

1. There are four types of ships: Submarines (1x1), Destroyers (1x2), Cruisers (1x3), Battleships (1x4).
2. Ships can be oriented vertically or horizontally, not diagonally.
3. The puzzle provides the number of ships for each type.
4. Ships cannot touch each other, including diagonally. They must be surrounded by at least one square of water on all sides and corners.
5. Some puzzles reveal the contents of certain squares:
– Revealed ship pieces indicate if they are middle or end portions and the orientation of the rest of the ship.
– Submarines are revealed as the entire ship.

## How to run a solver:

python3 battle.py <input file> <output file>


Assuming that input files are in correct formats as described below, the solver is expected to solve the puzzle on the output file if we run this command, within at most 5 minutes.


## Example Input Format:

Row constraints on the first line.
Column constraints on the second line.
Ship counts on the third line.
Remaining lines represent the starting layout of the puzzle.
Characters: '0', 'S', 'W', 'L', 'R', 'T', 'B', 'M'.

## Example Output Format:

Similar format to the input, with the final solution printed.
Each character represents a cell in the solution grid.

## Example Input and Output:
Input:
211222
140212
321
000000
0000S0
000000
000000
00000W
000000

Output:
LRWWWW
WWWWSW
WTWWWW
WMWWWS
WBWTWW
WWWBWS

## Note
This project was for a course CSC384H1: Introduction to Artificial Intelligence.
