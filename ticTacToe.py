def inicializar_tablero():
    return [None] * 9

def imprimir_tablero(tablero):
    for i in range(3):
        fila = tablero[3*i:3*(i+1)]
        print("|".join([celda if celda is not None else ' ' for celda in fila]))
        if i < 2:
            print("-----")
    print()  # Línea en blanco para separar tableros

def verificar_ganador(tablero):
    combinaciones = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Filas
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columnas
        [0, 4, 8], [2, 4, 6]              # Diagonales
    ]
    for combo in combinaciones:
        a, b, c = combo
        if tablero[a] == tablero[b] == tablero[c] and tablero[a] is not None:
            return tablero[a]
    if all(celda is not None for celda in tablero):
        return 'Empate'
    return None

def movimientos_disponibles(tablero):
    return [i for i, celda in enumerate(tablero) if celda is None]

def minimax(tablero, profundidad, es_maximizando, indent=""):
    resultado = verificar_ganador(tablero)
    if resultado == 'X':
        print(f"{indent}Profundidad {profundidad}: 'X' gana. Puntaje = 1")
        imprimir_tablero(tablero)
        return 1
    elif resultado == 'O':
        print(f"{indent}Profundidad {profundidad}: 'O' gana. Puntaje = -1")
        imprimir_tablero(tablero)
        return -1
    elif resultado == 'Empate':
        print(f"{indent}Profundidad {profundidad}: Empate. Puntaje = 0")
        imprimir_tablero(tablero)
        return 0

    if es_maximizando:
        mejor_puntaje = -float('inf')
        print(f"{indent}Profundidad {profundidad}: Maximizando 'X'")
        for movimiento in movimientos_disponibles(tablero):
            tablero[movimiento] = 'X'
            print(f"{indent}  'X' coloca en posición {movimiento}")
            puntaje = minimax(tablero, profundidad + 1, False, indent + "    ")
            tablero[movimiento] = None
            mejor_puntaje = max(mejor_puntaje, puntaje)
        print(f"{indent}Profundidad {profundidad}: Mejor puntaje para 'X' = {mejor_puntaje}")
        return mejor_puntaje
    else:
        mejor_puntaje = float('inf')
        print(f"{indent}Profundidad {profundidad}: Minimizando 'O'")
        for movimiento in movimientos_disponibles(tablero):
            tablero[movimiento] = 'O'
            print(f"{indent}  'O' coloca en posición {movimiento}")
            puntaje = minimax(tablero, profundidad + 1, True, indent + "    ")
            tablero[movimiento] = None
            mejor_puntaje = min(mejor_puntaje, puntaje)
        print(f"{indent}Profundidad {profundidad}: Mejor puntaje para 'O' = {mejor_puntaje}")
        return mejor_puntaje

def mejor_jugada(tablero):
    mejor_puntaje = -float('inf')
    movimiento_optimo = None
    print("Evaluando movimientos para 'X'...")
    for movimiento in movimientos_disponibles(tablero):
        tablero[movimiento] = 'X'
        print(f"'X' prueba la posición {movimiento}:")
        puntaje = minimax(tablero, 0, False, indent="  ")
        print(f"Puntaje de la posición {movimiento}: {puntaje}\n")
        tablero[movimiento] = None
        if puntaje > mejor_puntaje:
            mejor_puntaje = puntaje
            movimiento_optimo = movimiento
    print(f"Mejor jugada para 'X' es la posición {movimiento_optimo} con puntaje {mejor_puntaje}\n")
    return movimiento_optimo

def juego():
    tablero = inicializar_tablero()
    turno = 'X'  # 'X' será la IA, 'O' el jugador

    while True:
        imprimir_tablero(tablero)
        ganador = verificar_ganador(tablero)
        if ganador:
            if ganador == 'Empate':
                print("¡Es un empate!")
            else:
                print(f"¡{ganador} gana!")
            break

        if turno == 'X':
            print("Turno de la IA (X):")
            movimiento = mejor_jugada(tablero)
            if movimiento is not None:
                tablero[movimiento] = 'X'
            turno = 'O'
        else:
            print("Turno del Jugador (O):")
            try:
                movimiento = int(input("Ingresa una posición (0-8): "))
                if movimiento not in range(9):
                    print("Posición inválida. Debe estar entre 0 y 8.\n")
                    continue
                if tablero[movimiento] is None:
                    tablero[movimiento] = 'O'
                    turno = 'X'
                else:
                    print("Movimiento inválido. Casilla ya ocupada.\n")
            except ValueError:
                print("Entrada inválida. Por favor, ingresa un número entre 0 y 8.\n")

if __name__ == "__main__":
    juego()
