"""
Interfaz grafica del Clash Royale Tracker
Ventana overlay que muestra el elixir y ciclo de cartas del rival
"""

import tkinter as tk
from tkinter import ttk
from config import CARDS, COLORS


class TrackerGUI:
    """
    Interfaz grafica principal del tracker
    Muestra informacion del rival en tiempo real
    """

    def __init__(self, on_start=None, on_stop=None, on_reset=None,
                 on_elixir_mode=None, on_manual_card=None):
        # Callbacks
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_reset = on_reset
        self.on_elixir_mode = on_elixir_mode
        self.on_manual_card = on_manual_card

        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title("CR Tracker")
        self.root.geometry("350x500")
        self.root.configure(bg=COLORS["bg_dark"])

        # Hacer la ventana siempre visible
        self.root.attributes("-topmost", True)

        # Variables de estado
        self.is_running = False

        # Construir interfaz
        self._build_ui()

    def _build_ui(self):
        """Construye los elementos de la interfaz"""

        # === HEADER ===
        header_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        title = tk.Label(header_frame, text="CR Tracker",
                        font=("Helvetica", 16, "bold"),
                        fg=COLORS["text_white"], bg=COLORS["bg_dark"])
        title.pack(side=tk.LEFT)

        # === CONTROLES ===
        control_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        self.start_btn = tk.Button(control_frame, text="Iniciar",
                                   command=self._on_start_click,
                                   bg="#4CAF50", fg="white", width=8)
        self.start_btn.pack(side=tk.LEFT, padx=2)

        self.stop_btn = tk.Button(control_frame, text="Detener",
                                  command=self._on_stop_click,
                                  bg="#f44336", fg="white", width=8,
                                  state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=2)

        self.reset_btn = tk.Button(control_frame, text="Reset",
                                   command=self._on_reset_click,
                                   bg="#2196F3", fg="white", width=8)
        self.reset_btn.pack(side=tk.LEFT, padx=2)

        # === MODO ELIXIR ===
        elixir_mode_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        elixir_mode_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(elixir_mode_frame, text="Modo:",
                fg=COLORS["text_white"], bg=COLORS["bg_dark"]).pack(side=tk.LEFT)

        self.elixir_mode = tk.StringVar(value="normal")

        modes = [("1x", "normal"), ("2x", "double"), ("3x", "triple")]
        for text, mode in modes:
            rb = tk.Radiobutton(elixir_mode_frame, text=text,
                               variable=self.elixir_mode, value=mode,
                               command=self._on_mode_change,
                               fg=COLORS["text_white"], bg=COLORS["bg_dark"],
                               selectcolor=COLORS["bg_dark"],
                               activebackground=COLORS["bg_dark"])
            rb.pack(side=tk.LEFT, padx=5)

        # === BARRA DE ELIXIR ===
        elixir_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        elixir_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(elixir_frame, text="Elixir Rival:",
                font=("Helvetica", 12),
                fg=COLORS["text_white"], bg=COLORS["bg_dark"]).pack(anchor=tk.W)

        # Canvas para barra de elixir
        self.elixir_canvas = tk.Canvas(elixir_frame, width=320, height=30,
                                       bg=COLORS["elixir_bg"], highlightthickness=0)
        self.elixir_canvas.pack(pady=5)

        # Numero de elixir
        self.elixir_label = tk.Label(elixir_frame, text="5",
                                     font=("Helvetica", 24, "bold"),
                                     fg=COLORS["elixir_purple"],
                                     bg=COLORS["bg_dark"])
        self.elixir_label.pack()

        # === MAZO RIVAL ===
        deck_frame = tk.LabelFrame(self.root, text="Mazo Rival (0/8)",
                                   fg=COLORS["text_white"], bg=COLORS["bg_dark"],
                                   font=("Helvetica", 10))
        deck_frame.pack(fill=tk.X, padx=10, pady=5)
        self.deck_frame = deck_frame

        # Grid de cartas conocidas
        self.deck_cards_frame = tk.Frame(deck_frame, bg=COLORS["bg_dark"])
        self.deck_cards_frame.pack(fill=tk.X, padx=5, pady=5)

        self.deck_labels = []
        for i in range(8):
            lbl = tk.Label(self.deck_cards_frame, text="?",
                          width=8, height=2,
                          bg=COLORS["card_unknown"], fg="white",
                          font=("Helvetica", 8))
            lbl.grid(row=i//4, column=i%4, padx=2, pady=2)
            self.deck_labels.append(lbl)

        # === EN MANO ===
        hand_frame = tk.LabelFrame(self.root, text="En Mano (estimado)",
                                   fg=COLORS["text_white"], bg=COLORS["bg_dark"],
                                   font=("Helvetica", 10))
        hand_frame.pack(fill=tk.X, padx=10, pady=5)

        self.hand_cards_frame = tk.Frame(hand_frame, bg=COLORS["bg_dark"])
        self.hand_cards_frame.pack(fill=tk.X, padx=5, pady=5)

        self.hand_labels = []
        for i in range(4):
            lbl = tk.Label(self.hand_cards_frame, text="?",
                          width=10, height=2,
                          bg=COLORS["card_unknown"], fg="white",
                          font=("Helvetica", 8))
            lbl.grid(row=0, column=i, padx=2, pady=2)
            self.hand_labels.append(lbl)

        # === ULTIMAS JUGADAS ===
        history_frame = tk.LabelFrame(self.root, text="Ultimas Jugadas",
                                      fg=COLORS["text_white"], bg=COLORS["bg_dark"],
                                      font=("Helvetica", 10))
        history_frame.pack(fill=tk.X, padx=10, pady=5)

        self.history_text = tk.Text(history_frame, height=4, width=40,
                                    bg=COLORS["bg_dark"], fg=COLORS["text_white"],
                                    font=("Courier", 9), state=tk.DISABLED)
        self.history_text.pack(padx=5, pady=5)

        # === INPUT MANUAL ===
        manual_frame = tk.LabelFrame(self.root, text="Input Manual",
                                     fg=COLORS["text_white"], bg=COLORS["bg_dark"],
                                     font=("Helvetica", 10))
        manual_frame.pack(fill=tk.X, padx=10, pady=5)

        self.card_var = tk.StringVar()
        self.card_combo = ttk.Combobox(manual_frame, textvariable=self.card_var,
                                       width=25, state="readonly")

        # Lista de cartas para el combobox
        card_names = sorted([f"{info['name']} ({info['elixir']})"
                            for name, info in CARDS.items()])
        self.card_combo["values"] = card_names
        self.card_combo.pack(side=tk.LEFT, padx=5, pady=5)

        self.add_card_btn = tk.Button(manual_frame, text="Agregar",
                                      command=self._on_manual_card,
                                      bg="#FF9800", fg="white")
        self.add_card_btn.pack(side=tk.LEFT, padx=5)

        # Crear mapeo inverso para el combobox
        self._card_name_map = {}
        for name, info in CARDS.items():
            display = f"{info['name']} ({info['elixir']})"
            self._card_name_map[display] = name

        # === STATUS ===
        self.status_label = tk.Label(self.root, text="Estado: Detenido",
                                     fg=COLORS["text_white"], bg=COLORS["bg_dark"],
                                     font=("Helvetica", 9))
        self.status_label.pack(side=tk.BOTTOM, pady=5)

    def _on_start_click(self):
        """Callback para boton iniciar"""
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Estado: Rastreando...")
        if self.on_start:
            self.on_start()

    def _on_stop_click(self):
        """Callback para boton detener"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Estado: Detenido")
        if self.on_stop:
            self.on_stop()

    def _on_reset_click(self):
        """Callback para boton reset"""
        self._reset_display()
        if self.on_reset:
            self.on_reset()

    def _on_mode_change(self):
        """Callback para cambio de modo de elixir"""
        if self.on_elixir_mode:
            self.on_elixir_mode(self.elixir_mode.get())

    def _on_manual_card(self):
        """Callback para agregar carta manual"""
        selected = self.card_var.get()
        if selected and selected in self._card_name_map:
            card_name = self._card_name_map[selected]
            if self.on_manual_card:
                self.on_manual_card(card_name)
            self.card_var.set("")

    def _reset_display(self):
        """Resetea la visualizacion"""
        self.update_elixir(5)

        for lbl in self.deck_labels:
            lbl.config(text="?", bg=COLORS["card_unknown"])

        for lbl in self.hand_labels:
            lbl.config(text="?", bg=COLORS["card_unknown"])

        self.deck_frame.config(text="Mazo Rival (0/8)")

        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)

    def update_elixir(self, elixir):
        """Actualiza la barra y numero de elixir"""
        elixir = max(0, min(10, elixir))

        # Actualizar numero
        self.elixir_label.config(text=str(int(elixir)))

        # Actualizar barra
        self.elixir_canvas.delete("all")
        bar_width = (elixir / 10) * 310
        self.elixir_canvas.create_rectangle(5, 5, 5 + bar_width, 25,
                                           fill=COLORS["elixir_purple"],
                                           outline="")

        # Marcas de cada elixir
        for i in range(1, 10):
            x = 5 + (i * 31)
            self.elixir_canvas.create_line(x, 5, x, 25, fill="#555")

    def update_deck(self, known_cards, progress):
        """Actualiza la visualizacion del mazo rival"""
        self.deck_frame.config(text=f"Mazo Rival ({progress}/8)")

        for i, lbl in enumerate(self.deck_labels):
            if i < len(known_cards):
                card_name = known_cards[i]
                if card_name in CARDS:
                    display = CARDS[card_name]["name"][:8]
                    elixir = CARDS[card_name]["elixir"]
                    lbl.config(text=f"{display}\n({elixir})",
                              bg=COLORS["card_known"])
            else:
                lbl.config(text="?", bg=COLORS["card_unknown"])

    def update_hand(self, cards_in_hand):
        """Actualiza las cartas estimadas en mano"""
        for i, lbl in enumerate(self.hand_labels):
            if i < len(cards_in_hand):
                card_name = cards_in_hand[i]
                if card_name in CARDS:
                    display = CARDS[card_name]["name"][:10]
                    lbl.config(text=display, bg=COLORS["highlight"])
            else:
                lbl.config(text="?", bg=COLORS["card_unknown"])

    def update_history(self, last_played):
        """Actualiza el historial de cartas jugadas"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)

        for card_name in reversed(last_played):
            if card_name in CARDS:
                info = CARDS[card_name]
                line = f"► {info['name']} ({info['elixir']} elixir)\n"
                self.history_text.insert(tk.END, line)

        self.history_text.config(state=tk.DISABLED)

    def update_from_status(self, status):
        """
        Actualiza toda la interfaz desde un diccionario de estado

        Args:
            status: Dict con las claves de GameTracker.get_status()
        """
        self.update_elixir(status["elixir"])
        self.update_deck(status["known_cards"], status["deck_progress"])
        self.update_hand(status["cards_in_hand"])
        self.update_history(status["last_played"])

    def run(self):
        """Inicia el loop principal de la interfaz"""
        self.root.mainloop()

    def schedule_update(self, callback, ms=100):
        """Programa una actualizacion periodica"""
        self.root.after(ms, callback)

    def close(self):
        """Cierra la ventana"""
        self.root.quit()
        self.root.destroy()


def test_gui():
    """Prueba la interfaz grafica"""
    import time

    def on_start():
        print("Iniciando tracker...")

    def on_stop():
        print("Deteniendo tracker...")

    def on_reset():
        print("Reseteando...")

    def on_mode(mode):
        print(f"Modo: {mode}")

    def on_card(card):
        print(f"Carta manual: {card}")

    gui = TrackerGUI(
        on_start=on_start,
        on_stop=on_stop,
        on_reset=on_reset,
        on_elixir_mode=on_mode,
        on_manual_card=on_card
    )

    # Simular actualizaciones
    def update_test():
        gui.update_elixir(7)
        gui.update_deck(["knight", "fireball", "hog_rider"], 3)
        gui.update_hand(["knight", "fireball"])
        gui.update_history(["knight", "fireball", "arrows"])

    gui.root.after(1000, update_test)
    gui.run()


if __name__ == "__main__":
    test_gui()
