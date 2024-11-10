# gui.py
import tkinter as tk
from tkinter import messagebox
from constants import Tile, MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT
from game_logic import TableroWumpus
from minimax import miniMax
import math

class WumpusGUI:
    def __init__(self, root):
        self.root = root
        self.tamano = 6
        self.cell_size = 80
        self.maxLevel = 3
        self.game_running = False
        self.mode = "automatic"
        self.agent_turn = True  # Indica si es el turno del agente

        # Crear el tablero y los componentes de la GUI
        self.setup_gui()
        self.iniciar_nuevo_juego()
        self.draw_board()

    def setup_gui(self):
        """Configura la interfaz gráfica de usuario."""
        # Crear el marco principal
        self.main_frame = tk.Frame(self.root, bg="#2E4053")
        self.main_frame.pack(padx=10, pady=10)

        # Crear el lienzo para el tablero
        self.canvas = tk.Canvas(self.main_frame, width=self.tamano * self.cell_size,
                                height=self.tamano * self.cell_size, bg="#ECF0F1", bd=0, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=5)

        # Crear la barra de estado
        self.status_label = tk.Label(self.main_frame, text="Presiona 'Iniciar' para comenzar el juego.",
                                     font=("Arial", 14), bg="#2E4053", fg="white")
        self.status_label.grid(row=1, column=0, columnspan=5, pady=10)

        # Crear el marco para los botones
        self.button_frame = tk.Frame(self.root, bg="#2E4053")
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

        # Crear la leyenda
        self.create_legend()

    def create_legend(self):
        """Crea una leyenda para explicar los símbolos y colores del tablero."""
        legend_frame = tk.Frame(self.main_frame, bg="#2E4053")
        legend_frame.grid(row=2, column=0, columnspan=5, pady=10)

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
        """Inicia un nuevo juego creando una instancia del tablero."""
        self.tablero = TableroWumpus()
        self.game_running = False
        self.agent_turn = True

    def draw_board(self):
        """Dibuja el tablero en el canvas."""
        self.canvas.delete('all')
        matrix = self.tablero.matrix
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

    def get_tile_color(self, tile: Tile) -> str:
        """Devuelve el color correspondiente a cada tipo de casilla."""
        color_mapping = {
            Tile.BLANCO: "#ECF0F1",          # Gris claro
            Tile.AGENTE: "#00FF00",          # Verde brillante
            Tile.HOYO: "#D35400",            # Naranja
            Tile.WUMPUS: "#E74C3C",          # Rojo
            Tile.ORO: "#F1C40F",             # Amarillo
            Tile.HEDOR: "#95A5A6",           # Gris
            Tile.BRISA: "#2980B9",           # Azul oscuro
            Tile.BRISA_HEDOR: "#3498DB",     # Azul
            Tile.BRISA_ORO: "#F39C12",       # Naranja claro
            Tile.HEDOR_ORO: "#8E44AD",       # Púrpura
            Tile.BRISA_HEDOR_ORO: "#E67E22"  # Naranja medio
        }
        return color_mapping.get(tile, "#ECF0F1")  # Por defecto gris claro

    def add_tile_text(self, i: int, j: int, tile: Tile):
        """Añade texto a la casilla según el tipo de elemento."""
        text = ""
        font_style = ("Arial", 12, "bold")
        text_color = "black"  # Contraste adecuado con fondo claro

        if tile == Tile.AGENTE:
            text = "A"
            text_color = "white"
        elif tile == Tile.HOYO:
            text = "H"
            text_color = "black"
        elif tile == Tile.WUMPUS:
            text = "W"
            text_color = "black"
        elif tile == Tile.ORO:
            text = "O"
            text_color = "black"
        elif tile == Tile.HEDOR:
            text = "He"
            text_color = "black"
        elif tile == Tile.BRISA:
            text = "B"
            text_color = "black"
        elif tile == Tile.BRISA_HEDOR:
            text = "BH"
            text_color = "black"
        elif tile == Tile.BRISA_ORO:
            text = "BO"
            text_color = "black"
        elif tile == Tile.HEDOR_ORO:
            text = "HO"
            text_color = "black"
        elif tile == Tile.BRISA_HEDOR_ORO:
            text = "BHO"
            text_color = "black"

        if text:
            self.canvas.create_text(j * self.cell_size + self.cell_size / 2,
                                    i * self.cell_size + self.cell_size / 2,
                                    text=text, font=font_style, fill=text_color)

    def draw_rounded_rectangle(self, x1, y1, x2, y2, radius=10, **kwargs):
        """Dibuja un rectángulo con esquinas redondeadas en el canvas."""
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
        """Inicia el juego en modo automático."""
        if not self.game_running:
            self.game_running = True
            self.mode = "automatic"
            self.agent_turn = True
            # Deshabilitar botones de modo
            self.start_button.config(state=tk.DISABLED)
            self.sequential_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.DISABLED)
            self.next_move_button.config(state=tk.DISABLED)
            self.status_label.config(text="Juego en curso (Automático)...", fg="yellow")
            self.draw_board()
            self.root.after(1000, self.game_step)  # Iniciar después de 1 segundo

    def activate_sequential_mode(self):
        """Activa el modo secuencial del juego."""
        if not self.game_running:
            self.game_running = True
            self.mode = "sequential"
            self.agent_turn = True
            # Deshabilitar botones de modo
            self.start_button.config(state=tk.DISABLED)
            self.sequential_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.DISABLED)
            # Habilitar botón de siguiente movimiento
            self.next_move_button.config(state=tk.NORMAL)
            self.status_label.config(text="Juego en curso (Secuencial). Presiona 'Siguiente Movimiento' para continuar.", fg="yellow")
            self.draw_board()

    def execute_next_move(self):
        """Ejecuta el siguiente movimiento en modo secuencial."""
        if not self.game_running or self.mode != "sequential":
            return

        if self.tablero.is_game_over():
            self.show_game_over()
            return

        if self.agent_turn:
            # Turno del Agente (Max)
            self.status_label.config(text="Turno del Agente.", fg="black")
            best_value, best_state = miniMax(self.tablero, self.maxLevel, True, -math.inf, math.inf)

            if best_state is not None:
                self.tablero = best_state
                self.draw_board()
                self.status_label.config(text=f"Agente movido. Utilidad: {best_value:.2f}", fg="black")
            else:
                self.status_label.config(text="El agente no tiene movimientos disponibles.", fg="red")

            if self.tablero.is_game_over():
                self.show_game_over()
                return

            self.agent_turn = False
        else:
            # Turno de los Hoyos (Min)
            self.status_label.config(text="Turno de los Hoyos.", fg="black")
            moves = self.tablero.get_available_moves_min()
            if moves:
                # Podrías usar minimax para los hoyos también, pero para simplificar usaremos un movimiento aleatorio
                move = random.choice(moves)
                hoyo_index, new_pos = move
                self.tablero.move_hoyo(hoyo_index, new_pos)
                self.draw_board()
                self.status_label.config(text=f"Hoyo {hoyo_index} movido a {new_pos}.", fg="black")
            else:
                self.status_label.config(text="Los hoyos no tienen movimientos disponibles.", fg="red")

            if self.tablero.is_game_over():
                self.show_game_over()
                return

            self.agent_turn = True

    def game_step(self):
        """Realiza un paso en el juego en modo automático."""
        if not self.game_running:
            return

        if self.tablero.is_game_over():
            self.show_game_over()
            return

        if self.agent_turn:
            # Turno del Agente (Max)
            best_value, best_state = miniMax(self.tablero, self.maxLevel, True, -math.inf, math.inf)

            if best_state is not None:
                self.tablero = best_state
                self.draw_board()
                self.status_label.config(text=f"Agente movido. Utilidad: {best_value:.2f}", fg="black")
            else:
                self.status_label.config(text="El agente no tiene movimientos disponibles.", fg="red")

            if self.tablero.is_game_over():
                self.show_game_over()
                return

            self.agent_turn = False
            # Retraso antes del movimiento de los hoyos
            self.root.after(500, self.game_step)
        else:
            # Turno de los Hoyos (Min)
            moves = self.tablero.get_available_moves_min()
            if moves:
                move = random.choice(moves)
                hoyo_index, new_pos = move
                self.tablero.move_hoyo(hoyo_index, new_pos)
                self.draw_board()
                self.status_label.config(text=f"Hoyo {hoyo_index} movido.", fg="black")
            else:
                self.status_label.config(text="Los hoyos no tienen movimientos disponibles.", fg="red")

            if self.tablero.is_game_over():
                self.show_game_over()
                return

            self.agent_turn = True
            # Retraso antes del siguiente movimiento del agente
            self.root.after(500, self.game_step)

    def show_game_over(self):
        """Muestra el mensaje de fin del juego."""
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
        """Reinicia el juego."""
        # Reiniciar el tablero a un nuevo estado aleatorio
        self.iniciar_nuevo_juego()
        self.draw_board()
        # Deshabilitar botones de modo
        self.restart_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.sequential_button.config(state=tk.NORMAL)
        # Deshabilitar botón de siguiente movimiento
        self.next_move_button.config(state=tk.DISABLED)
        self.status_label.config(text="Presiona 'Iniciar' o 'Modo Secuencial' para comenzar el juego.", fg="white")

# Código para ejecutar la GUI
if __name__ == "__main__":
    import random  # Asegúrate de importar random si no lo has hecho

    root = tk.Tk()
    root.title("Juego del Wumpus")
    root.configure(bg="#2E4053")
    gui = WumpusGUI(root)
    root.mainloop()
