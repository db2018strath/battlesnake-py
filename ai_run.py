import simulator as sim
import ai

SNAKE_COUNT = 1

board = sim.generate_board(11, 11, SNAKE_COUNT)
while board.winner() == -1:
  print(board)
  board.step([ai.mcts_duct(board, i) for i in range(SNAKE_COUNT)])

print(board)
winner = board.winner()
if winner != None:
  print("Player", winner, "wins!")
else:
  print("Its a draw!")
