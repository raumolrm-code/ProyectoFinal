import tkinter as tk
from tkinter import scrolledtext

from utilidades_generales import VentanaCentrada, Alerta
from estructuras_gramatica import leer_gramatica_desde_texto
from equivalencias import comparar_gramaticas


class VentanaEquivalencias(tk.Toplevel, VentanaCentrada):
    """
    Ventana para comparar dos gramáticas y estimar si son equivalentes
    (hasta cierta longitud n, de forma heurística).
    """

    def __init__(self, master):
        super().__init__(master)
        self.title("Comparador de Equivalencia de Gramáticas")
        self.configure(bg="#b9ede2")
        self.centrar_ventana(self, 1000, 620)
        self._construir_interfaz()

    def _construir_interfaz(self):
        marco = tk.Frame(self, bg="#b9ede2")
        marco.pack(fill="both", expand=True, padx=10, pady=10)
        marco.grid_rowconfigure(1, weight=1)
        marco.grid_columnconfigure(0, weight=1)
        marco.grid_columnconfigure(1, weight=1)

        tk.Label(
            marco,
            text="Gramática 1",
            bg="#b9ede2",
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            marco,
            text="Gramática 2",
            bg="#b9ede2",
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=1, sticky="w")

        self.caja_g1 = scrolledtext.ScrolledText(
            marco, font=("Consolas", 11), wrap="word"
        )
        self.caja_g1.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        self.caja_g2 = scrolledtext.ScrolledText(
            marco, font=("Consolas", 11), wrap="word"
        )
        self.caja_g2.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

        # Ejemplo inicial
        self.caja_g1.insert("1.0", "S -> a A\nA -> b\n")
        self.caja_g2.insert("1.0", "S -> a b\n")

        panel_inferior = tk.Frame(marco, bg="#b9ede2")
        panel_inferior.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        tk.Label(panel_inferior, text="Longitud máxima n:", bg="#b9ede2").pack(
            side="left"
        )

        self.spin_n = tk.Spinbox(panel_inferior, from_=1, to=10, width=5)
        self.spin_n.pack(side="left", padx=5)
        self.spin_n.delete(0, "end")
        self.spin_n.insert(0, "5")

        tk.Button(
            panel_inferior,
            text="Comparar Gramáticas",
            bg="#c9c695",
            font=("Segoe UI", 11, "bold"),
            command=self.ejecutar_comparacion,
        ).pack(side="left", padx=10)

        self.etiqueta_resultado = tk.Label(
            marco,
            text="Resultado de la comparación...",
            bg="#e0e0e0",
            wraplength=950,
            justify="left",
        )
        self.etiqueta_resultado.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

    def ejecutar_comparacion(self):
        texto1 = self.caja_g1.get("1.0", "end")
        texto2 = self.caja_g2.get("1.0", "end")

        try:
            n = int(self.spin_n.get())
        except ValueError:
            Alerta.mostrar(self, "Error", "La longitud n debe ser un número entero.")
            return

        try:
            g1 = leer_gramatica_desde_texto(texto1)
        except Exception as e:
            Alerta.mostrar(self, "Error en Gramática 1", str(e))
            return

        try:
            g2 = leer_gramatica_desde_texto(texto2)
        except Exception as e:
            Alerta.mostrar(self, "Error en Gramática 2", str(e))
            return

        son_eq, mensaje = comparar_gramaticas(g1, g2, n_max=n)
        self.etiqueta_resultado.config(
            text=mensaje,
            fg="green" if son_eq else "red",
        )
