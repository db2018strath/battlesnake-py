import simulator as sim
import ai

SNAKE_COUNT = 2

board = sim.generate_board(11, 11, SNAKE_COUNT)
while board.winner() == -1:
  print(board)
  board.step([ai.safe_player(board, i) for i in range(SNAKE_COUNT)])

print(board)
winner = board.winner()
if winner != None:
  print("Player", winner, "wins!")
else:
  print("Its a draw!")