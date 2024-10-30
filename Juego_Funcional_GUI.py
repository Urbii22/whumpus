import random
import math
import tkinter as tk
from tkinter import messagebox
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
HEDOR_ORO = 7
BRISA_ORO = 8
BRISA_HEDOR = 9
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
        self.pos_agente = (5, 0)  # Posición inicial del agente

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

        # Colocar los 2 hoyos asegurando que no estén adyacentes al agente
        if len(posiciones_disponibles) < 2:
            raise ValueError("No hay suficientes posiciones disponibles para colocar los hoyos.")

        # Excluir posiciones adyacentes al agente para los hoyos
        posiciones_para_hoyos = [pos for pos in posiciones_disponibles if not self.es_adyacente(pos, self.pos_agente)]
        if len(posiciones_para_hoyos) < 2:
            raise ValueError(
                "No hay suficientes posiciones disponibles para colocar los hoyos sin estar adyacentes al agente.")

        hoyos_pos1 = random.choice(posiciones_para_hoyos)
        self.placeTile(hoyos_pos1[0], hoyos_pos1[1], HOYO)
        posiciones_disponibles.remove(hoyos_pos1)
        posiciones_para_hoyos.remove(hoyos_pos1)

        hoyos_pos2 = random.choice(posiciones_para_hoyos)
        self.placeTile(hoyos_pos2[0], hoyos_pos2[1], HOYO)
        posiciones_disponibles.remove(hoyos_pos2)
        self.pos_hoyos = [hoyos_pos1, hoyos_pos2]  # Almacenar las posiciones de los Hoyos

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
            BRISA_HEDOR_ORO: 0,
            HOYO: 0,
            WUMPUS: 0

        }

        for vec in vecinos_agente:
            tile = self.matrix[vec[0]][vec[1]]
            if tile in contador_penalizaciones:
                contador_penalizaciones[tile] += 1

        # Definir pesos de penalización
        pesos_penalizacion = {
        # las penalizaciones de hoyo y del whumpus son negativas ya que si las dejamos en positivo, al realizar
        # el movimiento hacia hoyo o whupus, el agente el nuevo estao seria mejor que el anterior, lo cual no es correcto
        # ya que el agente moriria, al ser negativos hace que la funcion de utilidad sea menor al mover a esas casillas
        # por lo que el agente no se movera hacia esas casillas
            HEDOR: 0.1,
            BRISA: 0.05,
            BRISA_HEDOR: 0.2,
            BRISA_ORO: 0,
            HEDOR_ORO: 0,
            BRISA_HEDOR_ORO: 0,
            HOYO: -0.5,
            WUMPUS: -0.5
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
        # Antes de mover, restaurar las casillas de brisa y hedor si es necesario
        self.restore_tile(old_row, old_col)

        # Actualizar la posición del agente
        self.pos_agente = (new_row, new_col)

        # Colocar el agente en la nueva posición
        self.placeTile(new_row, new_col, AGENTE)

    def restore_tile(self, row: int, col: int):
        # Restaurar la casilla según sus vecinos
        # Primero, limpiar brisas y hedores alrededor de la posición
        # Luego, recalcular si debe tener brisa o hedor
        self.placeTile(row, col, BLANCO)

        # Recalcular brisas y hedores en los vecinos
        vecinos = self.obtener_vecinos((row, col))
        for vec in vecinos:
            tile = self.matrix[vec[0]][vec[1]]
            if tile == HOYO:
                # Añadir brisa alrededor del hoyo
                if self.matrix[row][col] == BLANCO:
                    self.placeTile(row, col, BRISA)
            elif tile == WUMPUS:
                # Añadir hedor alrededor del Wumpus
                if self.matrix[row][col] == BLANCO:
                    self.placeTile(row, col, HEDOR)
            elif tile == ORO:
                # Si hay oro y brisa
                if self.matrix[row][col] == BLANCO:
                    self.placeTile(row, col, BRISA_ORO)

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
        """
        Verifica si un hoyo puede moverse a la posición (new_row, new_col).
        Puede moverse a casillas que sean BLANCO, BRISA, HEDOR o BRISA_HEDOR,
        pero no a casillas ocupadas por ORO, WUMPUS, AGENTE, BRISA_ORO, HEDOR_ORO o BRISA_HEDOR_ORO.
        """
        if 0 <= new_row < self.tamano and 0 <= new_col < self.tamano:
            tile = self.matrix[new_row][new_col]
            # Evitar ORO, Wumpus, AGENTE, BRISA_ORO y HEDOR_ORO
            forbidden_tiles = {AGENTE, WUMPUS, ORO, BRISA_ORO, HEDOR_ORO, BRISA_HEDOR_ORO}
            if tile not in forbidden_tiles and tile in {BLANCO, BRISA, HEDOR, BRISA_HEDOR}:
                return True
        return False

    def mover_hoyo(self, hoyo_index: int, new_row: int, new_col: int):
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
        if player == 1:  # Max (Agente)
            moves = self.getAvailableMovesForMax(*self.pos_agente)
            return len(moves) > 0
        else:  # Min (Hoyos)
            moves = self.getAvailableMovesForMin()
            return len(moves) > 0


# ================================
# Implementación de la función miniMax
# ================================

def miniMax(state: Tablerowumpus, currentLevel: int, maxLevel: int, player: int, alpha: float, beta: float) -> Tuple[
    Tablerowumpus, float]:
    # Verificar si el juego ha terminado o si se alcanzó el nivel máximo de profundidad
    if not state.moveCanBeMade(player) or currentLevel == maxLevel or state.isGameOver():
        return (state, state.utility())

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
            _, value = miniMax(new_state, currentLevel + 1, maxLevel, 0, alpha, beta)

            if value > maxValue:
                maxValue = value
                bestState = new_state

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

            if value < minValue:
                minValue = value
                bestState = new_state

            beta = min(beta, minValue)
            if beta <= alpha:
                break  # Poda alfa

        # Si no hay movimientos posibles para los hoyos, retornamos el estado actual
        if bestState is None:
            return (state, state.utility())

        return (bestState, minValue)


# ================================
# Clase de la GUI
# ================================

class WumpusGUI:
    def __init__(self, root):
        self.root = root
        self.tamano = 6
        self.cell_size = 80  # Tamaño de cada celda en píxeles
        self.maxLevel = 3  # Profundidad máxima del árbol de búsqueda
        self.game_running = False  # Indica si el juego está en ejecución

        # Crear el marco principal
        self.main_frame = tk.Frame(root)
        self.main_frame.pack()

        # Crear el lienzo para el tablero
        self.canvas = tk.Canvas(self.main_frame, width=self.tamano * self.cell_size,
                                height=self.tamano * self.cell_size)
        self.canvas.pack()

        # Crear el marco para los botones
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        # Botón para iniciar el juego
        self.start_button = tk.Button(self.button_frame, text="Iniciar", command=self.start_game, width=15)
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Botón para reiniciar el juego, inicialmente deshabilitado
        self.restart_button = tk.Button(self.button_frame, text="Reiniciar", command=self.reset_game, state=tk.DISABLED,
                                        width=15)
        self.restart_button.pack(side=tk.LEFT, padx=5)

        # Inicializar el tablero
        self.iniciar_nuevo_juego()
        self.draw_board()

    def iniciar_nuevo_juego(self):
        # Crear una matriz de 6x6 llena de BLANCO (0)
        matriz_inicial = [[BLANCO for _ in range(self.tamano)] for _ in range(self.tamano)]

        # Crear una instancia de Tablerowumpus pasando la matriz inicial
        self.tablero = Tablerowumpus(matriz_inicial)

    def draw_board(self):
        self.canvas.delete('all')
        matrix = self.tablero.getMatrix()
        for i in range(self.tamano):
            for j in range(self.tamano):
                x0 = j * self.cell_size
                y0 = i * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                tile = matrix[i][j]
                color = 'white'
                text = ''

                if tile == AGENTE:
                    color = 'lightblue'
                    text = 'A'
                elif tile == HOYO:
                    color = 'black'
                    text = 'H'
                elif tile == WUMPUS:
                    color = 'red'
                    text = 'W'
                elif tile == ORO:
                    color = 'yellow'
                    text = 'O'
                elif tile == HEDOR:
                    color = 'gray'
                    text = 'He'
                elif tile == BRISA:
                    color = 'lightgray'
                    text = 'B'
                elif tile == BRISA_HEDOR:
                    color = 'darkgray'
                    text = 'BHe'
                elif tile == BRISA_ORO:
                    color = 'gold'
                    text = 'BO'
                elif tile == HEDOR_ORO:
                    color = 'orange'
                    text = 'HeO'
                elif tile == BRISA_HEDOR_ORO:
                    color = 'brown'
                    text = 'BHeO'

                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='black')
                if text:
                    self.canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=text)

    def start_game(self):
        if not self.game_running:
            self.game_running = True
            self.start_button.config(state=tk.DISABLED)  # Deshabilitar botón de inicio
            self.restart_button.config(state=tk.DISABLED)  # Asegurarse que reiniciar está deshabilitado
            self.draw_board()
            self.root.after(1000, self.game_step)  # Iniciar después de 1 segundo

    def game_step(self):
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
        else:
            print("No se encontraron movimientos para el agente.")

        if self.tablero.isGameOver():
            self.show_game_over()
            return

        # Retraso antes del movimiento de los hoyos
        self.root.after(500, self.hoyos_move_step)  # 500 ms de retraso

    def hoyos_move_step(self):
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
        self.game_running = False
        if self.tablero.game_result == 'win':
            messagebox.showinfo("¡Ganaste!", "El agente ha encontrado el oro.")
        elif self.tablero.game_result == 'lose_wumpus':
            messagebox.showinfo("¡Perdiste!", "El agente ha sido devorado por el Wumpus.")
        elif self.tablero.game_result == 'lose_hoyo':
            messagebox.showinfo("¡Perdiste!", "El agente ha caído en un hoyo.")
        else:
            messagebox.showinfo("Juego Terminado", "El juego ha terminado.")
        self.restart_button.config(state=tk.NORMAL)  # Habilitar botón de reinicio

    def reset_game(self):
        # Reiniciar el tablero a un nuevo estado aleatorio
        self.iniciar_nuevo_juego()
        self.draw_board()
        print("Juego reiniciado.")
        self.restart_button.config(state=tk.DISABLED)  # Deshabilitar botón de reinicio
        self.start_button.config(state=tk.NORMAL)  # Habilitar botón de inicio


# ================================
# Ejecución Automática del Juego con GUI
# ================================

if __name__ == "__main__":
    # Inicializar la GUI
    root = tk.Tk()
    root.title("Juego del Wumpus")
    gui = WumpusGUI(root)
    root.mainloop()
