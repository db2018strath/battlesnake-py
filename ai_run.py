import simulator as sim
import ai

SNAKE_COUNT = 4


board = sim.generate_board(11, 11, SNAKE_COUNT)
while board.winner() == -1:
  print(board)
  #print(ai.get_unselected_action_matrices({}, board))
  board.step({k: ai.mcts_duct(board, k) for k in board.snakes})

print(board)
winner = board.winner()
if winner != None:
  print("Player", winner, "wins!")
else:
  print("Its a draw!")
