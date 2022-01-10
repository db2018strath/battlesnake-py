import random
import math
from typing import List, Dict

import simulator as sim

"""
This file can be a nice home for your move logic, and to write helper functions.

We have started this for you, with a function to help remove the 'neck' direction
from the list of possible moves!
"""

def get_new_position(pos: Dict[str, int], move: str):
  result = pos.copy()
  if move == "left":
    result["x"] -= 1
  elif move == "right":
    result["x"] += 1
  elif move == "up":
    result["y"] += 1
  elif move == "down":
    result["y"] -= 1
  return result

def avoid_my_neck(my_head: Dict[str, int], my_body: List[dict], possible_moves: List[str]) -> List[str]:
    """
    my_head: Dictionary of x/y coordinates of the Battlesnake head.
            e.g. {"x": 0, "y": 0}
    my_body: List of dictionaries of x/y coordinates for every segment of a Battlesnake.
            e.g. [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]
    possible_moves: List of strings. Moves to pick from.
            e.g. ["up", "down", "left", "right"]

    return: The list of remaining possible_moves, with the 'neck' direction removed
    """
    my_neck = my_body[1]  # The segment of body right after the head is the 'neck'

    if my_neck["x"] < my_head["x"]:  # my neck is left of my head
        possible_moves.remove("left")
    elif my_neck["x"] > my_head["x"]:  # my neck is right of my head
        possible_moves.remove("right")
    elif my_neck["y"] < my_head["y"]:  # my neck is below my head
        possible_moves.remove("down")
    elif my_neck["y"] > my_head["y"]:  # my neck is above my head
        possible_moves.remove("up")

    return possible_moves

def check_in_bounds(pos: Dict[str, int], w: int, h: int) -> bool:
  x, y = pos["x"], pos["y"]
  return (x >= 0 and x < w) and (y >= 0 and y < h)

def avoid_oob(pos: Dict[str, int], w: int, h: int, possible_moves: List[str]) -> List[str]:
  return list(filter(lambda m : check_in_bounds(get_new_position(pos, m), w, h), possible_moves))

def avoid_body(pos, body, possible_moves):
  return list(filter(lambda m : get_new_position(pos, m) not in body, possible_moves))

def avoid_snakes(pos, snakes, possible_moves):
  result = possible_moves[:]
  for snake in snakes:
    body = snake["body"]
    result = list(filter(lambda m : get_new_position(pos, m) not in body, possible_moves))
  return result

def distance(p1, p2):
  return abs(p1["x"] - p2["x"]) + abs(p1["y"] - p2["y"])

def find_closest_food(pos, foods):
  closest_distance = math.inf
  closest_food = None
  for food in foods:
    dist = distance(pos, food)
    if dist < closest_distance:
      closest_distance = dist
      closest_food = food
  return (closest_distance, closest_food)

def convert_to_position(p, h):
  return sim.Position(p["x"], h - 1 - p["y"]) # y is flipped to make +y down

def convert_board(data: dict) -> sim.BoardState:
  w = data["board"]["width"]
  h = data["board"]["height"]

  snakes = []
  for snake in data["board"]["snakes"]:
    head = convert_to_position(snake["head"], h)
    tail = [convert_to_position(p, h) for p in snake["body"]][1:] # body includes head so ignore first element
    health = snake["health"]
    snakes.append(sim.Snake(head, tail, health))

  food = set([convert_to_position(f, h) for f in data["board"]["food"]])
  minFood = 3 # TODO: change
  foodSpawnChance = 20 # TODO: change
    
  return sim.BoardState(w, h, snakes, food, minFood, foodSpawnChance)


def choose_move(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request

    return: A String, the single move to make. One of "up", "down", "left" or "right".

    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.

    """
    my_head = data["you"]["head"]  # A dictionary of x/y coordinates like {"x": 0, "y": 0}
    my_body = data["you"]["body"]  # A list of x/y coordinate dictionaries like [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]

    #print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    #print(f"All board data this turn: {data}")
    #print(f"My Battlesnakes head this turn is: {my_head}")
    #print(f"My Battlesnakes body this turn is: {my_body}")

    possible_moves = ["up", "down", "left", "right"]

    # Don't allow your Battlesnake to move back in on it's own neck
    possible_moves = avoid_my_neck(my_head, my_body, possible_moves)

    board_height = data["board"]["height"]
    board_width = data["board"]["width"]
    
    possible_moves = avoid_oob(my_head, board_width, board_height,possible_moves)

    possible_moves = avoid_body(my_head, my_body, possible_moves)

    possible_moves = avoid_snakes(my_head, data["board"]["snakes"], possible_moves)

    if possible_moves == []:
      move = "up"
    else:
      #move = random.choice(possible_moves)
      (d, food) = find_closest_food(my_head, data["board"]["food"])
      move = possible_moves[0]
      for m in possible_moves:
        d2 = distance(get_new_position(my_head, m), food)
        if d2 < d:
          move = m
          break

    print(convert_board(data))
    print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked from all valid options in {possible_moves}")

    return move
