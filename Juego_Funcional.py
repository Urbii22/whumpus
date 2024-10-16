import random
import math
from copy import deepcopy
from typing import List, Tuple, Union

# Definición de los elementos como números
BLANCO = 0
AGENTE = 1
HOYO = 2
WUMPUS = 3
ORO = 4
HEDOR = 5
BRISA = 6
BRISA_HEDOR = 9
BRISA_ORO = 8
HEDOR_ORO = 7
BRISA_HEDOR_ORO = 10  # Añadido para manejar combinaciones

# Definición de movimientos para facilitar la referencia
MOVE_UP = 'up'
MOVE_DOWN = 'down'
MOVE_LEFT = 'left'
MOVE_RIGHT = 'right'

class Tablerowumpus:

    def __init__(self, matrix: List[List[int]]):
        self.tamano = 6

        # Validar que la matriz tenga el tamaño correcto
        if not self.es_matriz_valida(matrix):
            raise ValueError(f"La matriz proporcionada debe ser de tamaño {self.tamano}x{self.tamano}.")

        self.matrix = deepcopy(matrix)
        self.pos_agente = (5, 0)  # Posición fija del agente

        # Colocar el agente en la matriz
        self.placeTile(self.pos_agente[0], self.pos_agente[1], AGENTE)

        # Inicializar atributos para posiciones clave
        self.pos_wumpus = None
        self.pos_oro = None
        self.pos_hoyos = []

        # Colocar los demás elementos del juego
        self.colocar_elementos()

        # Variables para indicar si el juego ha terminado y el resultado
        self.game_over = False
        self.game_result = None  # Puede ser 'win', 'lose_wumpus', 'lose_hoyo'

    def __eq__(self, other) -> bool:
        for i in range(self.tamano):
            for j in range(self.tamano):
                if self.matrix[i][j] != other.matrix[i][j]:
                    return False
        return True

    def setMatrix(self, matrix: List[List[int]]):
        if not self.es_matriz_valida(matrix):
            raise ValueError(f"La matriz proporcionada debe ser de tamaño {self.tamano}x{self.tamano}.")
        self.matrix = deepcopy(matrix)

    def getMatrix(self) -> List[List[int]]:
        return deepcopy(self.matrix)

    def placeTile(self, row: int, col: int, tile: int):
        if 0 <= row < self.tamano and 0 <= col < self.tamano:
            self.matrix[row][col] = tile
        else:
            raise IndexError(f"Las coordenadas ({row}, {col}) están fuera de los límites del tablero.")

    def colocar_elementos(self):
        posiciones_disponibles = [(i, j) for i in range(self.tamano) for j in range(self.tamano)]
        # Remover la posición del agente de las disponibles
        if self.pos_agente in posiciones_disponibles:
            posiciones_disponibles.remove(self.pos_agente)

        # Colocar el Wumpus
        wumpus_pos = random.choice(posiciones_disponibles)
        self.placeTile(wumpus_pos[0], wumpus_pos[1], WUMPUS)
        posiciones_disponibles.remove(wumpus_pos)
        self.pos_wumpus = wumpus_pos  # Almacenar la posición del Wumpus

        # Colocar el oro asegurando que no esté adyacente al agente
        posiciones_no_adyacentes = [pos for pos in posiciones_disponibles if
                                     not self.es_adyacente(pos, self.pos_agente)]
        if not posiciones_no_adyacentes:
            raise ValueError("No hay posiciones disponibles para colocar el oro que no estén adyacentes al agente.")
        oro_pos = random.choice(posiciones_no_adyacentes)
        self.placeTile(oro_pos[0], oro_pos[1], ORO)
        posiciones_disponibles.remove(oro_pos)
        self.pos_oro = oro_pos  # Almacenar la posición del Oro

        # Colocar los 2 huecos
        if len(posiciones_disponibles) < 2:
            raise ValueError("No hay suficientes posiciones disponibles para colocar los huecos.")
        hoyos_pos1 = random.choice(posiciones_disponibles)
        self.placeTile(hoyos_pos1[0], hoyos_pos1[1], HOYO)
        posiciones_disponibles.remove(hoyos_pos1)

        hoyos_pos2 = random.choice(posiciones_disponibles)
        self.placeTile(hoyos_pos2[0], hoyos_pos2[1], HOYO)
        posiciones_disponibles.remove(hoyos_pos2)
        self.pos_hoyos = [hoyos_pos1, hoyos_pos2]  # Almacenar las posiciones de los Huecos

        # Colocar casillas de hedor alrededor del Wumpus
        vecinos_wumpus = self.obtener_vecinos(wumpus_pos)
        for vec in vecinos_wumpus:
            if self.matrix[vec[0]][vec[1]] == BLANCO:
                self.placeTile(vec[0], vec[1], HEDOR)
            elif self.matrix[vec[0]][vec[1]] == ORO:
                self.placeTile(vec[0], vec[1], HEDOR_ORO)

        # Colocar casillas de brisa alrededor de los huecos
        for hoyo_pos in [hoyos_pos1, hoyos_pos2]:
            vecinos_hoyo = self.obtener_vecinos(hoyo_pos)
            for vec in vecinos_hoyo:
                if self.matrix[vec[0]][vec[1]] == BLANCO:
                    self.placeTile(vec[0], vec[1], BRISA)
                elif self.matrix[vec[0]][vec[1]] == HEDOR:
                    self.placeTile(vec[0], vec[1], BRISA_HEDOR)
                elif self.matrix[vec[0]][vec[1]] == ORO:
                    self.placeTile(vec[0], vec[1], BRISA_ORO)
                elif self.matrix[vec[0]][vec[1]] == HEDOR_ORO:
                    self.placeTile(vec[0], vec[1], BRISA_HEDOR_ORO)

    def es_matriz_valida(self, matrix: List[List[int]]) -> bool:
        if len(matrix) != self.tamano:
            return False
        for fila in matrix:
            if len(fila) != self.tamano:
                return False
            for casilla in fila:
                if casilla not in {BLANCO, AGENTE, HOYO, WUMPUS, ORO, HEDOR, BRISA, BRISA_HEDOR, BRISA_ORO, HEDOR_ORO, BRISA_HEDOR_ORO}:
                    return False
        return True

    def es_adyacente(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1

    def obtener_vecinos(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        i, j = pos
        vecinos = []
        posibles = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
        for x, y in posibles:
            if 0 <= x < self.tamano and 0 <= y < self.tamano:
                vecinos.append((x, y))
        return vecinos

    def utility(self) -> float:
        posAgente = list(self.pos_agente)
        posOro = list(self.pos_oro)

        distancia = math.sqrt((posOro[0] - posAgente[0]) ** 2 + (posOro[1] - posAgente[1]) ** 2)

        # Obtener los vecinos del agente
        vecinos_agente = self.obtener_vecinos(tuple(posAgente))

        # Contar las casillas de penalización
        contador_penalizaciones = {
            HEDOR: 0,
            BRISA: 0,
            BRISA_HEDOR: 0,
            BRISA_ORO: 0,
            HEDOR_ORO: 0,
            BRISA_HEDOR_ORO: 0
        }

        for vec in vecinos_agente:
            tile = self.matrix[vec[0]][vec[1]]
            if tile in contador_penalizaciones:
                contador_penalizaciones[tile] += 1

        # Definir pesos de penalización
        pesos_penalizacion = {
            HEDOR: 0.1,
            BRISA: 0.1,
            BRISA_HEDOR: 0.2,
            BRISA_ORO: 0.15,
            HEDOR_ORO: 0.15,
            BRISA_HEDOR_ORO: 0.25
        }

        # Calcular penalización total
        penalizacion_total = 0.0
        for tile, count in contador_penalizaciones.items():
            penalizacion_total += pesos_penalizacion.get(tile, 0) * count

        # Calcular la utilidad final
        utilidad = (1 / (distancia + 1e-2)) - penalizacion_total

        return utilidad

    def imprimir_tablero(self):
        for fila in self.matrix:
            print(' '.join(str(casilla) for casilla in fila))
        print()

    # ================================
    # Métodos de Movimiento
    # ================================

    def canMoveUp(self, row: int, col: int) -> bool:
        new_row = row - 1
        if new_row < 0:
            return False
        return True

    def canMoveDown(self, row: int, col: int) -> bool:
        new_row = row + 1
        if new_row >= self.tamano:
            return False
        return True

    def canMoveLeft(self, row: int, col: int) -> bool:
        new_col = col - 1
        if new_col < 0:
            return False
        return True

    def canMoveRight(self, row: int, col: int) -> bool:
        new_col = col + 1
        if new_col >= self.tamano:
            return False
        return True

    def getAvailableMovesForMax(self, row: int, col: int) -> List[str]:
        moves = []
        if self.canMoveUp(row, col):
            moves.append(MOVE_UP)
        if self.canMoveDown(row, col):
            moves.append(MOVE_DOWN)
        if self.canMoveLeft(row, col):
            moves.append(MOVE_LEFT)
        if self.canMoveRight(row, col):
            moves.append(MOVE_RIGHT)
        return moves

    def getAvailableMovesForMin(self) -> List[Tuple[int, int, int]]:
        """
        Retorna una lista de movimientos disponibles para los hoyos.
        Cada movimiento es una tupla (hoyo_index, new_row, new_col).
        """
        moves = []
        for hoyo_index, hoyo_pos in enumerate(self.pos_hoyos):
            vecinos = self.obtener_vecinos(hoyo_pos)
            for vec in vecinos:
                if self.canMoveHoyo(hoyo_index, vec[0], vec[1]):
                    moves.append((hoyo_index, vec[0], vec[1]))
        return moves

    def up(self, row: int, col: int):
        if not self.canMoveUp(row, col):
            return
        new_row, new_col = row - 1, col
        self.mover_agente(row, col, new_row, new_col)
        self.verificar_estado_juego(new_row, new_col)

    def down(self, row: int, col: int):
        if not self.canMoveDown(row, col):
            return
        new_row, new_col = row + 1, col
        self.mover_agente(row, col, new_row, new_col)
        self.verificar_estado_juego(new_row, new_col)

    def left(self, row: int, col: int):
        if not self.canMoveLeft(row, col):
            return
        new_row, new_col = row, col - 1
        self.mover_agente(row, col, new_row, new_col)
        self.verificar_estado_juego(new_row, new_col)

    def right(self, row: int, col: int):
        if not self.canMoveRight(row, col):
            return
        new_row, new_col = row, col + 1
        self.mover_agente(row, col, new_row, new_col)
        self.verificar_estado_juego(new_row, new_col)

    def mover_agente(self, old_row: int, old_col: int, new_row: int, new_col: int):
        # Retornar la casilla antigua a su estado original (BLANCO o lo que corresponda)
        self.placeTile(old_row, old_col, BLANCO)

        # Actualizar la posición del agente
        self.pos_agente = (new_row, new_col)

        # Colocar el agente en la nueva posición
        self.placeTile(new_row, new_col, AGENTE)

    def verificar_estado_juego(self, row: int, col: int):
        agente_pos = (row, col)

        # Verificar si el agente está en la misma posición que el oro
        if agente_pos == self.pos_oro:
            self.game_over = True
            self.game_result = 'win'
            return

        # Verificar si el agente está en la misma posición que el Wumpus
        if agente_pos == self.pos_wumpus:
            self.game_over = True
            self.game_result = 'lose_wumpus'
            return

        # Verificar si el agente está en una posición de hoyo
        if agente_pos in self.pos_hoyos:
            self.game_over = True
            self.game_result = 'lose_hoyo'
            return

    def isGameOver(self) -> bool:
        return self.game_over

    def canMoveHoyo(self, hoyo_index: int, new_row: int, new_col: int) -> bool:
        if 0 <= new_row < self.tamano and 0 <= new_col < self.tamano:
            if self.matrix[new_row][new_col] == BLANCO:
                return True
        return False

    def mover_hoyo(self, hoyo_index: int, new_row: int, new_col: int):
        old_row, old_col = self.pos_hoyos[hoyo_index]
        # Eliminar el hoyo de la posición actual
        self.placeTile(old_row, old_col, BLANCO)

        # Actualizar las brisas antiguas
        vecinos_antiguos = self.obtener_vecinos((old_row, old_col))
        for vec in vecinos_antiguos:
            tile = self.matrix[vec[0]][vec[1]]
            if tile == BRISA:
                self.placeTile(vec[0], vec[1], BLANCO)
            elif tile == BRISA_HEDOR:
                self.placeTile(vec[0], vec[1], HEDOR)
            elif tile == BRISA_ORO:
                self.placeTile(vec[0], vec[1], ORO)
            elif tile == BRISA_HEDOR_ORO:
                self.placeTile(vec[0], vec[1], HEDOR_ORO)

        # Colocar el hoyo en la nueva posición
        self.placeTile(new_row, new_col, HOYO)
        self.pos_hoyos[hoyo_index] = (new_row, new_col)

        # Actualizar las brisas nuevas
        vecinos_nuevos = self.obtener_vecinos((new_row, new_col))
        for vec in vecinos_nuevos:
            tile = self.matrix[vec[0]][vec[1]]
            if tile == BLANCO:
                self.placeTile(vec[0], vec[1], BRISA)
            elif tile == HEDOR:
                self.placeTile(vec[0], vec[1], BRISA_HEDOR)
            elif tile == ORO:
                self.placeTile(vec[0], vec[1], BRISA_ORO)
            elif tile == HEDOR_ORO:
                self.placeTile(vec[0], vec[1], BRISA_HEDOR_ORO)

    def moveCanBeMade(self, player: int) -> bool:
        if player == 1:  # Max (Agente)
            moves = self.getAvailableMovesForMax(*self.pos_agente)
            return len(moves) > 0
        else:  # Min (Hoyos)
            for hoyo_index, hoyo_pos in enumerate(self.pos_hoyos):
                vecinos = self.obtener_vecinos(hoyo_pos)
                for vec in vecinos:
                    if self.canMoveHoyo(hoyo_index, vec[0], vec[1]):
                        return True
            return False

# ================================
# Implementación de la función miniMax
# ================================

def miniMax(state: Tablerowumpus, currentLevel: int, maxLevel: int, player: int, alpha: float, beta: float, stop: bool) -> Tuple[Tablerowumpus, float, bool]:
    # Verificar si el juego ha terminado o si se alcanzó el nivel máximo de profundidad
    if not state.moveCanBeMade(player) or currentLevel == maxLevel or state.isGameOver():
        return (state, state.utility(), stop)

    # Inicializar variables
    bestState = None

    if player == 1:  # Max (Agente)
        maxValue = -math.inf
        moves = state.getAvailableMovesForMax(*state.pos_agente)

        for move in moves:
            new_state = deepcopy(state)
            row, col = new_state.pos_agente
            if move == MOVE_UP:
                new_state.up(row, col)
            elif move == MOVE_DOWN:
                new_state.down(row, col)
            elif move == MOVE_LEFT:
                new_state.left(row, col)
            elif move == MOVE_RIGHT:
                new_state.right(row, col)

            # Llamada recursiva al siguiente nivel
            _, value, _ = miniMax(new_state, currentLevel + 1, maxLevel, 0, alpha, beta, stop)

            if value > maxValue:
                maxValue = value
                bestState = new_state

            alpha = max(alpha, maxValue)
            if beta <= alpha:
                break  # Poda beta

        return (bestState, maxValue, stop)
    else:  # Min (Hoyos)
        minValue = math.inf
        moves = state.getAvailableMovesForMin()

        for move in moves:
            hoyo_index, new_row, new_col = move
            new_state = deepcopy(state)
            new_state.mover_hoyo(hoyo_index, new_row, new_col)

            # Llamada recursiva al siguiente nivel
            _, value, _ = miniMax(new_state, currentLevel + 1, maxLevel, 1, alpha, beta, stop)

            if value < minValue:
                minValue = value
                bestState = new_state

            beta = min(beta, minValue)
            if beta <= alpha:
                break  # Poda alfa

        # Si no hay movimientos posibles para los hoyos, retornamos el estado actual
        if bestState is None:
            return (state, state.utility(), stop)

        return (bestState, minValue, stop)

# ================================
# Ejemplo de Uso
# ================================

if __name__ == "__main__":
    # Crear una matriz de 6x6 llena de BLANCO (0)
    matriz_inicial = [[BLANCO for _ in range(6)] for _ in range(6)]

    # Crear una instancia de Tablerowumpus pasando la matriz inicial
    tablero = Tablerowumpus(matriz_inicial)
    print("Tablero inicial:")
    tablero.imprimir_tablero()

    # Parámetros iniciales para la función miniMax
    currentLevel = 0
    maxLevel = 3  # Profundidad máxima del árbol de búsqueda
    player = 1  # Comienza el jugador Max (Agente)
    alpha = -math.inf
    beta = math.inf
    stop = False

    # Llamada a la función miniMax
    bestState, utilityValue, _ = miniMax(tablero, currentLevel, maxLevel, player, alpha, beta, stop)

    print("Mejor movimiento encontrado:")
    bestState.imprimir_tablero()
    print("Utilidad del mejor estado:", utilityValue)

    # Verificar si el juego ha terminado
    if bestState.isGameOver():
        print(f"Resultado del juego: {bestState.game_result}")
    else:
        print("El juego continúa.")
