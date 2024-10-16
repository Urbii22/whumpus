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

        # Opcional: Colocar casillas de hedor alrededor del Wumpus
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

    def es_matriz_valida(self, matrix: List[List[int]]) -> bool:
        if len(matrix) != self.tamano:
            return False
        for fila in matrix:
            if len(fila) != self.tamano:
                return False
            for casilla in fila:
                if casilla not in {BLANCO, AGENTE, HOYO, WUMPUS, ORO, HEDOR, BRISA, BRISA_HEDOR, BRISA_ORO, HEDOR_ORO}:
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
        alto = len(self.matrix)
        ancho = len(self.matrix[0])

        distancia = math.sqrt((posOro[0] - posAgente[0]) ** 2 + (posOro[1] - posAgente[1]) ** 2)
        print(f"Distancia Euclidiana entre Agente y Oro: {distancia}")

        # Obtener los vecinos del agente
        vecinos_agente = self.obtener_vecinos(tuple(posAgente))
        print(f"Vecinos del Agente: {vecinos_agente}")

        # Contar las casillas de penalización
        contador_penalizaciones = {
            HEDOR: 0,
            BRISA: 0,
            BRISA_HEDOR: 0,
            BRISA_ORO: 0,
            HEDOR_ORO: 0
        }

        for vec in vecinos_agente:
            tile = self.matrix[vec[0]][vec[1]]
            if tile in contador_penalizaciones:
                contador_penalizaciones[tile] += 1

        print("Conteo de casillas de penalización cerca del Agente:", contador_penalizaciones)

        # Definir pesos de penalización
        pesos_penalizacion = {
            HEDOR: 0.1,
            BRISA: 0.1,
            BRISA_HEDOR: 0.2,
            BRISA_ORO: 0.15,
            HEDOR_ORO: 0.15
        }

        # Calcular penalización total
        penalizacion_total = 0.0
        for tile, count in contador_penalizaciones.items():
            penalizacion_total += pesos_penalizacion.get(tile, 0) * count

        print(f"Penalización Total: {penalizacion_total}")

        # Calcular la utilidad final
        utilidad = (1 / (distancia + 1e-2)) - penalizacion_total
        print(f"Utilidad Calculada: {utilidad}")

        return utilidad

    def imprimir_tablero(self):
        for fila in self.matrix:
            print(' '.join(str(casilla) for casilla in fila))
        print()

    # ================================
    # Métodos de Movimiento
    # ================================

    def canMoveUp(self, row: int, col: int) -> bool:
        """
        Comprueba si el agente puede moverse hacia arriba desde (row, col).
        Solo verifica los límites del tablero.
        """
        new_row, new_col = row - 1, col
        if new_row < 0:
            print(f"No se puede mover hacia arriba desde ({row}, {col}): fuera de los límites.")
            return False
        return True

    def canMoveDown(self, row: int, col: int) -> bool:
        """
        Comprueba si el agente puede moverse hacia abajo desde (row, col).
        Solo verifica los límites del tablero.
        """
        new_row, new_col = row + 1, col
        if new_row >= self.tamano:
            print(f"No se puede mover hacia abajo desde ({row}, {col}): fuera de los límites.")
            return False
        return True

    def canMoveLeft(self, row: int, col: int) -> bool:
        """
        Comprueba si el agente puede moverse hacia la izquierda desde (row, col).
        Solo verifica los límites del tablero.
        """
        new_row, new_col = row, col - 1
        if new_col < 0:
            print(f"No se puede mover hacia la izquierda desde ({row}, {col}): fuera de los límites.")
            return False
        return True

    def canMoveRight(self, row: int, col: int) -> bool:
        """
        Comprueba si el agente puede moverse hacia la derecha desde (row, col).
        Solo verifica los límites del tablero.
        """
        new_row, new_col = row, col + 1
        if new_col >= self.tamano:
            print(f"No se puede mover hacia la derecha desde ({row}, {col}): fuera de los límites.")
            return False
        return True

    def getAvailableMovesForMax(self, row: int, col: int) -> List[str]:
        """
        Retorna una lista de movimientos disponibles para el jugador maximizar.
        """
        moves = []
        if self.canMoveUp(row, col):
            moves.append(MOVE_UP)
            print(f"Movimiento 'up' disponible desde ({row}, {col}).")
        if self.canMoveDown(row, col):
            moves.append(MOVE_DOWN)
            print(f"Movimiento 'down' disponible desde ({row}, {col}).")
        if self.canMoveLeft(row, col):
            moves.append(MOVE_LEFT)
            print(f"Movimiento 'left' disponible desde ({row}, {col}).")
        if self.canMoveRight(row, col):
            moves.append(MOVE_RIGHT)
            print(f"Movimiento 'right' disponible desde ({row}, {col}).")
        return moves

    def getAvailableMovesForMin(self) -> List[Tuple[int, int]]:
        """
        Retorna una lista de posiciones disponibles para el jugador minimizar.
        (En el contexto de Wumpus, esto podría no tener sentido a menos que haya un adversario.
        Podría necesitar ajuste según la lógica del juego.)
        """
        # Como Wumpus es estático en esta implementación, asumiremos que no hay movimientos para el "min".
        # Si se desea que el Wumpus se mueva, se debería implementar aquí.
        # Por ahora, retornamos una lista vacía.
        return []

    def up(self, row: int, col: int):
        """
        Realiza el movimiento hacia arriba.
        """
        if not self.canMoveUp(row, col):
            print(f"No se puede mover hacia arriba desde ({row}, {col}).")
            return
        new_row, new_col = row - 1, col
        self.mover_agente(row, col, new_row, new_col)
        print(f"Movimiento hacia arriba realizado: ({row}, {col}) -> ({new_row}, {new_col}).")
        self.verificar_estado_juego(new_row, new_col)

    def down(self, row: int, col: int):
        """
        Realiza el movimiento hacia abajo.
        """
        if not self.canMoveDown(row, col):
            print(f"No se puede mover hacia abajo desde ({row}, {col}).")
            return
        new_row, new_col = row + 1, col
        self.mover_agente(row, col, new_row, new_col)
        print(f"Movimiento hacia abajo realizado: ({row}, {col}) -> ({new_row}, {new_col}).")
        self.verificar_estado_juego(new_row, new_col)

    def left(self, row: int, col: int):
        """
        Realiza el movimiento hacia la izquierda.
        """
        if not self.canMoveLeft(row, col):
            print(f"No se puede mover hacia la izquierda desde ({row}, {col}).")
            return
        new_row, new_col = row, col - 1
        self.mover_agente(row, col, new_row, new_col)
        print(f"Movimiento hacia la izquierda realizado: ({row}, {col}) -> ({new_row}, {new_col}).")
        self.verificar_estado_juego(new_row, new_col)

    def right(self, row: int, col: int):
        """
        Realiza el movimiento hacia la derecha.
        """
        if not self.canMoveRight(row, col):
            print(f"No se puede mover hacia la derecha desde ({row}, {col}).")
            return
        new_row, new_col = row, col + 1
        self.mover_agente(row, col, new_row, new_col)
        print(f"Movimiento hacia la derecha realizado: ({row}, {col}) -> ({new_row}, {new_col}).")
        self.verificar_estado_juego(new_row, new_col)

    def mover_agente(self, old_row: int, old_col: int, new_row: int, new_col: int):
        """
        Mueve al agente de (old_row, old_col) a (new_row, new_col).
        """
        # Retornar la casilla antigua a BLANCO
        self.placeTile(old_row, old_col, BLANCO)

        # Actualizar la posición del agente
        self.pos_agente = (new_row, new_col)

        # Colocar el agente en la nueva posición
        self.placeTile(new_row, new_col, AGENTE)

    def verificar_estado_juego(self, row: int, col: int):
        """
        Verifica si el juego ha terminado después de un movimiento.
        """
        agente_pos = (row, col)

        # Verificar si el agente está en la misma posición que el oro
        if agente_pos == self.pos_oro:
            print("¡El agente ha encontrado el oro! Has ganado.")
            self.game_over = True
            self.game_result = 'win'
            return

        # Verificar si el agente está en la misma posición que el Wumpus
        if agente_pos == self.pos_wumpus:
            print("¡El agente ha sido devorado por el Wumpus! Has perdido.")
            self.game_over = True
            self.game_result = 'lose_wumpus'
            return

        # Verificar si el agente está en una posición de hoyo
        if agente_pos in self.pos_hoyos:
            print("¡El agente ha caído en un hoyo! Has perdido.")
            self.game_over = True
            self.game_result = 'lose_hoyo'
            return

    def isGameOver(self) -> bool:
        """
        Retorna True si el juego ha terminado, de lo contrario False.
        """
        return self.game_over

    # ====================================================
    #
    # TODO: Implementar cualquier otro método necesario
    #
    # ====================================================

# ================================
# Ejemplo de Uso
# ================================

if __name__ == "__main__":
    # Crear una matriz de 6x6 llena de BLANCO (0)
    matriz_inicial = [[BLANCO for _ in range(6)] for _ in range(6)]

    # Crear una instancia de Tablerowumpus pasando la matriz inicial
    tablero = Tablerowumpus(matriz_inicial)
    tablero.imprimir_tablero()
    print("Utilidad del tablero:", tablero.utility())

    # Obtener la posición actual del agente
    agente_pos = tablero.pos_agente
    row, col = agente_pos

    # Obtener movimientos disponibles para Max (agente)
    movimientos_disponibles = tablero.getAvailableMovesForMax(row, col)
    print("Movimientos disponibles para el agente:", movimientos_disponibles)

    # Realizar un movimiento (ejemplo: mover hacia la derecha si está disponible)
    if MOVE_RIGHT in movimientos_disponibles:
        tablero.right(row, col)
        tablero.imprimir_tablero()
        print("Utilidad del tablero después del movimiento:", tablero.utility())

    # Verificar si el juego ha terminado
    if tablero.isGameOver():
        print(f"Resultado del juego: {tablero.game_result}")
    else:
        print("El juego continúa.")

    # Realizar más movimientos según sea necesario
    # Puedes añadir más lógica aquí para simular múltiples movimientos
