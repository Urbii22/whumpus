import random
import math
import tkinter as tk
from tkinter import messagebox
from copy import deepcopy
from typing import List, Tuple
import argparse

# Definición de constantes para representar los elementos del juego
BLANCO = 0               # Casilla vacía
AGENTE = 1               # Posición del agente
HOYO = 2                 # Hoyo mortal
WUMPUS = 3               # Monstruo Wumpus
ORO = 4                  # Oro a recolectar
HEDOR = 5                # Indica que el Wumpus está cerca
BRISA = 6                # Indica que un hoyo está cerca
HEDOR_ORO = 7            # Casilla con hedor y oro
BRISA_ORO = 8            # Casilla con brisa y oro
BRISA_HEDOR = 9          # Casilla con brisa y hedor
BRISA_HEDOR_ORO = 10     # Casilla con brisa, hedor y oro (combinaciones adicionales)

# Definición de movimientos posibles
MOVE_UP = 'up'
MOVE_DOWN = 'down'
MOVE_LEFT = 'left'
MOVE_RIGHT = 'right'


class Tablerowumpus:
    """
    Clase que representa el tablero del juego del Wumpus.
    """

    def __init__(self, matrix: List[List[int]]):
        self.tamano = 6  # Tamaño del tablero (6x6)

        # Validar que la matriz tenga el tamaño correcto
        if not self.es_matriz_valida(matrix):
            raise ValueError(f"La matriz proporcionada debe ser de tamaño {self.tamano}x{self.tamano}.")

        # Crear una copia profunda de la matriz inicial
        self.matrix = deepcopy(matrix)
        self.pos_agente = (5, 0)  # Posición inicial fija del agente en la esquina inferior izquierda
        self.previous_pos = None  # Nueva línea para rastrear la posición anterior

        # Colocar el agente en la matriz
        self.placeTile(self.pos_agente[0], self.pos_agente[1], AGENTE)

        # Inicializar atributos para posiciones clave
        self.pos_wumpus = None
        self.pos_oro = None
        self.pos_hoyos = []

        # Colocar los demás elementos del juego (Wumpus, oro, hoyos, brisas y hedores)
        self.colocar_elementos()

        # Variables para indicar si el juego ha terminado y el resultado
        self.game_over = False
        self.game_result = None  # Puede ser 'win', 'lose_wumpus' o 'lose_hoyo'

    def __eq__(self, other) -> bool:
        """
        Método para comparar dos tableros y verificar si son iguales.
        """
        for i in range(self.tamano):
            for j in range(self.tamano):
                if self.matrix[i][j] != other.matrix[i][j]:
                    return False
        return True

    def setMatrix(self, matrix: List[List[int]]):
        """
        Establece una nueva matriz para el tablero, después de validar su tamaño.
        """
        if not self.es_matriz_valida(matrix):
            raise ValueError(f"La matriz proporcionada debe ser de tamaño {self.tamano}x{self.tamano}.")
        self.matrix = deepcopy(matrix)

    def getMatrix(self) -> List[List[int]]:
        """
        Retorna una copia profunda de la matriz actual del tablero.
        """
        return deepcopy(self.matrix)

    def placeTile(self, row: int, col: int, tile: int):
        """
        Coloca un elemento específico en una posición del tablero.
        """
        if 0 <= row < self.tamano and 0 <= col < self.tamano:
            self.matrix[row][col] = tile
        else:
            raise IndexError(f"Las coordenadas ({row}, {col}) están fuera de los límites del tablero.")

    def colocar_elementos(self):
        """
        Coloca el Wumpus, el oro y los hoyos en el tablero de manera aleatoria,
        asegurándose de que cumplan con las restricciones del juego.
        """
        # Generar todas las posiciones disponibles en el tablero
        posiciones_disponibles = [(i, j) for i in range(self.tamano) for j in range(self.tamano)]
        # Remover la posición del agente de las disponibles
        if self.pos_agente in posiciones_disponibles:
            posiciones_disponibles.remove(self.pos_agente)

        # Colocar el Wumpus en una posición aleatoria
        wumpus_pos = random.choice(posiciones_disponibles)
        self.placeTile(wumpus_pos[0], wumpus_pos[1], WUMPUS)
        posiciones_disponibles.remove(wumpus_pos)
        self.pos_wumpus = wumpus_pos  # Almacenar la posición del Wumpus

        # Colocar el oro, asegurando que no esté adyacente al agente
        posiciones_no_adyacentes = [pos for pos in posiciones_disponibles if
                                     not self.es_adyacente(pos, self.pos_agente)]
        if not posiciones_no_adyacentes:
            raise ValueError("No hay posiciones disponibles para colocar el oro que no estén adyacentes al agente.")
        oro_pos = random.choice(posiciones_no_adyacentes)
        self.placeTile(oro_pos[0], oro_pos[1], ORO)
        posiciones_disponibles.remove(oro_pos)
        self.pos_oro = oro_pos  # Almacenar la posición del oro

        # Colocar dos hoyos, asegurando que no estén adyacentes al agente
        if len(posiciones_disponibles) < 2:
            raise ValueError("No hay suficientes posiciones disponibles para colocar los hoyos.")

        # Excluir posiciones adyacentes al agente para los hoyos
        posiciones_para_hoyos = [pos for pos in posiciones_disponibles if not self.es_adyacente(pos, self.pos_agente)]
        if len(posiciones_para_hoyos) < 2:
            raise ValueError("No hay suficientes posiciones disponibles para colocar los hoyos sin estar adyacentes al agente.")

        # Colocar el primer hoyo
        hoyos_pos1 = random.choice(posiciones_para_hoyos)
        self.placeTile(hoyos_pos1[0], hoyos_pos1[1], HOYO)
        posiciones_disponibles.remove(hoyos_pos1)
        posiciones_para_hoyos.remove(hoyos_pos1)

        # Colocar el segundo hoyo
        hoyos_pos2 = random.choice(posiciones_para_hoyos)
        self.placeTile(hoyos_pos2[0], hoyos_pos2[1], HOYO)
        posiciones_disponibles.remove(hoyos_pos2)
        self.pos_hoyos = [hoyos_pos1, hoyos_pos2]  # Almacenar las posiciones de los hoyos

        # Colocar casillas de hedor alrededor del Wumpus
        vecinos_wumpus = self.obtener_vecinos(wumpus_pos)
        for vec in vecinos_wumpus:
            if self.matrix[vec[0]][vec[1]] == BLANCO:
                self.placeTile(vec[0], vec[1], HEDOR)
            elif self.matrix[vec[0]][vec[1]] == ORO:
                self.placeTile(vec[0], vec[1], HEDOR_ORO)

        # Colocar casillas de brisa alrededor de los hoyos
        for hoyo_pos in self.pos_hoyos:
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
        """
        Verifica si la matriz proporcionada es válida (tamaño correcto y valores permitidos).
        """
        if len(matrix) != self.tamano:
            return False
        for fila in matrix:
            if len(fila) != self.tamano:
                return False
            for casilla in fila:
                if casilla not in {BLANCO, AGENTE, HOYO, WUMPUS, ORO, HEDOR, BRISA, BRISA_HEDOR, BRISA_ORO, HEDOR_ORO,
                                   BRISA_HEDOR_ORO}:
                    return False
        return True

    def es_adyacente(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """
        Verifica si dos posiciones en el tablero son adyacentes (arriba, abajo, izquierda, derecha).
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1

    def obtener_vecinos(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Obtiene una lista de posiciones adyacentes válidas a una posición dada.
        """
        i, j = pos
        vecinos = []
        posibles = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
        for x, y in posibles:
            if 0 <= x < self.tamano and 0 <= y < self.tamano:
                vecinos.append((x, y))
        return vecinos

    def utility(self, currentLevel: int) -> float:

        posAgente = list(self.pos_agente)
        posOro = list(self.pos_oro) if self.pos_oro else [0, 0]  # Manejar pos_oro=None

        if self.pos_oro:
            distancia = math.sqrt((posOro[0] - posAgente[0]) ** 2 + (posOro[1] - posAgente[1]) ** 2)
        else:
            distancia = 0  # Cuando el oro ya ha sido recolectado

        # Obtener los vecinos del agente
        vecinos_agente = self.obtener_vecinos(tuple(posAgente))

        # Contar las casillas de penalización
        contador_penalizaciones = {
            HEDOR: 0,
            BRISA: 0,
            BRISA_HEDOR: 0,
            BRISA_ORO: 0,
            HEDOR_ORO: 0,
            BRISA_HEDOR_ORO: 0,
            HOYO: 0,
            WUMPUS: 0
        }

        for vec in vecinos_agente:
            tile = self.matrix[vec[0]][vec[1]]
            if tile in contador_penalizaciones:
                contador_penalizaciones[tile] += 1

        # Definir pesos de penalización (valores POSITIVOS ahora)
        pesos_penalizacion = {
            HEDOR: 0.2,            # Penalización por hedor
            BRISA: 0.2,            # Penalización por brisa
            BRISA_HEDOR: 0.5,      # Penalización por combinación de brisa y hedor
            BRISA_ORO: 2,          # Penalización menor si hay oro
            HEDOR_ORO: 2,          # Penalización menor si hay oro
            BRISA_HEDOR_ORO: 0.05, # Penalización menor si hay oro
        }

        # Calcular penalización total
        penalizacion_total = 0.0
        for tile, count in contador_penalizaciones.items():
            penalizacion_total += pesos_penalizacion.get(tile, 0) * count

        # Agregar penalización por profundidad (costo por movimiento)
        costo_por_movimiento = 0.1 * currentLevel

        # Calcular la utilidad final
        utilidad = (1 / (distancia + 1e-2)) - penalizacion_total - costo_por_movimiento

        return utilidad

    def imprimir_tablero(self):
        """
        Imprime el tablero en la consola con símbolos representativos.
        """
        tile_symbols = {
            BLANCO: '  ',
            AGENTE: 'A ',
            HOYO: 'H ',
            WUMPUS: 'W ',
            ORO: 'O ',
            HEDOR: 'He',
            BRISA: 'B ',
            BRISA_HEDOR: 'BH',
            BRISA_ORO: 'BO',
            HEDOR_ORO: 'HO',
            BRISA_HEDOR_ORO: 'BHO'
        }
        print("-" * (self.tamano * 4 + 1))
        for fila in self.matrix:
            print("|", end="")
            for casilla in fila:
                symbol = tile_symbols.get(casilla, '??')
                print(f" {symbol}|", end="")
            print()
            print("-" * (self.tamano * 4 + 1))
        print()

    # ================================
    # Métodos de Movimiento del Agente
    # ================================

    def canMoveUp(self, row: int, col: int) -> bool:
        """
        Verifica si el agente puede moverse hacia arriba desde su posición actual.
        """
        new_row = row - 1
        if new_row < 0:
            return False
        return True

    def canMoveDown(self, row: int, col: int) -> bool:
        """
        Verifica si el agente puede moverse hacia abajo desde su posición actual.
        """
        new_row = row + 1
        if new_row >= self.tamano:
            return False
        return True

    def canMoveLeft(self, row: int, col: int) -> bool:
        """
        Verifica si el agente puede moverse hacia la izquierda desde su posición actual.
        """
        new_col = col - 1
        if new_col < 0:
            return False
        return True

    def canMoveRight(self, row: int, col: int) -> bool:
        """
        Verifica si el agente puede moverse hacia la derecha desde su posición actual.
        """
        new_col = col + 1
        if new_col >= self.tamano:
            return False
        return True

    def getAvailableMovesForMax(self, row: int, col: int) -> List[str]:
        """
        Obtiene una lista de movimientos disponibles para el agente (Max) desde su posición actual,
        excluyendo el movimiento que llevaría al agente de vuelta a la posición anterior.
        """
        moves = []
        if self.canMoveUp(row, col):
            new_pos = (row - 1, col)
            if new_pos != self.previous_pos:
                moves.append(MOVE_UP)
        if self.canMoveDown(row, col):
            new_pos = (row + 1, col)
            if new_pos != self.previous_pos:
                moves.append(MOVE_DOWN)
        if self.canMoveLeft(row, col):
            new_pos = (row, col - 1)
            if new_pos != self.previous_pos:
                moves.append(MOVE_LEFT)
        if self.canMoveRight(row, col):
            new_pos = (row, col + 1)
            if new_pos != self.previous_pos:
                moves.append(MOVE_RIGHT)
        return moves

    def getAvailableMovesForMin(self) -> List[Tuple[int, int, int]]:
        """
        Retorna una lista de movimientos disponibles para los hoyos (Min).
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
        """
        Mueve el agente hacia arriba si es posible y verifica el estado del juego.
        """
        if not self.canMoveUp(row, col):
            return
        new_row, new_col = row - 1, col
        self.mover_agente(row, col, new_row, new_col)
        self.verificar_estado_juego(new_row, new_col)

    def down(self, row: int, col: int):
        """
        Mueve el agente hacia abajo si es posible y verifica el estado del juego.
        """
        if not self.canMoveDown(row, col):
            return
        new_row, new_col = row + 1, col
        self.mover_agente(row, col, new_row, new_col)
        self.verificar_estado_juego(new_row, new_col)

    def left(self, row: int, col: int):
        """
        Mueve el agente hacia la izquierda si es posible y verifica el estado del juego.
        """
        if not self.canMoveLeft(row, col):
            return
        new_row, new_col = row, col - 1
        self.mover_agente(row, col, new_row, new_col)
        self.verificar_estado_juego(new_row, new_col)

    def right(self, row: int, col: int):
        """
        Mueve el agente hacia la derecha si es posible y verifica el estado del juego.
        """
        if not self.canMoveRight(row, col):
            return
        new_row, new_col = row, col + 1
        self.mover_agente(row, col, new_row, new_col)
        self.verificar_estado_juego(new_row, new_col)

    def mover_agente(self, old_row: int, old_col: int, new_row: int, new_col: int):
        """
        Actualiza la posición del agente en el tablero, restaurando la casilla anterior y colocando el agente en la nueva.
        """
        # Actualizar la posición anterior
        self.previous_pos = (old_row, old_col)

        # Restaurar la casilla antigua a su estado original
        self.restore_tile(old_row, old_col)

        # Actualizar la posición del agente
        self.pos_agente = (new_row, new_col)

        # Colocar el agente en la nueva posición
        self.placeTile(new_row, new_col, AGENTE)

    def restore_tile(self, row: int, col: int):
        """
        Restaura una casilla después de que el agente se ha movido de ella,
        recalculando si debe contener brisa o hedor.
        """
        # Dejar la casilla en blanco inicialmente
        self.placeTile(row, col, BLANCO)

        # Recalcular brisas y hedores en los vecinos
        vecinos = self.obtener_vecinos((row, col))
        for vec in vecinos:
            tile = self.matrix[vec[0]][vec[1]]
            if tile == HOYO:
                # Si hay un hoyo adyacente, colocar brisa
                if self.matrix[row][col] == BLANCO:
                    self.placeTile(row, col, BRISA)
            elif tile == WUMPUS:
                # Si hay un Wumpus adyacente, colocar hedor
                if self.matrix[row][col] == BLANCO:
                    self.placeTile(row, col, HEDOR)
            elif tile == ORO:
                # Si hay oro adyacente, colocar indicación de oro con brisa si aplica
                if self.matrix[row][col] == BLANCO:
                    self.placeTile(row, col, BRISA_ORO)

    def verificar_estado_juego(self, row: int, col: int):
        """
        Verifica si el agente ha ganado o perdido después de un movimiento.
        """
        agente_pos = (row, col)

        # Verificar si el agente ha encontrado el oro
        if agente_pos == self.pos_oro:
            self.game_over = True
            self.game_result = 'win'
            self.pos_oro = None  # Actualizar pos_oro para indicar que el oro ha sido recolectado
            return

        # Verificar si el agente ha sido devorado por el Wumpus
        if agente_pos == self.pos_wumpus:
            self.game_over = True
            self.game_result = 'lose_wumpus'
            return

        # Verificar si el agente ha caído en un hoyo
        if agente_pos in self.pos_hoyos:
            self.game_over = True
            self.game_result = 'lose_hoyo'
            return

    def isGameOver(self) -> bool:
        """
        Verifica si el juego ha terminado.
        """
        return self.game_over

    def canMoveHoyo(self, hoyo_index: int, new_row: int, new_col: int) -> bool:
        """
        Verifica si un hoyo puede moverse a la posición (new_row, new_col).
        Los hoyos pueden moverse a casillas que sean BLANCO, BRISA, HEDOR o BRISA_HEDOR,
        pero no a casillas ocupadas por ORO, WUMPUS, AGENTE o combinaciones con ORO.
        """
        if 0 <= new_row < self.tamano and 0 <= new_col < self.tamano:
            tile = self.matrix[new_row][new_col]
            # Evitar mover a casillas prohibidas
            forbidden_tiles = {AGENTE, WUMPUS, ORO, BRISA_ORO, HEDOR_ORO, BRISA_HEDOR_ORO}
            if tile not in forbidden_tiles and tile in {BLANCO, BRISA, HEDOR, BRISA_HEDOR}:
                return True
        return False

    def mover_hoyo(self, hoyo_index: int, new_row: int, new_col: int):
        """
        Mueve un hoyo a una nueva posición y actualiza las brisas en el tablero.
        """
        old_row, old_col = self.pos_hoyos[hoyo_index]
        # Eliminar el hoyo de la posición actual
        self.placeTile(old_row, old_col, BLANCO)

        # Actualizar las brisas antiguas
        self.actualizar_brisa_al_eliminar_hoyo(old_row, old_col)

        # Colocar el hoyo en la nueva posición
        self.placeTile(new_row, new_col, HOYO)
        self.pos_hoyos[hoyo_index] = (new_row, new_col)

        # Actualizar las brisas nuevas
        self.actualizar_brisa_al_agregar_hoyo(new_row, new_col)

    def actualizar_brisa_al_eliminar_hoyo(self, row: int, col: int):
        """
        Actualiza las casillas de brisa alrededor de un hoyo que ha sido movido.
        """
        vecinos = self.obtener_vecinos((row, col))
        for vec in vecinos:
            tile = self.matrix[vec[0]][vec[1]]
            if tile == BRISA:
                self.placeTile(vec[0], vec[1], BLANCO)
            elif tile == BRISA_HEDOR:
                self.placeTile(vec[0], vec[1], HEDOR)
            elif tile == BRISA_ORO:
                self.placeTile(vec[0], vec[1], ORO)
            elif tile == BRISA_HEDOR_ORO:
                self.placeTile(vec[0], vec[1], HEDOR_ORO)

    def actualizar_brisa_al_agregar_hoyo(self, row: int, col: int):
        """
        Actualiza las casillas de brisa alrededor de un hoyo que ha sido colocado.
        """
        vecinos = self.obtener_vecinos((row, col))
        for vec in vecinos:
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
        """
        Verifica si el jugador (1: Agente, 0: Hoyos) puede realizar algún movimiento.
        """
        if player == 1:  # Max (Agente)
            moves = self.getAvailableMovesForMax(*self.pos_agente)
            return len(moves) > 0
        else:  # Min (Hoyos)
            moves = self.getAvailableMovesForMin()
            return len(moves) > 0


# ================================
# Implementación de la función MiniMax con poda alfa-beta
# ================================

def miniMax(state: Tablerowumpus, currentLevel: int, maxLevel: int, player: int, alpha: float, beta: float) -> Tuple[
    Tablerowumpus, float]:
    """
    Implementa el algoritmo MiniMax con poda alfa-beta para decidir el mejor movimiento.
    """
    # Verificar si el juego ha terminado o si se alcanzó la profundidad máxima
    if not state.moveCanBeMade(player) or currentLevel == maxLevel or state.isGameOver():
        return (state, state.utility(currentLevel))

    # Inicializar variables
    bestState = None

    if player == 1:  # Max (Agente)
        maxValue = -math.inf
        moves = state.getAvailableMovesForMax(*state.pos_agente)

        for move in moves:
            # Crear una copia del estado actual
            new_state = deepcopy(state)
            row, col = new_state.pos_agente
            # Realizar el movimiento correspondiente
            if move == MOVE_UP:
                new_state.up(row, col)
            elif move == MOVE_DOWN:
                new_state.down(row, col)
            elif move == MOVE_LEFT:
                new_state.left(row, col)
            elif move == MOVE_RIGHT:
                new_state.right(row, col)

            # Llamada recursiva al siguiente nivel
            _, value = miniMax(new_state, currentLevel + 1, maxLevel, 0, alpha, beta)

            # Actualizar el valor máximo y el mejor estado
            if value > maxValue:
                maxValue = value
                bestState = new_state

            # Actualizar alfa y verificar poda
            alpha = max(alpha, maxValue)
            if beta <= alpha:
                break  # Poda beta

        return (bestState, maxValue)
    else:  # Min (Hoyos)
        minValue = math.inf
        moves = state.getAvailableMovesForMin()

        for move in moves:
            hoyo_index, new_row, new_col = move
            new_state = deepcopy(state)
            new_state.mover_hoyo(hoyo_index, new_row, new_col)

            # Llamada recursiva al siguiente nivel
            _, value = miniMax(new_state, currentLevel + 1, maxLevel, 1, alpha, beta)

            # Actualizar el valor mínimo y el mejor estado
            if value < minValue:
                minValue = value
                bestState = new_state

            # Actualizar beta y verificar poda
            beta = min(beta, minValue)
            if beta <= alpha:
                break  # Poda alfa

        # Si no hay movimientos posibles para los hoyos, retornar el estado actual
        if bestState is None:
            return (state, state.utility(currentLevel))

        return (bestState, minValue)


# ================================
# Clase de la Interfaz Gráfica del Usuario (GUI) mejorada sin imágenes y con modo secuencial
# ================================

class WumpusGUI:
    """
    Clase que representa la interfaz gráfica del juego del Wumpus.
    """

    def __init__(self, root):
        self.root = root
        self.tamano = 6
        self.cell_size = 80  # Tamaño de cada celda en píxeles
        self.maxLevel = 3  # Profundidad máxima del árbol de búsqueda
        self.game_running = False  # Indica si el juego está en ejecución
        self.mode = "automatic"  # Modo de juego: automático o secuencial

        # Crear el marco principal
        self.main_frame = tk.Frame(root, bg="#2E4053")
        self.main_frame.pack(padx=10, pady=10)

        # Crear el lienzo para el tablero
        self.canvas = tk.Canvas(self.main_frame, width=self.tamano * self.cell_size,
                                height=self.tamano * self.cell_size, bg="#ECF0F1", bd=0, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=6)  # Aumentar columnspan para la leyenda

        # Crear la barra de estado
        self.status_label = tk.Label(self.main_frame, text="Presiona 'Iniciar' para comenzar el juego.",
                                     font=("Arial", 14), bg="#2E4053", fg="white")
        self.status_label.grid(row=1, column=0, columnspan=6, pady=10)  # Aumentar columnspan para la leyenda

        # Crear el marco para los botones
        self.button_frame = tk.Frame(root, bg="#2E4053")
        self.button_frame.pack(pady=10)

        # Botón para iniciar el juego (Modo Automático)
        self.start_button = tk.Button(self.button_frame, text="Iniciar", command=self.start_game,
                                      width=15, bg="#28B463", fg="white", font=("Arial", 12, "bold"),
                                      activebackground="#1E8449")
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Botón para reiniciar el juego, inicialmente deshabilitado
        self.restart_button = tk.Button(self.button_frame, text="Reiniciar", command=self.reset_game,
                                        state=tk.DISABLED, width=15, bg="#E74C3C", fg="white",
                                        font=("Arial", 12, "bold"), activebackground="#C0392B")
        self.restart_button.pack(side=tk.LEFT, padx=5)

        # Botón para activar el modo secuencial
        self.sequential_button = tk.Button(self.button_frame, text="Modo Secuencial", command=self.activate_sequential_mode,
                                           width=15, bg="#5DADE2", fg="white", font=("Arial", 12, "bold"),
                                           activebackground="#3498DB")
        self.sequential_button.pack(side=tk.LEFT, padx=5)

        # Botón para ejecutar el siguiente movimiento en modo secuencial, inicialmente deshabilitado
        self.next_move_button = tk.Button(self.button_frame, text="Siguiente Movimiento", command=self.execute_next_move,
                                          state=tk.DISABLED, width=17, bg="#F1C40F", fg="black",
                                          font=("Arial", 12, "bold"), activebackground="#F39C12")
        self.next_move_button.pack(side=tk.LEFT, padx=5)

        # **Nuevo Botón de Salir**
        self.exit_button = tk.Button(self.button_frame, text="Salir", command=self.exit_game,
                                     width=10, bg="#95A5A6", fg="white",
                                     font=("Arial", 12, "bold"),
                                     activebackground="#7F8C8D")
        self.exit_button.pack(side=tk.LEFT, padx=5)  # Añadido al final de los botones

        # Crear la leyenda de símbolos
        self.create_legend()

        # Inicializar el tablero
        self.iniciar_nuevo_juego()
        self.draw_board()

    def create_legend(self):
        """
        Crea una leyenda para explicar los símbolos y colores del tablero.
        """
        legend_frame = tk.Frame(self.main_frame, bg="#2E4053")
        legend_frame.grid(row=2, column=0, columnspan=6, pady=10)  # Aumentar columnspan para acomodar más elementos

        # Definición de elementos para la leyenda
        legend_items = [
            ("Agente (A)", "#00FF00"),
            ("Wumpus (W)", "#E74C3C"),
            ("Oro (O)", "#F1C40F"),
            ("Hoyo (H)", "#D35400"),
            ("Hedor (He)", "#95A5A6"),
            ("Brisa (B)", "#2980B9"),
            ("Brisa + Hedor (BH)", "#3498DB"),
            ("Brisa + Oro (BO)", "#F39C12"),
            ("Hedor + Oro (HO)", "#8E44AD"),
            ("Brisa + Hedor + Oro (BHO)", "#E67E22"),
        ]

        for idx, (text, color) in enumerate(legend_items):
            tk.Label(legend_frame, text=text, bg="#2E4053", fg=color, font=("Arial", 10, "bold")).grid(row=0, column=idx, padx=5)

    def iniciar_nuevo_juego(self):
        """
        Inicializa un nuevo juego creando una matriz inicial y un nuevo tablero.
        """
        # Crear una matriz de 6x6 llena de BLANCO (0)
        matriz_inicial = [[BLANCO for _ in range(self.tamano)] for _ in range(self.tamano)]

        # Crear una instancia de Tablerowumpus pasando la matriz inicial
        self.tablero = Tablerowumpus(matriz_inicial)

    def draw_board(self):
        """
        Dibuja el tablero en el lienzo de la interfaz gráfica.
        """
        self.canvas.delete('all')
        matrix = self.tablero.getMatrix()
        for i in range(self.tamano):
            for j in range(self.tamano):
                x0 = j * self.cell_size
                y0 = i * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size

                # Dibujar el fondo de la celda con bordes redondeados
                self.draw_rounded_rectangle(x0, y0, x1, y1, radius=10, fill=self.get_tile_color(matrix[i][j]),
                                            outline="#BDC3C7", width=2)

                # Añadir textos según el tipo de casilla
                self.add_tile_text(i, j, matrix[i][j])

    def get_tile_color(self, tile: int) -> str:
        """
        Devuelve el color correspondiente a cada tipo de casilla.
        """
        color_mapping = {
            BLANCO: "#ECF0F1",          # Gris claro
            AGENTE: "#00FF00",          # Verde brillante
            HOYO: "#D35400",            # Naranja
            WUMPUS: "#E74C3C",          # Rojo
            ORO: "#F1C40F",             # Amarillo
            HEDOR: "#95A5A6",           # Gris
            BRISA: "#2980B9",           # Azul oscuro
            BRISA_HEDOR: "#3498DB",     # Azul
            BRISA_ORO: "#F39C12",       # Naranja claro
            HEDOR_ORO: "#8E44AD",       # Púrpura
            BRISA_HEDOR_ORO: "#E67E22"  # Naranja medio
        }
        return color_mapping.get(tile, "#ECF0F1")  # Por defecto gris claro

    def add_tile_text(self, i: int, j: int, tile: int):
        """
        Añade texto a la casilla según el tipo de elemento.
        """
        text = ""
        font_style = ("Arial", 12, "bold")
        text_color = "black"  # Contraste adecuado con fondo claro

        # Determinar el texto y color según el tipo de casilla
        if tile == AGENTE:
            text = "A"
            text_color = "white"  # Mejor contraste sobre fondo verde
        elif tile == HOYO:
            text = "H"
        elif tile == WUMPUS:
            text = "W"
        elif tile == ORO:
            text = "O"
        elif tile == HEDOR:
            text = "He"
        elif tile == BRISA:
            text = "B"
        elif tile == BRISA_HEDOR:
            text = "BH"
        elif tile == BRISA_ORO:
            text = "BO"
        elif tile == HEDOR_ORO:
            text = "HO"
        elif tile == BRISA_HEDOR_ORO:
            text = "BHO"

        # Añadir el texto al lienzo si corresponde
        if text:
            self.canvas.create_text(j * self.cell_size + self.cell_size / 2,
                                    i * self.cell_size + self.cell_size / 2,
                                    text=text, font=font_style, fill=text_color)

    def draw_rounded_rectangle(self, x1, y1, x2, y2, radius=10, **kwargs):
        """
        Dibuja un rectángulo con esquinas redondeadas en el canvas.
        """
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def start_game(self):
        """
        Inicia el juego en modo automático.
        """
        if not self.game_running:
            self.game_running = True
            self.mode = "automatic"
            # Deshabilitar botones de modo
            self.start_button.config(state=tk.DISABLED)
            self.sequential_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.DISABLED)
            self.next_move_button.config(state=tk.DISABLED)
            self.status_label.config(text="Juego en curso (Automático)...", fg="yellow")
            self.draw_board()
            self.root.after(1000, self.game_step)  # Iniciar después de 1 segundo

    def activate_sequential_mode(self):
        """
        Activa el modo secuencial, donde el jugador debe presionar un botón para cada movimiento.
        """
        if not self.game_running:
            self.game_running = True
            self.mode = "sequential"
            # Deshabilitar botones de modo
            self.start_button.config(state=tk.DISABLED)
            self.sequential_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.DISABLED)
            # Habilitar botón de siguiente movimiento
            self.next_move_button.config(state=tk.NORMAL)
            self.status_label.config(text="Juego en curso (Secuencial). Presiona 'Siguiente Movimiento' para continuar.", fg="yellow")
            self.draw_board()

    def execute_next_move(self):
        """
        Ejecuta el siguiente movimiento en modo secuencial.
        """
        if not self.game_running or self.mode != "sequential":
            return

        if self.tablero.isGameOver():
            self.show_game_over()
            return

        # Turno del Agente (Max)
        print("Turno del Agente:")
        bestState, utilityValue = miniMax(self.tablero, 0, self.maxLevel, 1, -math.inf, math.inf)

        if bestState is not None:
            self.tablero = bestState
            self.draw_board()
            print("Utilidad del estado actual:", utilityValue)
            self.status_label.config(text=f"Utilidad actual: {utilityValue:.2f}", fg="black")
        else:
            print("No se encontraron movimientos para el agente.")

        if self.tablero.isGameOver():
            self.show_game_over()
            return

        # Turno de los Hoyos (Min)
        print("Turno de los Hoyos:")
        moves = self.tablero.getAvailableMovesForMin()
        if moves:
            move = random.choice(moves)
            hoyo_index, new_row, new_col = move
            self.tablero.mover_hoyo(hoyo_index, new_row, new_col)
            self.draw_board()
            print(f"Hoyo {hoyo_index} movido a ({new_row}, {new_col})")
        else:
            print("Los hoyos no pueden moverse.")

        if self.tablero.isGameOver():
            self.show_game_over()
            return

    def game_step(self):
        """
        Ejecuta un paso del juego en modo automático.
        """
        if not self.game_running:
            return

        if self.tablero.isGameOver():
            self.show_game_over()
            return

        # Turno del Agente (Max)
        print("Turno del Agente:")
        bestState, utilityValue = miniMax(self.tablero, 0, self.maxLevel, 1, -math.inf, math.inf)

        if bestState is not None:
            self.tablero = bestState
            self.draw_board()
            print("Utilidad del estado actual:", utilityValue)
            self.status_label.config(text=f"Utilidad actual: {utilityValue:.2f}", fg="black")
        else:
            print("No se encontraron movimientos para el agente.")

        if self.tablero.isGameOver():
            self.show_game_over()
            return

        # Retraso antes del movimiento de los hoyos
        self.root.after(500, self.hoyos_move_step)  # 500 ms de retraso

    def hoyos_move_step(self):
        """
        Ejecuta el movimiento de los hoyos en modo automático.
        """
        if not self.game_running:
            return

        if self.tablero.isGameOver():
            self.show_game_over()
            return

        # Turno de los Hoyos (Min)
        print("Turno de los Hoyos:")
        moves = self.tablero.getAvailableMovesForMin()
        if moves:
            move = random.choice(moves)
            hoyo_index, new_row, new_col = move
            self.tablero.mover_hoyo(hoyo_index, new_row, new_col)
            self.draw_board()
            print(f"Hoyo {hoyo_index} movido a ({new_row}, {new_col})")
        else:
            print("Los hoyos no pueden moverse.")

        if self.tablero.isGameOver():
            self.show_game_over()
            return

        # Retraso antes del siguiente movimiento del agente
        self.root.after(500, self.game_step)  # 500 ms de retraso

    def show_game_over(self):
        """
        Muestra el mensaje de fin de juego y actualiza la interfaz.
        """
        self.game_running = False
        if self.tablero.game_result == 'win':
            messagebox.showinfo("¡Ganaste!", "El agente ha encontrado el oro.")
            self.status_label.config(text="¡Ganaste! El agente ha encontrado el oro.", fg="green")
        elif self.tablero.game_result == 'lose_wumpus':
            messagebox.showinfo("¡Perdiste!", "El agente ha sido devorado por el Wumpus.")
            self.status_label.config(text="¡Perdiste! El agente ha sido devorado por el Wumpus.", fg="red")
        elif self.tablero.game_result == 'lose_hoyo':
            messagebox.showinfo("¡Perdiste!", "El agente ha caído en un hoyo.")
            self.status_label.config(text="¡Perdiste! El agente ha caído en un hoyo.", fg="red")
        else:
            messagebox.showinfo("Juego Terminado", "El juego ha terminado.")
            self.status_label.config(text="Juego Terminado.", fg="black")
        # Habilitar botón de reinicio
        self.restart_button.config(state=tk.NORMAL)
        # Habilitar botones de modo
        self.start_button.config(state=tk.NORMAL)
        self.sequential_button.config(state=tk.NORMAL)
        # Deshabilitar botón de siguiente movimiento
        self.next_move_button.config(state=tk.DISABLED)

    def reset_game(self):
        """
        Reinicia el juego a un nuevo estado aleatorio.
        """
        # Reiniciar el tablero a un nuevo estado aleatorio
        self.iniciar_nuevo_juego()
        self.draw_board()
        print("Juego reiniciado.")
        # Deshabilitar botones de modo
        self.restart_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.sequential_button.config(state=tk.NORMAL)
        # Deshabilitar botón de siguiente movimiento
        self.next_move_button.config(state=tk.DISABLED)
        self.status_label.config(text="Presiona 'Iniciar' o 'Modo Secuencial' para comenzar el juego.", fg="white")

    # **Nueva Función para Salir del Juego**
    def exit_game(self):
        """
        Cierra la aplicación de manera limpia.
        """
        self.root.destroy()


if __name__ == "__main__":
    # Analizar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Juego del Wumpus")
    parser.add_argument('--mode', choices=['gui', 'text'], default='gui', help='Modo de juego: gui o text')
    args = parser.parse_args()

    if args.mode == 'gui':
        # Inicializar la interfaz gráfica
        root = tk.Tk()
        root.title("Juego del Wumpus")
        root.configure(bg="#2E4053")
        gui = WumpusGUI(root)
        root.mainloop()
    else:
        # Implementación del modo de texto (si es necesario)
        # Aquí puedes añadir la función run_text_game() si tienes una implementación en modo texto
        print("Modo de juego en texto no está implementado.")
