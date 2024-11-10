from enum import Enum

class Tile(Enum):
    BLANCO = 0
    AGENTE = 1
    HOYO = 2
    WUMPUS = 3
    ORO = 4
    HEDOR = 5
    BRISA = 6
    HEDOR_ORO = 7
    BRISA_ORO = 8
    BRISA_HEDOR = 9
    BRISA_HEDOR_ORO = 10

# Movimientos posibles
MOVE_UP = 'up'
MOVE_DOWN = 'down'
MOVE_LEFT = 'left'
MOVE_RIGHT = 'right'
