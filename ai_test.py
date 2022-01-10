import copy

import simulator as sim
import ai

def get_all_possible_moves(noSnakes: int, prefix=[]):
  if noSnakes == 0:
    return [prefix]

  moves = []
  for m in sim.MOVES:
    moves += get_all_possible_moves(noSnakes - 1, prefix + [m])

  return moves

def is_safe_move(board: sim.BoardState, snakeId: int, move: sim.Direction):
  for ms in get_all_possible_moves(len(board.snakes) - 1):
    boardClone = copy.deepcopy(board)
    boardClone.step(ms[:snakeId] + [move] + ms[snakeId:])
    if not boardClone.snakes[snakeId].alive:
      return False

  return True

def is_in_bounds(w: int, h: int, pos: sim.Position):
  return (0 <= pos.x and pos.x < w) and (0 <= pos.y and pos.y < h)

def test_avoid_oob():
  for y in range(11):
    for x in range(11):
      head = sim.Position(x, y)
      board = sim.BoardState(11, 11, [sim.Snake(head, [])], set())
      if not all(map(lambda m: is_safe_move(board, 0, m), ai.avoid_oob(board, sim.MOVES, head))):
        return False

  return True

def test_avoid_neck():
  for y in range(1, 10):
    for x in range(1, 10):
      head = sim.Position(x, y)
      for tail in [[sim.Position(x + d.x, y + d.y)] for d in sim.MOVES]:
        board = sim.BoardState(11, 11, [sim.Snake(head, tail), sim.Snake(sim.Position(-1, -1), [])], set())
        if not all(map(lambda m: is_safe_move(board, 0, m), ai.avoid_snakes(board, sim.MOVES, head))):
          print(board)
          print(ai.avoid_snakes(board, sim.MOVES, head))
          return False

  return True

def test_avoid_oob_and_neck():
  for y in range(11):
    for x in range(11):
      head = sim.Position(x, y)
      for tail in [[p] for d in sim.MOVES for p in [sim.Position(x + d.x, y + d.y)] if is_in_bounds(11, 11, p)]:
        board = sim.BoardState(11, 11, [sim.Snake(head, tail)], set())
        moves = ai.avoid_snakes(board, ai.avoid_oob(board, sim.MOVES, head), head)
        print(board)
        print(moves)
        if not all(map(lambda m: is_safe_move(board, 0, m), moves)):
          return False

  return True

print("AvoidOOB:", test_avoid_oob())
print("AvoidNeck:", test_avoid_neck())
#print("AvoidOOB&Neck", test_avoid_oob_and_neck())