import copy
import itertools
import math
import random as rd
import time

from dataclasses import dataclass
from typing import List, Dict

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

def avoid_oob_and_snakes(board: sim.BoardState, possibleMoves: List[sim.Direction], head: sim.Position):
    newPossibleMoves = set()
    for move in possibleMoves:
        newPos = sim.Position(head.x + move.x, head.y + move.y)
        if board.is_in_bounds(newPos) and not any(map(lambda s: s.contains(newPos), board.snakes)):
            newPossibleMoves.add(move)

    return newPossibleMoves

def find_closest_food(board: sim.BoardState, pos: sim.Position): 
    minDistance = math.inf
    closestFood = None
    
    for food in board.food:
        dist = sim.distance(pos, food)
        if dist < minDistance:
            closestFood = food
            minDistance = dist
            
    return closestFood
        

def safe_player(board: sim.BoardState, playerIndex: int):
  possibleMoves = set(sim.MOVES)

  head = board.snakes[playerIndex].head
  #tail = board.snakes[playerIndex].tail

  possibleMoves = avoid_oob_and_snakes(board, possibleMoves, head)
  
  if possibleMoves:
    return list(possibleMoves)[rd.randrange(len(possibleMoves))]
  else:
    return sim.UP # default to up if all moves are bad

def chase_food(board: sim.BoardState, playerIndex: int):
    possibleMoves = set(sim.MOVES)
    
    head = board.snakes[playerIndex].head
    
    possibleMoves = avoid_oob_and_snakes(board, possibleMoves, head)
    
    closestFood = find_closest_food(board, head)
    
    bestMove = sim.UP
    bestMoveDistance = math.inf
    for move in possibleMoves:
        newPos = sim.Position(head.x + move.x, head.y + move.y)
        dist = sim.distance(closestFood, newPos)
        if dist < bestMoveDistance:
            bestMove = move
            bestMoveDistance = dist
                
    return bestMove
    
def simple_player(board: sim.BoardState, playerIndex: int):
    STRATEGIES = [safe_player, chase_food]
    
    return STRATEGIES[rd.randrange(len(STRATEGIES))](board, playerIndex)

#------------------------#
#          MCTS          #
#------------------------#

@dataclass
class RewardInfo:
    visitCount: int
    totalReward: int

@dataclass
class Node:
    visitCount: int
    rewardInfo: List[Dict[sim.Direction, RewardInfo]]

Tree = Dict[sim.BoardState, Node]
    
def generate_safe_move_matrix(board: sim.BoardState):
    return itertools.product(*[avoid_oob_and_snakes(board, sim.MOVES, snake.head) for snake in board.snakes])

def apply_action(s: sim.BoardState, actions: List[sim.Direction]):
    sNew = copy.deepcopy(s)
    sNew.step(actions)
    return sNew

def get_unselected_action_matrix(nodes: Tree, s: sim.BoardState):
    return [ms for ms in generate_safe_move_matrix(s) if apply_action(s, ms) not in nodes]

def choose_unselected_action(nodes: Tree, s: sim.BoardState):
    actions = get_unselected_action_matrix(nodes, s)
    return actions[rd.randrange(len(actions))]

def evaluate_state(s: sim.BoardState):
    rewards = []
    winner = s.winner()
    for i in range(len(s.snakes)):
        if winner == i:
            rewards.append(1)
        elif winner == None:
            rewards.append(0)
        else:
            rewards.append(-1)

    return rewards

def add_node(nodes: Tree, s: sim.BoardState):
    nodes[s] = Node(0, [
            {
                sim.UP: RewardInfo(0, 0),
                sim.DOWN: RewardInfo(0, 0),
                sim.LEFT: RewardInfo(0, 0),
                sim.RIGHT: RewardInfo(0, 0)
            } 
            for _ in s.snakes]
        )

def mcts_playout(s: sim.BoardState):
    state = copy.deepcopy(s)
    while state.winner() == -1:
        state.step([simple_player(s, i) for i in range(len(s.snakes))])

    return evaluate_state(state)


def update_node(nodes: Tree, s: sim.BoardState, actions: List[sim.Direction], rs: List[int]):
    for i in range(len(s.snakes)):
        nodes[s].rewardInfo[i][actions[i]].totalReward += rs[i]
        nodes[s].rewardInfo[i][actions[i]].visitCount += 1
    nodes[s].visitCount += 1

def select_action(nodes: Tree, s: sim.BoardState):
    actionMatrix = []
    for i in range(len(s.snakes)):
        bestMove = sim.MOVES[0]
        bestMoveUCB = -math.inf
        for m in sim.MOVES:
            rewardInfo = nodes[s].rewardInfo[(i, m)]

            n_a = rewardInfo.visitCount
            x = rewardInfo.totalReward / n_a

            c = 1 # TODO: change this
            ucb = x + c * math.sqrt(math.log(nodes[s].visitCount) / n_a)

            if ucb > bestMoveUCB:
                bestMove = m
                bestMoveUCB = ucb

        actionMatrix.append(bestMove)

    return actionMatrix


def mcts_iter(nodes: Tree, s: sim.BoardState):
    if s.winner() != -1: # if in a terminal state
        return evaluate_state(s)
    elif s in nodes and len(get_unselected_action_matrix(nodes, s)) != 0:
        a = choose_unselected_action(nodes, s)

        # Calculate next state
        sNew = apply_action(s, a)

        # Add new state to the tree
        add_node(nodes, sNew)

        rs = mcts_playout(sNew)

        nodes[sNew].visitCount += 1

        update_node(nodes, s, a, rs)
        return rs

    else: # selection phase
        a = select_action(nodes, s)
        sNew = apply_action(s, a)
        rs = mcts_iter(nodes, sNew)
        update_node(nodes, s, a, rs)
        return rs


def mcts_duct(board: sim.BoardState, playerIndex: int, maxTime=150):
    tStart = time.time_ns()
    
    s = copy.deepcopy(board)
    
    nodes = {}
    add_node(nodes, s)
    while time.time_ns() - tStart < maxTime * 1000000:
    #for i in range(10):
        mcts_iter(nodes, s)

    bestMove = sim.MOVES[0]
    bestMoveReward = -math.inf
    for m in sim.MOVES:
        rewardInfo = nodes[s].rewardInfo[playerIndex][m]
        if rewardInfo.visitCount != 0:
            x = rewardInfo.totalReward / rewardInfo.visitCount

            if x > bestMoveReward:
                bestMove = m
                bestMoveReward = x

    return bestMove
