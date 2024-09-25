import tkinter as tk
import random
from tkinter import messagebox
import time
import threading
from collections import deque
import math

# Definir direcciones
DIRECCIONES = ['N', 'W', 'S', 'E']  # Norte, Oeste, Sur, Este

class Celda:
    """Clase que representa cada celda del tablero. y nada mas"""

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
        self.puntuacion = 0  # Sistema de puntuación
        self.colocar_agente()
        self.colocar_elementos()
        self.modo_manual = True  # Por defecto, modo manual
        self.modo_automatico = False
        self.gui = None  # Referencia a la GUI (será asignada después)

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
            if (fila, col) != self.agente_pos and not self.tablero[fila][col].wumpus and not self.tablero[fila][col].hoyo:
                # Verificar que no esté contiguo al Wumpus
                if not self.adyacente(fila, col, self.wumpus_pos[0], self.wumpus_pos[1]):
                    self.tablero[fila][col].hoyo = True
                    self.actualizar_percepciones(fila, col, tipo='hoyo')
                    colocados += 1

        # Colocar Oro
        while True:
            fila = random.randint(0, self.filas - 1)
            col = random.randint(0, self.columnas - 1)
            if (fila, col) != self.agente_pos and not self.tablero[fila][col].wumpus and not self.tablero[fila][col].hoyo:
                self.tablero[fila][col].oro = True
                self.oro_pos = (fila, col)
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
            self.puntuacion -= 1  # Penalización por movimiento
            self.verificar_celda()
            if self.gui:
                self.gui.actualizar_visual()
        else:
            # Si sale del tablero, revertir
            self.tablero[fila][col].agente = True
            if self.gui:
                self.gui.actualizar_visual()
            messagebox.showinfo("Movimiento inválido", "No puedes salir del tablero.")

    def girar_agente(self):
        """Gira al agente 90 grados en sentido contrario a las agujas del reloj."""
        idx = DIRECCIONES.index(self.agente_direccion)
        nueva_direccion = DIRECCIONES[(idx + 1) % 4]
        self.agente_direccion = nueva_direccion
        if self.gui:
            self.gui.actualizar_visual()

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
                    self.tablero[f][col_agente].hedor = False
                    messagebox.showinfo("Flecha", "¡Has matado al Wumpus!")
                    self.puntuacion += 50  # Bonificación por matar al Wumpus
                    self.juego_terminado = True
                    self.ganar = True
                    if self.gui:
                        self.gui.actualizar_visual()
                    return
        elif direccion == 'S':
            rango = range(fila_agente + 1, self.filas)
            for f in rango:
                if self.tablero[f][col_agente].wumpus:
                    self.wumpus_vivo = False
                    self.tablero[f][col_agente].wumpus = False
                    self.tablero[f][col_agente].hedor = False
                    messagebox.showinfo("Flecha", "¡Has matado al Wumpus!")
                    self.puntuacion += 50  # Bonificación por matar al Wumpus
                    self.juego_terminado = True
                    self.ganar = True
                    if self.gui:
                        self.gui.actualizar_visual()
                    return
        elif direccion == 'E':
            rango = range(col_agente + 1, self.columnas)
            for c in rango:
                if self.tablero[fila_agente][c].wumpus:
                    self.wumpus_vivo = False
                    self.tablero[fila_agente][c].wumpus = False
                    self.tablero[fila_agente][c].hedor = False
                    messagebox.showinfo("Flecha", "¡Has matado al Wumpus!")
                    self.puntuacion += 50  # Bonificación por matar al Wumpus
                    self.juego_terminado = True
                    self.ganar = True
                    if self.gui:
                        self.gui.actualizar_visual()
                    return
        elif direccion == 'W':
            rango = range(col_agente - 1, -1, -1)
            for c in rango:
                if self.tablero[fila_agente][c].wumpus:
                    self.wumpus_vivo = False
                    self.tablero[fila_agente][c].wumpus = False
                    self.tablero[fila_agente][c].hedor = False
                    messagebox.showinfo("Flecha", "¡Has matado al Wumpus!")
                    self.puntuacion += 50  # Bonificación por matar al Wumpus
                    self.juego_terminado = True
                    self.ganar = True
                    if self.gui:
                        self.gui.actualizar_visual()
                    return
        messagebox.showinfo("Flecha", "Has usado tu flecha.")
        if self.gui:
            self.gui.actualizar_visual()

    def verificar_celda(self):
        """Verifica el estado de la celda donde está el agente."""
        fila, col = self.agente_pos
        celda = self.tablero[fila][col]

        # Si hay Wumpus y está vivo
        if celda.wumpus and self.wumpus_vivo:
            self.juego_terminado = True
            messagebox.showinfo("¡Perdiste!", "Has sido matado por el Wumpus.")
            if self.gui:
                self.gui.actualizar_visual()
            return

        # Si hay un hoyo
        if celda.hoyo:
            self.juego_terminado = True
            messagebox.showinfo("¡Perdiste!", "Has caído en un hoyo.")
            if self.gui:
                self.gui.actualizar_visual()
            return

        # Si hay oro
        if celda.oro:
            self.juego_terminado = True
            self.ganar = True
            messagebox.showinfo("¡Ganaste!", "¡Has encontrado el oro y ganado el juego!")
            self.puntuacion += 100  # Bonificación por encontrar el oro
            if self.gui:
                self.gui.actualizar_visual()
            return

    def reiniciar_juego(self):
        """Reinicia el juego."""
        # Resetear todas las celdas
        self.tablero = [[Celda() for _ in range(self.columnas)] for _ in range(self.filas)]
        self.agente_pos = (self.filas - 1, 0)
        self.agente_direccion = 'E'
        self.flecha = True
        self.wumpus_vivo = True
        self.juego_terminado = False
        self.ganar = False
        self.puntuacion = 0  # Reiniciar puntuación
        self.colocar_agente()
        self.colocar_elementos()
        self.modo_manual = True
        self.modo_automatico = False
        if self.gui:
            self.gui.actualizar_visual()
            self.gui.info_label.config(text="Juego reiniciado. Elige un modo para comenzar.")

class AgenteInteligente:
    """Clase que representa al agente inteligente que juega automáticamente usando A*."""

    def __init__(self, juego):
        self.juego = juego
        self.gui = juego.gui  # Referencia a la GUI
        self.conocido = {}  # Mapa de celdas conocidas: (fila, col) -> {'visited': bool, 'safe': bool, 'wumpus_possible': bool, 'hoyo_possible': bool}
        self.queue = deque()  # Cola para BFS
        self.direccion = self.juego.agente_direccion
        self.running = True  # Control para detener el agente al reiniciar
        self.celdas_visitadas = []  # Ruta tomada

        # Inicializar el conocimiento con la posición inicial
        fila, col = self.juego.agente_pos
        self.conocido[(fila, col)] = {'visited': True, 'safe': True}
        self.queue.append((fila, col))
        self.celdas_visitadas.append((fila, col))

    def ejecutar(self):
        """Ejecuta el agente en un hilo separado."""
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        """Método principal del agente que toma decisiones usando A*. """
        while not self.juego.juego_terminado and self.running and self.queue:
            current = self.queue.popleft()
            fila, col = current

            # Mover al agente a la celda actual
            self.mover_a(fila, col)
            if self.juego.juego_terminado or not self.running:
                break

            # Obtener percepciones en la celda actual
            percepciones = self.obtener_percepciones(fila, col)

            # Actualizar el conocimiento
            self.actualizar_conocimiento(fila, col, percepciones)

            # Decidir el siguiente movimiento basado en A*
            siguientes = self.obtener_celdas_seguras()

            for s in siguientes:
                if s not in self.conocido or not self.conocido[s].get('visited', False):
                    self.queue.append(s)
                    self.celdas_visitadas.append(s)

            time.sleep(0.5)  # Pausa para visualizar los movimientos

    def mover_a(self, fila, col):
        """Calcula la dirección para moverse a la celda (fila, col) y realiza el movimiento."""
        current_fila, current_col = self.juego.agente_pos
        direccion = None

        if fila < current_fila:
            direccion = 'N'
        elif fila > current_fila:
            direccion = 'S'
        elif col < current_col:
            direccion = 'W'
        elif col > current_col:
            direccion = 'E'

        if direccion:
            self.juego.mover_agente(direccion)
            self.juego.agente_direccion = direccion  # Actualizar la dirección del agente
            self.juego.gui.actualizar_visual()

    def obtener_percepciones(self, fila, col):
        """Obtiene las percepciones en la celda actual."""
        celda = self.juego.tablero[fila][col]
        percepciones = []
        if celda.hedor:
            percepciones.append('hedor')
        if celda.brisa:
            percepciones.append('brisa')
        return percepciones

    def actualizar_conocimiento(self, fila, col, percepciones):
        """Actualiza el conocimiento del agente basado en las percepciones."""
        # Marcar la celda como visitada y segura
        self.conocido[(fila, col)]['visited'] = True
        self.conocido[(fila, col)]['safe'] = True

        # Obtener adyacentes
        adyacentes = self.juego.obtener_adyacentes(fila, col)

        if 'hedor' in percepciones:
            # Posibles posiciones del Wumpus
            for f, c in adyacentes:
                if (f, c) not in self.conocido:
                    self.conocido[(f, c)] = {}
                self.conocido[(f, c)]['wumpus_possible'] = True
        else:
            # Las celdas adyacentes no tienen Wumpus
            for f, c in adyacentes:
                if (f, c) not in self.conocido:
                    self.conocido[(f, c)] = {}
                self.conocido[(f, c)]['wumpus_possible'] = False

        if 'brisa' in percepciones:
            # Posibles posiciones de hoyos
            for f, c in adyacentes:
                if (f, c) not in self.conocido:
                    self.conocido[(f, c)] = {}
                self.conocido[(f, c)]['hoyo_possible'] = True
        else:
            # Las celdas adyacentes no tienen hoyos
            for f, c in adyacentes:
                if (f, c) not in self.conocido:
                    self.conocido[(f, c)] = {}
                self.conocido[(f, c)]['hoyo_possible'] = False

        # Determinar celdas seguras para explorar
        for f, c in adyacentes:
            if (f, c) not in self.conocido:
                self.conocido[(f, c)] = {}
            if (not self.conocido[(f, c)].get('wumpus_possible', False) and
                    not self.conocido[(f, c)].get('hoyo_possible', False)):
                self.conocido[(f, c)]['safe'] = True
                self.conocido[(f, c)]['visited'] = False

    def obtener_celdas_seguras(self):
        """Devuelve una lista de celdas que son seguras para explorar."""
        seguras = []
        for (f, c), info in self.conocido.items():
            if info.get('safe', False) and not info.get('visited', False):
                seguras.append((f, c))
        return seguras

    def detener(self):
        """Detiene la ejecución del agente."""
        self.running = False

class GUIWumpus:
    """Clase que maneja la interfaz gráfica del juego Wumpus."""

    def __init__(self, juego):
        self.juego = juego
        self.juego.gui = self  # Asignar referencia de la GUI al juego
        self.root = tk.Tk()
        self.root.title("Juego Wumpus Mejorado")
        self.crear_tablero()
        self.crear_info()
        self.crear_controles()  # Añadido
        self.actualizar_visual()
        self.root.bind("<Key>", self.manejar_teclas)
        self.agente_inteligente = None  # Inicializar como None

    def crear_tablero(self):
        """Crea el tablero visual usando botones."""
        self.botones = [[None for _ in range(self.juego.columnas)] for _ in range(self.juego.filas)]
        for f in range(self.juego.filas):
            for c in range(self.juego.columnas):
                btn = tk.Button(
                    self.root,
                    width=4,
                    height=2,
                    command=lambda row=f, col=c: self.mostrar_info_celda(row, col),
                    state="disabled",
                    font=("Helvetica", 12, "bold")
                )
                btn.grid(row=f, column=c, padx=2, pady=2)
                self.botones[f][c] = btn

    def crear_info(self):
        """Crea un área de información para mostrar percepciones y puntuación."""
        self.info_label = tk.Label(self.root, text="Usa las flechas para mover al agente o elige un modo.", font=("Helvetica", 12))
        self.info_label.grid(row=self.juego.filas, column=0, columnspan=self.juego.columnas, pady=10)

        self.score_label = tk.Label(self.root, text=f"Puntuación: {self.juego.puntuacion}", font=("Helvetica", 12))
        self.score_label.grid(row=self.juego.filas + 1, column=0, columnspan=self.juego.columnas, pady=5)

    def crear_controles(self):
        """Crea los controles para seleccionar el modo de juego."""
        controles_frame = tk.Frame(self.root)
        controles_frame.grid(row=self.juego.filas + 2, column=0, columnspan=self.juego.columnas, pady=10)

        btn_manual = tk.Button(controles_frame, text="Modo Manual", command=self.activar_modo_manual, bg="lightblue")
        btn_manual.pack(side="left", padx=5)

        btn_automatico = tk.Button(controles_frame, text="Modo Automático", command=self.activar_modo_automatico, bg="lightgreen")
        btn_automatico.pack(side="left", padx=5)

        btn_reiniciar = tk.Button(controles_frame, text="Reiniciar Juego", command=self.reiniciar_juego_gui, bg="lightcoral")
        btn_reiniciar.pack(side="left", padx=5)

    def activar_modo_manual(self):
        """Activa el modo de juego manual."""
        if self.juego.modo_automatico and self.agente_inteligente:
            # Detener el agente inteligente si está activo
            self.agente_inteligente.detener()
            self.agente_inteligente = None
        self.juego.modo_manual = True
        self.juego.modo_automatico = False
        self.info_label.config(text="Modo Manual Activado. Usa las flechas para mover al agente.")
        self.score_label.config(text=f"Puntuación: {self.juego.puntuacion}")

    def activar_modo_automatico(self):
        """Activa el modo de juego automático."""
        if not self.agente_inteligente:
            self.agente_inteligente = AgenteInteligente(self.juego)
            self.agente_inteligente.ejecutar()
        self.juego.modo_manual = False
        self.juego.modo_automatico = True
        self.info_label.config(text="Modo Automático Activado. El agente está tomando decisiones.")
        self.score_label.config(text=f"Puntuación: {self.juego.puntuacion}")

    def reiniciar_juego_gui(self):
        """Reinicia el juego desde la interfaz gráfica."""
        if self.agente_inteligente:
            self.agente_inteligente.detener()
            self.agente_inteligente = None
        self.juego.reiniciar_juego()
        self.actualizar_visual()
        self.info_label.config(text="Juego reiniciado. Elige un modo para comenzar.")
        self.score_label.config(text=f"Puntuación: {self.juego.puntuacion}")

    def manejar_teclas(self, event):
        """Maneja los eventos de las teclas de flecha y otras teclas."""
        if self.juego.juego_terminado:
            return
        if self.juego.modo_manual:
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
                self.reiniciar_juego_gui()
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
                    btn.config(bg="blue", fg="white", text=text)
                elif self.juego.juego_terminado:
                    # Revelar todos los elementos al finalizar el juego
                    if celda.wumpus and self.juego.wumpus_vivo:
                        btn.config(bg="red", fg="white", text="W")
                    elif celda.hoyo:
                        btn.config(bg="black", fg="white", text="H")
                    elif celda.oro:
                        btn.config(bg="yellow", fg="black", text="O")
                    else:
                        btn.config(bg="lightgrey", text="")
                else:
                    btn.config(bg="lightgrey", text="")

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

        # Actualizar puntuación
        self.score_label.config(text=f"Puntuación: {self.juego.puntuacion}")

    def iniciar(self):
        """Inicia la interfaz gráfica."""
        self.root.mainloop()

def main():
    juego = JuegoWumpus(filas=6, columnas=6, num_hoyos=3, aleatorio=True)
    gui = GUIWumpus(juego)
    juego.gui = gui  # Asignar la GUI al juego
    gui.iniciar()

if __name__ == "__main__":
    main()
