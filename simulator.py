import random as rd
from dataclasses import dataclass
from typing import List, Set

@dataclass(frozen=True)
class Position:
    x: int
    y: int

Direction = Position

UP    = Direction( 0,  1)
DOWN  = Direction( 0, -1)
LEFT  = Direction(-1,  0)
RIGHT = Direction( 1,  0)

# List of available moves
MOVES = [UP, DOWN, LEFT, RIGHT]

SNAKE_MAX_HEALTH = 100

# Class for storing information about a snake
class Snake:
    def __init__(self, head: Position, tail: List[Position]):
        self.head = head
        self.tail = tail
        self.health = SNAKE_MAX_HEALTH
        self.alive = True

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
    def __init__(self, w: int, h: int, snakes: List[Snake], food: Set[Position], minFood: int, foodSpawnChance: int):
        self.w = w
        self.h = h
        self.snakes = snakes
        self.food = food
        self.minFood = minFood
        self.foodSpawnChance = foodSpawnChance

    def __str__(self):
        s = "DIM: " + str(self.w) + " x " + str(self.h) + "\n"
        s += "Minimum Food: " + str(self.minFood) + "\n"
        s += "Food Spawn Chance: " + str(self.foodSpawnChance) + "%\n"

        s += ('# ' * (self.w + 2)) + "\n# "
        for y in range(self.h):
            for x in range(self.w):
                pos = Position(x, y)

                cell = ""
                for i in range(len(self.snakes)):
                    if pos == self.snakes[i].head:
                        cell = "H"
                        break
                    elif pos in self.snakes[i].tail:
                        cell = str(i)
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
        for i in range(len(self.snakes)):
            if self.snakes[i].alive:
                if self.snakes[i].head in self.food:
                    self.snakes[i].reset_health()
                    eatenFood.add(self.snakes[i].head)
                else:
                    self.snakes[i].pop_tail()

        for food in eatenFood:
            self.food.remove(food)

    # Returns a list of all of the squares not being occupied by snakes or food
    def get_empty_squares(self):
        emptySquares = []
        for y in range(self.h):
            for x in range(self.w):
                pos = Position(x, y)
                if not any(map(lambda s: s.contains(pos), self.snakes)) and pos not in self.food:
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
        for i in range(len(self.snakes)):
            if self.snakes[i].alive:
                # Eliminate snakes that are out of bounds or have ran out of health
                if not self.is_in_bounds(self.snakes[i].head) or self.snakes[i].health <= 0:
                    toBeEliminated.add(i)

                # Eliminate if self intersecting
                if self.snakes[i].head in self.snakes[i].tail:
                    toBeEliminated.add(i)

                # Eliminate snakes that are colliding with another
                for j in range(i + 1, len(self.snakes)):
                    if self.snakes[i].head == self.snakes[j].head:
                        li = self.snakes[i].length()
                        lj = self.snakes[j].length()
                        if li <= lj:
                            toBeEliminated.add(i)
                        if lj <= li:
                            toBeEliminated.add(j)
                    else:
                        if self.snakes[i].head in self.snakes[j].tail:
                            toBeEliminated.add(i)
                        if self.snakes[j].head in self.snakes[i].tail:
                            toBeEliminated.add(j)

        for i in toBeEliminated:
            self.snakes[i].alive = False


    # Updates the board by one step using the inputs given for each snake
    def step(self, moves: Direction):
        for i in range(len(self.snakes)):
            if self.snakes[i].alive:
                self.snakes[i].move(moves[i])

        self.feed_snakes()
        self.spawn_food()
        self.eliminate_snakes()

    # Returns the winner of the game if the game has ended (or None on a draw).
    # If the game has not ended then -1 is returned
    def winner(self):
        winner = None
        aliveCount = 0
        for i in range(len(self.snakes)):
            if self.snakes[i].alive:
                if aliveCount == 0:
                    winner = i
                    aliveCount += 1
                else:
                    return -1

        return winner


def generate_board(w: int, h: int, noSnakes: int, minFood: int, foodSpawnChance: int):
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
    snakes = possible_snakes[:noSnakes]

    possible_food = [Position(x, y) for x in range(w) for y in range(h) if Position(x, y) not in SNAKE_POSITIONS]
    rd.shuffle(possible_food)
    food = set(possible_food[:minFood])
    
    return BoardState(w, h, snakes, food, minFood, foodSpawnChance)
