import tkinter as tk
import random
from tkinter import messagebox

# Definir direcciones
DIRECCIONES = ['N', 'W', 'S', 'E']  # Norte, Oeste, Sur, Este


class Celda:
    """Clase que representa cada celda del tablero."""

    def __init__(self):
        self.agente = False
        self.wumpus = False
        self.oro = False
        self.hoyo = False
        self.hedor = False
        self.brisa = False


class JuegoWumpus:
    """Clase principal que maneja la lógica del juego Wumpus."""

    def __init__(self, filas=6, columnas=6, num_hoyos=3, aleatorio=True):
        self.filas = filas
        self.columnas = columnas
        self.num_hoyos = num_hoyos
        self.aleatorio = aleatorio  # Determina si la colocación es aleatoria o manual
        self.tablero = [[Celda() for _ in range(columnas)] for _ in range(filas)]
        self.agente_pos = (filas - 1, 0)  # Empieza en (M,1) que es (filas-1, 0) en índice 0
        self.agente_direccion = 'E'  # Dirección inicial (Este)
        self.flecha = True  # El agente tiene una flecha
        self.wumpus_vivo = True
        self.juego_terminado = False
        self.ganar = False
        self.colocar_agente()
        self.colocar_elementos()

    def colocar_agente(self):
        fila, col = self.agente_pos
        self.tablero[fila][col].agente = True

    def colocar_elementos(self):
        # Colocar Wumpus
        while True:
            fila = random.randint(0, self.filas - 1)
            col = random.randint(0, self.columnas - 1)
            if (fila, col) != self.agente_pos:
                self.tablero[fila][col].wumpus = True
                self.wumpus_pos = (fila, col)
                self.actualizar_percepciones(fila, col, tipo='wumpus')
                break

        # Colocar Hoyos
        colocados = 0
        while colocados < self.num_hoyos:
            fila = random.randint(0, self.filas - 1)
            col = random.randint(0, self.columnas - 1)
            if (fila, col) != self.agente_pos and not self.tablero[fila][col].wumpus and not self.tablero[fila][
                col].hoyo:
                # Verificar que no esté contiguo al Wumpus
                if not self.adyacente(fila, col, self.wumpus_pos[0], self.wumpus_pos[1]):
                    self.tablero[fila][col].hoyo = True
                    self.actualizar_percepciones(fila, col, tipo='hoyo')
                    colocados += 1

        # Colocar Oro
        while True:
            fila = random.randint(0, self.filas - 1)
            col = random.randint(0, self.columnas - 1)
            if (fila, col) != self.agente_pos and not self.tablero[fila][col].wumpus and not self.tablero[fila][
                col].hoyo:
                self.tablero[fila][col].oro = True
                break

    def adyacente(self, fila1, col1, fila2, col2):
        """Verifica si dos posiciones están adyacentes (arriba, abajo, izquierda, derecha)."""
        return (abs(fila1 - fila2) == 1 and col1 == col2) or (abs(col1 - col2) == 1 and fila1 == fila2)

    def actualizar_percepciones(self, fila, col, tipo):
        """
        Actualiza las percepciones de hedor y brisa en las celdas adyacentes.
        :param fila: Fila del elemento (Wumpus o Hoyo)
        :param col: Columna del elemento
        :param tipo: 'wumpus' o 'hoyo'
        """
        adyacentes = self.obtener_adyacentes(fila, col)
        for f, c in adyacentes:
            celda = self.tablero[f][c]
            if tipo == 'wumpus':
                celda.hedor = True
            elif tipo == 'hoyo':
                celda.brisa = True

    def obtener_adyacentes(self, fila, col):
        """Devuelve una lista de posiciones adyacentes válidas."""
        adyacentes = []
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Norte, Sur, Oeste, Este
        for df, dc in direcciones:
            nf, nc = fila + df, col + dc
            if 0 <= nf < self.filas and 0 <= nc < self.columnas:
                adyacentes.append((nf, nc))
        return adyacentes

    def mover_agente(self, direccion):
        """Mueve al agente en la dirección especificada."""
        if self.juego_terminado:
            return

        # Quitar agente de posición actual
        fila, col = self.agente_pos
        self.tablero[fila][col].agente = False

        # Calcular nueva posición
        if direccion == 'N':
            fila_nueva, col_nueva = fila - 1, col
        elif direccion == 'S':
            fila_nueva, col_nueva = fila + 1, col
        elif direccion == 'E':
            fila_nueva, col_nueva = fila, col + 1
        elif direccion == 'W':
            fila_nueva, col_nueva = fila, col - 1
        else:
            return  # Dirección no válida

        # Verificar límites
        if 0 <= fila_nueva < self.filas and 0 <= col_nueva < self.columnas:
            self.agente_pos = (fila_nueva, col_nueva)
            self.tablero[fila_nueva][col_nueva].agente = True
            self.agente_direccion = direccion
            self.verificar_celda()
        else:
            # Si sale del tablero, revertir
            self.tablero[fila][col].agente = True
            messagebox.showinfo("Movimiento inválido", "No puedes salir del tablero.")

    def girar_agente(self):
        """Gira al agente 90 grados en sentido contrario a las agujas del reloj."""
        idx = DIRECCIONES.index(self.agente_direccion)
        nueva_direccion = DIRECCIONES[(idx + 1) % 4]
        self.agente_direccion = nueva_direccion

    def usar_flecha_funcion(self):
        """El agente usa la flecha para intentar matar al Wumpus."""
        if self.juego_terminado:
            return

        if not self.flecha:
            messagebox.showinfo("Flecha", "Ya has usado tu flecha.")
            return

        self.flecha = False
        fila_agente, col_agente = self.agente_pos
        direccion = self.agente_direccion

        # Determinar dirección de tiro
        if direccion == 'N':
            rango = range(fila_agente - 1, -1, -1)
            for f in rango:
                if self.tablero[f][col_agente].wumpus:
                    self.wumpus_vivo = False
                    self.tablero[f][col_agente].wumpus = False
                    # Eliminar percepciones si Wumpus muere
                    self.tablero[f][col_agente].hedor = False
                    messagebox.showinfo("Flecha", "¡Has matado al Wumpus!")
                    self.juego_terminado = True
                    self.ganar = True
                    return
        elif direccion == 'S':
            rango = range(fila_agente + 1, self.filas)
            for f in rango:
                if self.tablero[f][col_agente].wumpus:
                    self.wumpus_vivo = False
                    self.tablero[f][col_agente].wumpus = False
                    self.tablero[f][col_agente].hedor = False
                    messagebox.showinfo("Flecha", "¡Has matado al Wumpus!")
                    self.juego_terminado = True
                    self.ganar = True
                    return
        elif direccion == 'E':
            rango = range(col_agente + 1, self.columnas)
            for c in rango:
                if self.tablero[fila_agente][c].wumpus:
                    self.wumpus_vivo = False
                    self.tablero[fila_agente][c].wumpus = False
                    self.tablero[fila_agente][c].hedor = False
                    messagebox.showinfo("Flecha", "¡Has matado al Wumpus!")
                    self.juego_terminado = True
                    self.ganar = True
                    return
        elif direccion == 'W':
            rango = range(col_agente - 1, -1, -1)
            for c in rango:
                if self.tablero[fila_agente][c].wumpus:
                    self.wumpus_vivo = False
                    self.tablero[fila_agente][c].wumpus = False
                    self.tablero[fila_agente][c].hedor = False
                    messagebox.showinfo("Flecha", "¡Has matado al Wumpus!")
                    self.juego_terminado = True
                    self.ganar = True
                    return
        messagebox.showinfo("Flecha", "Has usado tu flecha.")

    def verificar_celda(self):
        """Verifica el estado de la celda donde está el agente."""
        fila, col = self.agente_pos
        celda = self.tablero[fila][col]

        # Si hay Wumpus y está vivo
        if celda.wumpus and self.wumpus_vivo:
            self.juego_terminado = True
            messagebox.showinfo("¡Perdiste!", "Has sido matado por el Wumpus.")
            return

        # Si hay un hoyo
        if celda.hoyo:
            self.juego_terminado = True
            messagebox.showinfo("¡Perdiste!", "Has caído en un hoyo.")
            return

        # Si hay oro
        if celda.oro:
            self.juego_terminado = True
            self.ganar = True
            messagebox.showinfo("¡Ganaste!", "¡Has encontrado el oro y ganado el juego!")
            return

    def reiniciar_juego(self):
        """Reinicia el juego."""
        self.__init__(self.filas, self.columnas, self.num_hoyos, self.aleatorio)


class GUIWumpus:
    """Clase que maneja la interfaz gráfica del juego Wumpus."""

    def __init__(self, juego):
        self.juego = juego
        self.root = tk.Tk()
        self.root.title("Juego Wumpus")
        self.crear_tablero()
        self.crear_info()
        self.actualizar_visual()
        self.root.bind("<Key>", self.manejar_teclas)

    def crear_tablero(self):
        """Crea el tablero visual usando botones."""
        self.botones = [[None for _ in range(self.juego.columnas)] for _ in range(self.juego.filas)]
        for f in range(self.juego.filas):
            for c in range(self.juego.columnas):
                btn = tk.Button(
                    self.root,
                    width=12,
                    height=6,
                    command=lambda row=f, col=c: self.mostrar_info_celda(row, col),
                    state="disabled"  # Deshabilitar clic para evitar revelar información
                )
                btn.grid(row=f, column=c)
                self.botones[f][c] = btn

    def crear_info(self):
        """Crea un área de información para mostrar percepciones."""
        self.info_label = tk.Label(self.root, text="Usa las flechas para mover al agente.", font=("Helvetica", 12))
        self.info_label.grid(row=self.juego.filas, column=0, columnspan=self.juego.columnas)

    def actualizar_visual(self):
        """Actualiza la visualización del tablero según el estado del juego."""
        for f in range(self.juego.filas):
            for c in range(self.juego.columnas):
                celda = self.juego.tablero[f][c]
                btn = self.botones[f][c]
                # Reset estilo
                btn.config(bg="lightgrey", text="")
                # Agente
                if celda.agente:
                    text = "A"
                    # Mostrar percepciones en la misma casilla
                    percepciones = []
                    if celda.hedor:
                        percepciones.append("H")
                    if celda.brisa:
                        percepciones.append("B")
                    if percepciones:
                        text += "\n" + ",".join(percepciones)
                    btn.config(bg="blue", text=text)
                elif self.juego.juego_terminado:
                    # Revelar todos los elementos al finalizar el juego
                    if celda.wumpus and self.juego.wumpus_vivo:
                        btn.config(bg="red", text="W")
                    elif celda.hoyo:
                        btn.config(bg="black", text="H")
                    elif celda.oro:
                        btn.config(bg="yellow", text="O")

        # Actualizar percepciones en la etiqueta inferior basado en la casilla actual
        fila, col = self.juego.agente_pos
        celda_actual = self.juego.tablero[fila][col]
        percepciones = []
        if celda_actual.hedor:
            percepciones.append("Hedor")
        if celda_actual.brisa:
            percepciones.append("Brisa")
        percepciones = list(set(percepciones))  # Evitar duplicados
        if percepciones:
            texto = "Percepciones: " + ", ".join(percepciones)
        else:
            texto = "Percepciones: Ninguna"
        if self.juego.flecha:
            texto += " | Tienes una flecha."
        else:
            texto += " | No tienes flechas."
        texto += f" | Dirección: {self.juego.agente_direccion}"
        self.info_label.config(text=texto)

    def manejar_teclas(self, event):
        """Maneja los eventos de las teclas de flecha y otras teclas."""
        if self.juego.juego_terminado:
            return
        tecla = event.keysym
        if tecla == 'Up':
            self.juego.mover_agente('N')
        elif tecla == 'Down':
            self.juego.mover_agente('S')
        elif tecla == 'Right':
            self.juego.mover_agente('E')
        elif tecla == 'Left':
            self.juego.mover_agente('W')
        elif tecla.lower() == 'space':
            self.juego.usar_flecha_funcion()
        elif tecla.lower() == 'r':
            self.juego.reiniciar_juego()
            self.actualizar_visual()
            return
        elif tecla.lower() == 'g':
            self.juego.girar_agente()
        self.actualizar_visual()

    def mostrar_info_celda(self, f, c):
        """Muestra información detallada de una celda específica."""
        celda = self.juego.tablero[f][c]
        info = f"Celda ({f + 1},{c + 1}):\n"
        if celda.agente:
            info += "Agente\n"
        # No mostrar información del Wumpus, hoyos ni oro
        # Solo mostrar percepciones si están presentes
        if celda.hedor:
            info += "Hedor\n"
        if celda.brisa:
            info += "Brisa\n"
        messagebox.showinfo("Información de la Celda", info)

    def iniciar(self):
        """Inicia la interfaz gráfica."""
        self.root.mainloop()


def main():
    juego = JuegoWumpus(filas=6, columnas=6, num_hoyos=3, aleatorio=True)
    gui = GUIWumpus(juego)
    gui.iniciar()


if __name__ == "__main__":
    main()
