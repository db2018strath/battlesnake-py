import time

import simulator as sim
import ai

"""
This file can be a nice home for your move logic, and to write helper functions.

We have started this for you, with a function to help remove the 'neck' direction
from the list of possible moves!
"""

def convert_to_position(p, h):
  return sim.Position(p["x"], h - 1 - p["y"]) # y is flipped to make +y down

def convert_board(data: dict) -> (sim.BoardState, int):
  w = data["board"]["width"]
  h = data["board"]["height"]

  snakes = {}
  for i in range(len(data["board"]["snakes"])):
    snake = data["board"]["snakes"][i]

    head = convert_to_position(snake["head"], h)
    tail = [convert_to_position(p, h) for p in snake["body"]][1:] # body includes head so ignore first element
    health = snake["health"]
    snakes[snake["id"]] = sim.Snake(head, tail, health)

  food = set([convert_to_position(f, h) for f in data["board"]["food"]])
    
  return sim.BoardState(w, h, snakes, food, data["turn"])

def convert_direction(dir: sim.Direction):
  if dir == sim.UP:
    return "down" # need to flip these to correspond to battlesnake's coordinates
  elif dir == sim.DOWN:
    return "up"
  elif dir == sim.LEFT:
    return "left"
  elif dir == sim.RIGHT:
    return "right"
  else:
    return None


def choose_move(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request

    return: A String, the single move to make. One of "up", "down", "left" or "right".

    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.

    """

    #print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    #print(f"All board data this turn: {data}")
    #print(f"My Battlesnakes head this turn is: {my_head}")
    #print(f"My Battlesnakes body this turn is: {my_body}")

    #print(data)

    snakeID = data["you"]["id"]
    board = convert_board(data)

    t1 = time.time_ns()
    move = convert_direction(ai.mcts_duct(board, snakeID, 200))
    t2 = time.time_ns()
    print(t2 - t1, "ns")

    print(board)
    print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked")

    return move
