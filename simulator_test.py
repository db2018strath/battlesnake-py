import random as rd
import simulator as sim

board = sim.generate_board(11, 11, 2, 3, 5)
print(board)

while board.winner() == -1:
  board.step([sim.MOVES[rd.randrange(len(sim.MOVES))] for i in range(2)])
  print(board)

print(board.winner())