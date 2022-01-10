import random as rd
from typing import List, Set

import simulator as sim

# Returns possible_moves without any moves which result in the snake entering out of bounds
def avoid_oob(board: sim.BoardState, possibleMoves: List[sim.Direction], head: sim.Position):
  newPossibleMoves = set()
  for move in possibleMoves:
    newPos = sim.Position(head.x + move.x, head.y + move.y)
    if board.is_in_bounds(newPos):
      newPossibleMoves.add(move)

  return newPossibleMoves

def avoid_snakes(board: sim.BoardState, possibleMoves: List[sim.Direction], head: sim.Position):
  newPossibleMoves = set()
  for move in possibleMoves:
    newPos = sim.Position(head.x + move.x, head.y + move.y)
    for snake in board.snakes:
      if snake.contains(newPos):
        break
    else:
      newPossibleMoves.add(move)
  
  return newPossibleMoves


def safe_player(board: sim.BoardState, playerIndex: int):
  possibleMoves = set(sim.MOVES)

  head = board.snakes[playerIndex].head
  tail = board.snakes[playerIndex].tail

  possibleMoves = avoid_oob(board, possibleMoves, head)
  possibleMoves = avoid_snakes(board, possibleMoves, head)
  
  print("P" + str(playerIndex), "[")
  for move in possibleMoves:
    print(" ", move)
  print("]")

  if possibleMoves:
    return list(possibleMoves)[rd.randrange(len(possibleMoves))]
  else:
    return sim.UP # default to up if all moves are bad