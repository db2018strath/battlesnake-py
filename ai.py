import copy
import itertools
import math
import random as rd
import time

from dataclasses import dataclass
from typing import List, Dict, Set

import simulator as sim

# Returns possible_moves without any moves which result in the snake entering out of bounds
def avoid_oob(board: sim.BoardState, possibleMoves: List[sim.Direction], head: sim.Position):
  newPossibleMoves = set()
  for move in possibleMoves:
    newPos = sim.Position(head.x + move.x, head.y + move.y)
    if board.is_in_bounds(newPos):
      newPossibleMoves.add(move)

  return newPossibleMoves

def avoid_snakes(board: sim.BoardState, possibleMoves: Set[sim.Direction], head: sim.Position):
  newPossibleMoves = set()
  for move in possibleMoves:
    newPos = sim.Position(head.x + move.x, head.y + move.y)
    for snake in board.snakes.values():
      if snake.contains(newPos):
        break
    else:
      newPossibleMoves.add(move)
  
  return newPossibleMoves

def avoid_oob_and_snakes(board: sim.BoardState, possibleMoves: Set[sim.Direction], head: sim.Position):
    newPossibleMoves = set()
    for move in possibleMoves:
        newPos = sim.Position(head.x + move.x, head.y + move.y)
        if (board.is_in_bounds(newPos) and
            not any(map(lambda s: newPos == s.head or newPos in s.tail[:-1], board.snakes.values()))):
            
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
        

def safe_player(board: sim.BoardState, playerId):
  possibleMoves = set(sim.MOVES)

  head = board.snakes[playerId].head
  #tail = board.snakes[playerIndex].tail

  possibleMoves = avoid_oob_and_snakes(board, possibleMoves, head)
  
  if possibleMoves:
    return list(possibleMoves)[rd.randrange(len(possibleMoves))]
  else:
    return sim.UP # default to up if all moves are bad

def chase_food(board: sim.BoardState, playerId):
    head = board.snakes[playerId].head
    
    closestFood = find_closest_food(board, head)
    if closestFood == None:
        return safe_player(board, playerId)
 
    possibleMoves = avoid_oob_and_snakes(board, set(sim.MOVES), head)
        
    bestMove = sim.UP
    bestMoveDistance = math.inf
    for move in possibleMoves:
        newPos = sim.Position(head.x + move.x, head.y + move.y)
        dist = sim.distance(closestFood, newPos)
        if dist < bestMoveDistance:
            bestMove = move
            bestMoveDistance = dist
                
    return bestMove
    
def random_choice(xs, ps):
    if len(xs) != len(ps):
        return None

    total = rd.random()
    for i in range(len(xs)):
        if total < ps[i]:
            return xs[i]
        
        total += ps[i]

    return xs[-1]
    

def simple_player(board: sim.BoardState, playerId: int):
    STRATEGIES = [safe_player, chase_food]
    PROBABILITIES = [0.10, 0.90]

    return random_choice(STRATEGIES, PROBABILITIES)(board, playerId)
    

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
    rewardInfo: Dict[object, Dict[sim.Direction, RewardInfo]]

Tree = Dict[sim.BoardState, Node]

def get_reward(winner, snake):
    if snake == winner:
        return 1.0
    elif winner == None:
        return 0.0
    else:
        return -1.0

def evaluate_state(s: sim.BoardState):
    winner = s.winner()
    return {k: get_reward(winner, k) for k in s.snakes}

def get_safe_actions(s: sim.BoardState, k):
    return avoid_oob_and_snakes(s, sim.MOVES, s.snakes[k].head)
    

def get_all_matrices(possibleMoves: Dict[object, List[sim.Direction]]):
    pmoves = copy.deepcopy(possibleMoves)
    
    if not pmoves:
        return {}
    elif len(pmoves) == 1:
        return [{k: m} for k in pmoves for m in pmoves[k]]
    else:
        (k, ms) = pmoves.popitem()
        rest = get_all_matrices(pmoves)
        
        result = []
        for d in rest:
            for m in ms:
                newDict = copy.deepcopy(d)
                newDict[k] = m
                result.append(newDict)
            
        return result
        
        
def get_unselected_action_matrices(nodes: Tree, s: sim.BoardState):
    possibleActions = {}
    for k in s.snakes:
        actions = get_safe_actions(s, k)
        if actions:
            possibleActions[k] = actions
        else:
            possibleActions[k] = [sim.UP]
            
    return get_all_matrices(possibleActions)


def apply_action(s: sim.BoardState, a: Dict[object, sim.Direction]):
    sNew = copy.deepcopy(s)
    sNew.step(a)
    return sNew

def add_node(nodes: Tree, s: sim.BoardState):
    nodes[s] = Node(0, {k: {m: RewardInfo(0, 0) for m in sim.MOVES} for k in s.snakes})

def longest_snake(s: sim.BoardState):
    index = 0
    longest_length = s.snakes[0].length()
    for i in range(1, len(s.snakes)):
        new_length = s.snakes[i].length()
        if new_length > longest_length:
            longest_length = new_length
            index = i

    return index
        

def mcts_playout(s: sim.BoardState):
    sCopy = copy.deepcopy(s)
    for i in range(50):
        if sCopy.winner() != -1:
            break
        sCopy.step({k: simple_player(sCopy, k) for k in sCopy.snakes})

    if sCopy.winner() != -1:
        return {k: get_reward(sCopy.winner(), k) for k in s.snakes}
    else:
        longest = longest_snake(sCopy)
        return {k: get_reward(longest, k) for k in s.snakes}

def update_node(nodes: Tree, s: sim.BoardState, actions: Dict[object, sim.Direction], rs):
    for k in actions:
        a = actions[k]
        nodes[s].rewardInfo[k][a].totalReward += rs.get(k, -1.0)
        nodes[s].rewardInfo[k][a].visitCount += 1
    nodes[s].visitCount += 1
    
def ucb_duct(tR: int, n: int, n_a: int, c=1.0):
  if n_a == 0:
    return math.inf
  else:
    return (tR / n_a) + c * math.sqrt(math.log(n) / n_a)
    
def select_actions(nodes: Tree, s: sim.BoardState):
    result = {}
    for k in s.snakes:
        bestAction = sim.UP
        bestActionUCB = -math.inf
        for a in get_safe_actions(s, k):
            rewardInfo = nodes[s].rewardInfo[k][a]
            tR = rewardInfo.totalReward
            nA = rewardInfo.visitCount
            n = nodes[s].visitCount
            
            ucb = ucb_duct(tR, n, nA)
            if ucb > bestActionUCB:
                bestAction = a
                bestActionUCB = ucb
        
        result[k] = bestAction
        
    return result
            
            

def mcts_iter(nodes: Tree, s: sim.BoardState):
    if s.winner() != -1: # if in a terminal state
        return evaluate_state(s)
    elif s in nodes and (actionMats := get_unselected_action_matrices(nodes, s)):
        a = actionMats[rd.randrange(len(actionMats))]

        # Calculate next state
        sNew = apply_action(s, a)

        # Add new state to the tree
        add_node(nodes, sNew)

        rs = mcts_playout(sNew)

        nodes[sNew].visitCount += 1

        update_node(nodes, s, a, rs)
        return rs

    else: # selection phase
        actions = select_actions(nodes, s)
        sNew = apply_action(s, actions)
        rs = mcts_iter(nodes, sNew)
        update_node(nodes, s, actions, rs)
        return rs


def mcts_duct(board: sim.BoardState, playerIndex: int, maxTime=150):
    tStart = time.time_ns()
    
    s = copy.deepcopy(board)
    s.foodSpawnChance = 0

    nodes = {}
    add_node(nodes, s)
    while time.time_ns() - tStart < maxTime * 1000000:
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

    print("Nodes Visited:", len(nodes))
    return bestMove
