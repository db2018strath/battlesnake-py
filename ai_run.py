import simulator as sim
import ai

SNAKE_COUNT = 2
BOARD_WIDTH = 11
BOARD_HEIGHT = 11


board = sim.generate_board(BOARD_WIDTH, BOARD_HEIGHT, SNAKE_COUNT)
while board.winner() == -1:
    print(board)

    #print(ai.get_unselected_action_matrices({}, board))
    board.step({k: ai.mcts_suct(board, k, 200) for k in board.snakes})

print(board)
winner = board.winner()
if winner != None:
    print("Player", winner, "wins!")
else:
    print("Its a draw!")
