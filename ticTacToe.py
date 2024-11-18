import tkinter as tk
from tkinter import messagebox

def inicializar_tablero():
    return [None] * 9

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

def minimax(tablero, es_maximizando):
    resultado = verificar_ganador(tablero)
    if resultado == 'X':
        return 1
    elif resultado == 'O':
        return -1
    elif resultado == 'Empate':
        return 0

    if es_maximizando:
        mejor_puntaje = -float('inf')
        for movimiento in movimientos_disponibles(tablero):
            tablero[movimiento] = 'X'
            puntaje = minimax(tablero, False)
            tablero[movimiento] = None
            mejor_puntaje = max(mejor_puntaje, puntaje)
        return mejor_puntaje
    else:
        mejor_puntaje = float('inf')
        for movimiento in movimientos_disponibles(tablero):
            tablero[movimiento] = 'O'
            puntaje = minimax(tablero, True)
            tablero[movimiento] = None
            mejor_puntaje = min(mejor_puntaje, puntaje)
        return mejor_puntaje

def mejor_jugada(tablero):
    mejor_puntaje = -float('inf')
    movimiento_optimo = None
    for movimiento in movimientos_disponibles(tablero):
        tablero[movimiento] = 'X'
        puntaje = minimax(tablero, False)
        tablero[movimiento] = None
        if puntaje > mejor_puntaje:
            mejor_puntaje = puntaje
            movimiento_optimo = movimiento
    return movimiento_optimo

def actualizar_interfaz():
    for i in range(9):
        texto = tablero[i] if tablero[i] is not None else ''
        botones[i]['text'] = texto

def click_boton(i):
    if tablero[i] is None and turno_jugador.get():
        tablero[i] = 'O'
        actualizar_interfaz()
        ganador = verificar_ganador(tablero)
        if ganador:
            if ganador == 'Empate':
                messagebox.showinfo("Resultado", "¡Es un empate!")
            else:
                messagebox.showinfo("Resultado", f"¡{ganador} gana!")
            reiniciar_juego()
        else:
            turno_jugador.set(False)
            ventana.after(500, turno_ia)

def turno_ia():
    movimiento = mejor_jugada(tablero)
    if movimiento is not None:
        tablero[movimiento] = 'X'
        actualizar_interfaz()
        ganador = verificar_ganador(tablero)
        if ganador:
            if ganador == 'Empate':
                messagebox.showinfo("Resultado", "¡Es un empate!")
            else:
                messagebox.showinfo("Resultado", f"¡{ganador} gana!")
            reiniciar_juego()
        else:
            turno_jugador.set(True)

def reiniciar_juego():
    global tablero
    tablero = inicializar_tablero()
    actualizar_interfaz()
    turno_jugador.set(True)

# Configuración de la ventana principal
ventana = tk.Tk()
ventana.title("Tres en Raya")

tablero = inicializar_tablero()
turno_jugador = tk.BooleanVar(value=True)

# Creación de los botones del tablero
botones = []
for i in range(9):
    boton = tk.Button(ventana, text='', font=('Helvetica', 32), width=5, height=2, command=lambda i=i: click_boton(i))
    boton.grid(row=i//3, column=i%3)
    botones.append(boton)

# Iniciar el juego
actualizar_interfaz()
ventana.mainloop()
