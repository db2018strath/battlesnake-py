import random as rd
from dataclasses import dataclass
from typing import List, Set, Dict

@dataclass(frozen=True)
class Position:
    x: int
    y: int

Direction = Position

def distance(p1: Position, p2: Position):
  return abs(p1.x - p2.x) + abs(p1.y - p2.y)

UP    = Direction( 0,  1)
DOWN  = Direction( 0, -1)
LEFT  = Direction(-1,  0)
RIGHT = Direction( 1,  0)

# List of available moves
MOVES = [UP, DOWN, LEFT, RIGHT]

SNAKE_MAX_HEALTH = 100

# Values obtained from: https://github.com/BattlesnakeOfficial/rules/blob/main/cli/commands/play.go
DEFAULT_FOOD_SPAWN_CHANCE=15
DEFAULT_MIN_FOOD=1

# Class for storing information about a snake
class Snake:
    def __init__(self, head: Position, tail: List[Position], health=SNAKE_MAX_HEALTH):
        self.head = head
        self.tail = tail
        self.health = health

    def __eq__(self, other):
        return (
            (self.head == other.head) and
            (self.tail == other.tail) and
            (self.health == other.health)
        )


    def length(self):
        return len(self.tail) + 1

    def reset_health(self):
        self.health = SNAKE_MAX_HEALTH

    # Moves the snake in the direction provided (without removing the end of the tail)
    def move(self, direction: Direction):
        # Add the old position of the head to the tail and then update the head
        self.tail.append(self.head)
        self.head = Position(self.head.x + direction.x, self.head.y + direction.y)

        self.health -= 1

    def contains(self, pos: Position):
        return pos == self.head or pos in self.tail

    # Removes the last element of the tail
    def pop_tail(self):
        self.tail.pop(0)

# Class for storing the current state of the board
class BoardState:
    def __init__(self, w: int, h: int, snakes: Dict[object, Snake], food: Set[Position], minFood=DEFAULT_MIN_FOOD, foodSpawnChance=DEFAULT_FOOD_SPAWN_CHANCE):
        self.w = w
        self.h = h
        self.snakes = snakes
        self.food = food
        self.minFood = minFood
        self.foodSpawnChance = foodSpawnChance

    def __eq__(self, other):
        return (
            (self.w == other.w) and
            (self.h == other.h) and
            (self.minFood == other.minFood) and
            (self.foodSpawnChance == other.foodSpawnChance) and
            (self.snakes == other.snakes) and
            (self.food == other.food)
        )

    def __hash__(self):
        return 0 # TODO: change this

    def __str__(self):
        s = "DIM: " + str(self.w) + " x " + str(self.h) + "\n"
        s += "Minimum Food: " + str(self.minFood) + "\n"
        s += "Food Spawn Chance: " + str(self.foodSpawnChance) + "%\n"
        for k in self.snakes:
            s += "Health P" + str(k) + ": " + str(self.snakes[k].health) + "\n"

        s += ('# ' * (self.w + 2)) + "\n# "
        for y in range(self.h):
            for x in range(self.w):
                pos = Position(x, y)

                cell = ""
                for k in self.snakes:
                    if pos == self.snakes[k].head:
                        cell = "H"
                        break
                    elif pos in self.snakes[k].tail:
                        cell = str(k)[0]
                        break
                
                if cell == "":
                    if pos in self.food:
                        cell = "*"
                    else:
                        cell = " "
                
                s += cell + " "
 
            s +="#\n# "
        s += ('# ' * (self.w + 1)) + "\n"
        return s

    # Checks if a given position is in bounds
    def is_in_bounds(self, pos: Position):
        return (0 <= pos.x and pos.x < self.w) and (0 <= pos.y and pos.y < self.h)

    # Has each snake attempt to eat any food under its head. If successful the food is removed
    # from the board and the snake's health is reset, otherwise the snake loses the end of its tail.
    def feed_snakes(self):
        eatenFood = set()
        for k in self.snakes:
            if self.snakes[k].head in self.food:
                self.snakes[k].reset_health()
                eatenFood.add(self.snakes[k].head)
            else:
                self.snakes[k].pop_tail()

        for food in eatenFood:
            self.food.remove(food)

    # Returns a list of all of the squares not being occupied by snakes or food
    def get_empty_squares(self):
        emptySquares = []
        for y in range(self.h):
            for x in range(self.w):
                pos = Position(x, y)
                if not any(map(lambda s: s.contains(pos), self.snakes.values())) and pos not in self.food:
                    emptySquares.append(pos)

        return emptySquares


    # Randomly places food in an empty square
    def randomly_place_food(self, n: int):
        emptySquares = self.get_empty_squares()
        if emptySquares:
            rd.shuffle(emptySquares)
            newFood = emptySquares[:n]
            for food in newFood:
                self.food.add(food)


    # Adds new food to the board
    def spawn_food(self):
        if len(self.food) < self.minFood:
            self.randomly_place_food(self.minFood - len(self.food))
        elif rd.randrange(100) < self.foodSpawnChance:
            self.randomly_place_food(1)


    def eliminate_snakes(self):
        toBeEliminated = set()
        for k in self.snakes:
            # Eliminate snakes that are out of bounds or have ran out of health
            if not self.is_in_bounds(self.snakes[k].head) or self.snakes[k].health <= 0:
                toBeEliminated.add(k)

            # Eliminate if self intersecting
            if self.snakes[k].head in self.snakes[k].tail:
                toBeEliminated.add(k)

            # Eliminate snakes that are colliding with another
            for k2 in self.snakes:
                if k != k2:
                    if (self.snakes[k].head == self.snakes[k2].head and
                        self.snakes[k].length() <= self.snakes[k2].length()):
                    
                        toBeEliminated.add(k)
                    elif self.snakes[k].head in self.snakes[k2].tail:
                        toBeEliminated.add(k)
                            
        for k in toBeEliminated:
            self.snakes.pop(k)


    # Updates the board by one step using the inputs given for each snake
    def step(self, moves: Dict[object, Direction]):
        for k in self.snakes:
            self.snakes[k].move(moves[k])

        self.feed_snakes()
        self.spawn_food()
        self.eliminate_snakes()

    # Returns the winner of the game if the game has ended (or None on a draw).
    # If the game has not ended then -1 is returned
    def winner(self):
        if len(self.snakes) > 1:
            return -1
        elif len(self.snakes) == 1:
            return list(self.snakes.keys())[0]
        else:
            return None


def generate_board(w: int, h: int, noSnakes: int, minFood=DEFAULT_MIN_FOOD, foodSpawnChance=DEFAULT_FOOD_SPAWN_CHANCE):
    SNAKE_POSITIONS = ([
        Position(1, 1),
        Position(w - 2, h - 2),
        Position(w - 2, 1),
        Position(1, h - 2)
    ])

    if noSnakes == 0 or noSnakes > len(SNAKE_POSITIONS):
        return None

    possible_snakes = list(map(lambda p: Snake(p, [p] * 2), SNAKE_POSITIONS))
    rd.shuffle(possible_snakes)
    snakes = {i: possible_snakes[i] for i in range(noSnakes)}

    possible_food = [Position(x, y) for x in range(w) for y in range(h) if Position(x, y) not in SNAKE_POSITIONS]
    rd.shuffle(possible_food)
    food = set(possible_food[:minFood])
    
    return BoardState(w, h, snakes, food, minFood, foodSpawnChance)
