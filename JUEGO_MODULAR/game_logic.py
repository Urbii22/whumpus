# game_logic.py
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import random
import math

from constants import Tile, MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT

@dataclass
class TableroWumpus:
    tamano: int = 6
    matrix: List[List[Tile]] = field(default_factory=lambda: [[Tile.BLANCO]*6 for _ in range(6)])
    pos_agente: Tuple[int, int] = (5, 0)
    pos_wumpus: Tuple[int, int] = field(init=False)
    pos_oro: Tuple[int, int] = field(init=False)
    pos_hoyos: List[Tuple[int, int]] = field(default_factory=list)
    game_over: bool = False
    game_result: Optional[str] = None  # 'win', 'lose_wumpus', 'lose_hoyo'

    def __post_init__(self):
        self.place_tile(*self.pos_agente, Tile.AGENTE)
        self.colocar_elementos()

    def place_tile(self, row: int, col: int, tile: Tile):
        """Coloca un elemento en la posición especificada del tablero."""
        if 0 <= row < self.tamano and 0 <= col < self.tamano:
            self.matrix[row][col] = tile
        else:
            raise IndexError(f"Coordenadas fuera del tablero: ({row}, {col})")

    def colocar_elementos(self):
        """Coloca el Wumpus, el oro y los hoyos en el tablero."""
        posiciones_disponibles = [(i, j) for i in range(self.tamano) for j in range(self.tamano)]
        posiciones_disponibles.remove(self.pos_agente)

        # Colocar el Wumpus
        self.pos_wumpus = random.choice(posiciones_disponibles)
        self.place_tile(*self.pos_wumpus, Tile.WUMPUS)
        posiciones_disponibles.remove(self.pos_wumpus)

        # Colocar el oro
        posiciones_no_adyacentes = [pos for pos in posiciones_disponibles if not self.es_adyacente(pos, self.pos_agente)]
        self.pos_oro = random.choice(posiciones_no_adyacentes)
        self.place_tile(*self.pos_oro, Tile.ORO)
        posiciones_disponibles.remove(self.pos_oro)

        # Colocar los hoyos
        posiciones_para_hoyos = [pos for pos in posiciones_disponibles if not self.es_adyacente(pos, self.pos_agente)]
        self.pos_hoyos = random.sample(posiciones_para_hoyos, 2)
        for hoyo_pos in self.pos_hoyos:
            self.place_tile(*hoyo_pos, Tile.HOYO)
            posiciones_disponibles.remove(hoyo_pos)

        # Colocar hedores y brisas
        self.actualizar_hedor_brisa()

    def es_adyacente(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """Determina si dos posiciones son adyacentes en el tablero."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1

    def obtener_vecinos(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Obtiene las posiciones vecinas válidas de una posición dada."""
        i, j = pos
        vecinos = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            x, y = i + dx, j + dy
            if 0 <= x < self.tamano and 0 <= y < self.tamano:
                vecinos.append((x, y))
        return vecinos

    def actualizar_hedor_brisa(self):
        """Actualiza las casillas de hedor y brisa alrededor del Wumpus y los hoyos."""
        # Colocar hedores alrededor del Wumpus
        for vecino in self.obtener_vecinos(self.pos_wumpus):
            tile = self.matrix[vecino[0]][vecino[1]]
            if tile == Tile.BLANCO:
                self.place_tile(*vecino, Tile.HEDOR)
            elif tile == Tile.ORO:
                self.place_tile(*vecino, Tile.HEDOR_ORO)

        # Colocar brisas alrededor de los hoyos
        for hoyo_pos in self.pos_hoyos:
            for vecino in self.obtener_vecinos(hoyo_pos):
                tile = self.matrix[vecino[0]][vecino[1]]
                if tile == Tile.BLANCO:
                    self.place_tile(*vecino, Tile.BRISA)
                elif tile == Tile.HEDOR:
                    self.place_tile(*vecino, Tile.BRISA_HEDOR)
                elif tile == Tile.ORO:
                    self.place_tile(*vecino, Tile.BRISA_ORO)
                elif tile == Tile.HEDOR_ORO:
                    self.place_tile(*vecino, Tile.BRISA_HEDOR_ORO)

    def utility(self) -> float:
        """Calcula la utilidad del estado actual del tablero."""
        pos_agente = self.pos_agente
        pos_oro = self.pos_oro
        distancia = abs(pos_oro[0] - pos_agente[0]) + abs(pos_oro[1] - pos_agente[1])

        penalizacion = 0
        tile_actual = self.matrix[pos_agente[0]][pos_agente[1]]
        if tile_actual in [Tile.HEDOR, Tile.BRISA, Tile.BRISA_HEDOR]:
            penalizacion += 0.1

        utilidad = -distancia - penalizacion
        return utilidad

    def can_move(self, direction: str) -> bool:
        """Determina si el agente puede moverse en una dirección dada."""
        row, col = self.pos_agente
        if direction == MOVE_UP:
            return row > 0
        elif direction == MOVE_DOWN:
            return row < self.tamano - 1
        elif direction == MOVE_LEFT:
            return col > 0
        elif direction == MOVE_RIGHT:
            return col < self.tamano - 1
        return False

    def move_agent(self, direction: str):
        """Mueve el agente en la dirección especificada, si es posible."""
        if not self.can_move(direction):
            return  # Movimiento no válido

        old_row, old_col = self.pos_agente
        new_row, new_col = old_row, old_col

        if direction == MOVE_UP:
            new_row -= 1
        elif direction == MOVE_DOWN:
            new_row += 1
        elif direction == MOVE_LEFT:
            new_col -= 1
        elif direction == MOVE_RIGHT:
            new_col += 1

        # Actualizar la posición del agente
        self.pos_agente = (new_row, new_col)

        # Restaurar la casilla anterior (puede ser BLANCO o un percepto)
        self.restore_tile(old_row, old_col)

        # Guardar el contenido de la nueva casilla para verificar eventos
        tile_destino = self.matrix[new_row][new_col]

        # Colocar el agente en la nueva posición
        self.place_tile(new_row, new_col, Tile.AGENTE)

        # Verificar si el juego ha terminado
        self.verificar_estado_juego(tile_destino)

    def restore_tile(self, row: int, col: int):
        """Restaura una casilla después de que el agente se mueve."""
        # Verificar los perceptos alrededor de la casilla
        vecinos = self.obtener_vecinos((row, col))
        tiene_hedor = any(self.matrix[v[0]][v[1]] in [Tile.WUMPUS] for v in vecinos)
        tiene_brisa = any(self.matrix[v[0]][v[1]] in [Tile.HOYO] for v in vecinos)

        if self.pos_oro == (row, col):
            if tiene_hedor and tiene_brisa:
                self.place_tile(row, col, Tile.BRISA_HEDOR_ORO)
            elif tiene_hedor:
                self.place_tile(row, col, Tile.HEDOR_ORO)
            elif tiene_brisa:
                self.place_tile(row, col, Tile.BRISA_ORO)
            else:
                self.place_tile(row, col, Tile.ORO)
        else:
            if tiene_hedor and tiene_brisa:
                self.place_tile(row, col, Tile.BRISA_HEDOR)
            elif tiene_hedor:
                self.place_tile(row, col, Tile.HEDOR)
            elif tiene_brisa:
                self.place_tile(row, col, Tile.BRISA)
            else:
                self.place_tile(row, col, Tile.BLANCO)

    def verificar_estado_juego(self, tile_destino: Tile):
        """Verifica si el juego ha terminado después del movimiento del agente."""
        if tile_destino == Tile.ORO or tile_destino in [Tile.BRISA_ORO, Tile.HEDOR_ORO, Tile.BRISA_HEDOR_ORO]:
            self.game_over = True
            self.game_result = 'win'
        elif tile_destino == Tile.WUMPUS:
            self.game_over = True
            self.game_result = 'lose_wumpus'
        elif tile_destino == Tile.HOYO:
            self.game_over = True
            self.game_result = 'lose_hoyo'

    def get_available_moves(self) -> List[str]:
        """Obtiene una lista de movimientos disponibles para el agente."""
        moves = []
        for direction in [MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT]:
            if self.can_move(direction):
                moves.append(direction)
        return moves

    def simulate_move(self, direction: str):
        """Simula un movimiento del agente y devuelve un nuevo estado."""
        new_state = TableroWumpus()
        new_state.matrix = [row.copy() for row in self.matrix]
        new_state.pos_agente = self.pos_agente
        new_state.pos_wumpus = self.pos_wumpus
        new_state.pos_oro = self.pos_oro
        new_state.pos_hoyos = self.pos_hoyos.copy()
        new_state.game_over = self.game_over
        new_state.game_result = self.game_result

        new_state.move_agent(direction)
        return new_state

    def is_game_over(self) -> bool:
        """Indica si el juego ha terminado."""
        return self.game_over

    # Métodos para los movimientos de los hoyos (jugador Min)
    def get_available_moves_min(self) -> List[Tuple[int, Tuple[int, int]]]:
        """Obtiene una lista de movimientos disponibles para los hoyos."""
        moves = []
        for idx, hoyo_pos in enumerate(self.pos_hoyos):
            vecinos = self.obtener_vecinos(hoyo_pos)
            for vecino in vecinos:
                if self.can_move_hoyo(vecino):
                    moves.append((idx, vecino))
        return moves

    def can_move_hoyo(self, pos: Tuple[int, int]) -> bool:
        """Verifica si un hoyo puede moverse a una posición dada."""
        tile = self.matrix[pos[0]][pos[1]]
        forbidden_tiles = {Tile.AGENTE, Tile.WUMPUS, Tile.ORO, Tile.BRISA_ORO, Tile.HEDOR_ORO, Tile.BRISA_HEDOR_ORO}
        return tile not in forbidden_tiles and tile in {Tile.BLANCO, Tile.BRISA, Tile.HEDOR, Tile.BRISA_HEDOR}

    def move_hoyo(self, hoyo_index: int, new_pos: Tuple[int, int]):
        """Mueve un hoyo a una nueva posición."""
        old_pos = self.pos_hoyos[hoyo_index]
        self.place_tile(*old_pos, Tile.BLANCO)
        self.actualizar_brisa_al_eliminar_hoyo(old_pos)

        self.place_tile(*new_pos, Tile.HOYO)
        self.pos_hoyos[hoyo_index] = new_pos
        self.actualizar_brisa_al_agregar_hoyo(new_pos)

    def actualizar_brisa_al_eliminar_hoyo(self, pos: Tuple[int, int]):
        """Actualiza las brisas al eliminar un hoyo."""
        for vecino in self.obtener_vecinos(pos):
            tile = self.matrix[vecino[0]][vecino[1]]
            if tile == Tile.BRISA:
                self.place_tile(*vecino, Tile.BLANCO)
            elif tile == Tile.BRISA_HEDOR:
                self.place_tile(*vecino, Tile.HEDOR)
            elif tile == Tile.BRISA_ORO:
                self.place_tile(*vecino, Tile.ORO)
            elif tile == Tile.BRISA_HEDOR_ORO:
                self.place_tile(*vecino, Tile.HEDOR_ORO)

    def actualizar_brisa_al_agregar_hoyo(self, pos: Tuple[int, int]):
        """Actualiza las brisas al agregar un hoyo."""
        for vecino in self.obtener_vecinos(pos):
            tile = self.matrix[vecino[0]][vecino[1]]
            if tile == Tile.BLANCO:
                self.place_tile(*vecino, Tile.BRISA)
            elif tile == Tile.HEDOR:
                self.place_tile(*vecino, Tile.BRISA_HEDOR)
            elif tile == Tile.ORO:
                self.place_tile(*vecino, Tile.BRISA_ORO)
            elif tile == Tile.HEDOR_ORO:
                self.place_tile(*vecino, Tile.BRISA_HEDOR_ORO)

    def simulate_move_min(self, move: Tuple[int, Tuple[int, int]]):
        """Simula un movimiento de un hoyo y devuelve un nuevo estado."""
        hoyo_index, new_pos = move
        new_state = TableroWumpus()
        new_state.matrix = [row.copy() for row in self.matrix]
        new_state.pos_agente = self.pos_agente
        new_state.pos_wumpus = self.pos_wumpus
        new_state.pos_oro = self.pos_oro
        new_state.pos_hoyos = self.pos_hoyos.copy()
        new_state.game_over = self.game_over
        new_state.game_result = self.game_result

        new_state.move_hoyo(hoyo_index, new_pos)
        return new_state
