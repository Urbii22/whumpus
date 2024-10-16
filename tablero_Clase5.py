import random
import math
from copy import deepcopy
from typing import List, Tuple


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


class Tablerowumpus:

    def __init__(self):
        self.tamano = 6
        self.matrix = [[BLANCO for _ in range(self.tamano)] for _ in range(self.tamano)]
        self.pos_agente = (5, 0)  # Posición fija inicial del agente
        self.last_cell_value = BLANCO  # Valor original de la casilla del agente
        self.matrix[self.pos_agente[0]][self.pos_agente[1]] = AGENTE
        self.game_over = False
        self.win = False
        self.colocar_elementos()

    def __eq__(self, other) -> bool:
        for i in range(self.tamano):
            for j in range(self.tamano):
                if self.matrix[i][j] != other.matrix[i][j]:
                    return False
        return True

    def setMatrix(self, matrix):
        self.matrix = deepcopy(matrix)

    def getMatrix(self) -> List[List]:
        return deepcopy(self.matrix)

    def placeTile(self, row: int, col: int, tile: int):
        if 0 <= row < self.tamano and 0 <= col < self.tamano:
            self.matrix[row][col] = tile

    def colocar_elementos(self):
        posiciones_disponibles = [(i, j) for i in range(self.tamano) for j in range(self.tamano)]
        posiciones_disponibles.remove(self.pos_agente)

        # Colocar el Wumpus
        wumpus_pos = random.choice(posiciones_disponibles)
        self.placeTile(wumpus_pos[0], wumpus_pos[1], WUMPUS)
        posiciones_disponibles.remove(wumpus_pos)

        # Colocar el oro asegurando que no esté adyacente al agente
        posiciones_no_adyacentes = [pos for pos in posiciones_disponibles if
                                    not self.es_adyacente(pos, self.pos_agente)]
        oro_pos = random.choice(posiciones_no_adyacentes)
        self.placeTile(oro_pos[0], oro_pos[1], ORO)
        posiciones_disponibles.remove(oro_pos)

        # Colocar los 2 huecos
        hoyos_pos1 = random.choice(posiciones_disponibles)
        self.placeTile(hoyos_pos1[0], hoyos_pos1[1], HOYO)
        posiciones_disponibles.remove(hoyos_pos1)

        hoyos_pos2 = random.choice(posiciones_disponibles)
        self.placeTile(hoyos_pos2[0], hoyos_pos2[1], HOYO)
        posiciones_disponibles.remove(hoyos_pos2)

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
        posAgente = [0, 0]
        posOro = [0, 0]
        alto = len(self.matrix)
        ancho = len(self.matrix[0])

        for i in range(alto):
            for j in range(ancho):
                if self.matrix[i][j] == AGENTE:
                    posAgente = [i, j]
                if self.matrix[i][j] in [ORO, BRISA_ORO, HEDOR_ORO]:
                    posOro = [i, j]

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
            HOYO: 0,
            WUMPUS: 0
        }

        for vec in vecinos_agente:
            tile = self.matrix[vec[0]][vec[1]]
            if tile in contador_penalizaciones:
                contador_penalizaciones[tile] += 1

        # Definir pesos de penalización
        pesos_penalizacion = {
            HEDOR: 0.1,
            BRISA: 0.1,
            BRISA_HEDOR: 0.15,
            BRISA_ORO: 0.05,
            HEDOR_ORO: 0.05,
            HOYO: 0.2,
            WUMPUS: 0.25
        }

        # Calcular penalización total
        penalizacion_total = 0.0
        for tile, count in contador_penalizaciones.items():
            penalizacion_total += pesos_penalizacion.get(tile, 0) * count

        # Calcular la utilidad final
        utilidad = (1 / (distancia + 1e-2)) - penalizacion_total

        return utilidad

    def mover_agente(self, direccion: str) -> bool:
        """
        Mueve al agente en la dirección especificada si el movimiento es válido.
        Direcciones permitidas: 'arriba', 'abajo', 'izquierda', 'derecha'.
        Retorna True si el movimiento fue exitoso, False en caso contrario.
        """
        if self.game_over:
            print("El juego ha terminado. Por favor, reinicia para jugar nuevamente.")
            return False

        direcciones_validas = ['arriba', 'abajo', 'izquierda', 'derecha']
        if direccion not in direcciones_validas:
            print(f"Dirección inválida: {direccion}. Usa 'arriba', 'abajo', 'izquierda' o 'derecha'.")
            return False

        # Obtener la posición actual del agente
        fila_actual, col_actual = self.pos_agente
        nueva_fila, nueva_col = fila_actual, col_actual

        if direccion == 'arriba':
            nueva_fila -= 1
        elif direccion == 'abajo':
            nueva_fila += 1
        elif direccion == 'izquierda':
            nueva_col -= 1
        elif direccion == 'derecha':
            nueva_col += 1

        # Verificar que la nueva posición esté dentro del tablero
        if not (0 <= nueva_fila < self.tamano and 0 <= nueva_col < self.tamano):
            print("Movimiento fuera de los límites del tablero.")
            return False

        # Verificar si el movimiento es no diagonal (ya garantizado por las direcciones permitidas)

        # Verificar si la nueva casilla está ocupada por un obstáculo (por ejemplo, WUMPUS o HOYO)
        tile_destino = self.matrix[nueva_fila][nueva_col]

        # Restaurar el valor original de la casilla actual
        self.matrix[fila_actual][col_actual] = self.last_cell_value

        # Manejar encuentros
        if tile_destino == WUMPUS:
            print("¡El agente ha encontrado al Wumpus! Juego terminado. Has perdido.")
            self.game_over = True
            self.win = False
            return False
        elif tile_destino == HOYO:
            print("¡El agente ha caído en un hoyo! Juego terminado. Has perdido.")
            self.game_over = True
            self.win = False
            return False
        elif tile_destino == ORO:
            print("¡El agente ha encontrado el oro! ¡Has ganado!")
            # Actualizar la posición del agente
            self.last_cell_value = self.matrix[nueva_fila][nueva_col]
            self.matrix[nueva_fila][nueva_col] = AGENTE
            self.pos_agente = (nueva_fila, nueva_col)
            self.game_over = True
            self.win = True
            # Calcular y mostrar la utilidad final
            utilidad = self.utility()
            print(f"Utilidad final: {utilidad}")
            return True

        # Preservar el valor de la nueva casilla
        self.last_cell_value = self.matrix[nueva_fila][nueva_col]

        # Mover al agente a la nueva posición
        self.matrix[nueva_fila][nueva_col] = AGENTE
        self.pos_agente = (nueva_fila, nueva_col)
        print(f"Agente movido a: {self.pos_agente}")

        # Recalcular y mostrar la utilidad después del movimiento
        utilidad = self.utility()
        print(f"Utilidad actualizada: {utilidad}")

        return True

    def imprimir_tablero(self):
        print("Tablero Actual:")
        for fila in self.matrix:
            print(' '.join(str(casilla) for casilla in fila))
        print()


if __name__ == "__main__":
    tablero = Tablerowumpus()
    tablero.imprimir_tablero()
    utilidad_inicial = tablero.utility()
    print("Utilidad inicial del tablero:", utilidad_inicial)

    # Interfaz simple para mover al agente
    while not tablero.game_over:
        print("\nDirecciones permitidas: 'arriba', 'abajo', 'izquierda', 'derecha'")
        direccion = input("Ingresa la dirección para mover al agente (o 'salir' para terminar): ").strip().lower()
        if direccion == 'salir':
            print("Terminando el juego.")
            break
        exitoso = tablero.mover_agente(direccion)
        tablero.imprimir_tablero()
        if exitoso and not tablero.game_over:
            utilidad_actual = tablero.utility()
            print(f"Utilidad actualizada del tablero: {utilidad_actual}")
        elif tablero.game_over:
            if tablero.win:
                print("¡Felicidades! Has ganado el juego.")
            else:
                print("Has perdido el juego.")
        else:
            print("Movimiento no exitoso.")
