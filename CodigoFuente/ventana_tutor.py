import tkinter as tk
from tkinter import scrolledtext

from utilidades_generales import VentanaCentrada
from ejemplos_y_tutor import ModoTutor


class VentanaTutor(tk.Toplevel, VentanaCentrada):
    """
    Ventana del modo tutor:
    - Muestra una gramática generada por el agente.
    - El usuario selecciona el tipo (0,1,2,3).
    - Se muestra retroalimentación inmediata.
    """

    def __init__(self, master):
        super().__init__(master)
        self.title("Modo Tutor (Quiz) - Chomsky Classifier AI")
        self.configure(bg="#b9ede2")
        self.centrar_ventana(self, 750, 550)

        self.modo = ModoTutor()

        self._construir_interfaz()
        self.cargar_nuevo_ejercicio()

    def _construir_interfaz(self):
        tk.Label(
            self,
            text="Modo Tutor: Clasifica la gramática mostrada",
            bg="#b9ede2",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(10, 5))

        self.caja_gramatica = scrolledtext.ScrolledText(
            self, font=("Consolas", 11), wrap="word", height=10
        )
        self.caja_gramatica.pack(fill="x", padx=10)
        self.caja_gramatica.config(state="disabled")

        marco_botones = tk.Frame(self, bg="#b9ede2")
        marco_botones.pack(pady=10)

        tk.Button(
            marco_botones,
            text="Tipo 0",
            width=8,
            bg="#c9c695",
            command=lambda: self._verificar(0),
        ).pack(side="left", padx=4)
        tk.Button(
            marco_botones,
            text="Tipo 1",
            width=8,
            bg="#c9c695",
            command=lambda: self._verificar(1),
        ).pack(side="left", padx=4)
        tk.Button(
            marco_botones,
            text="Tipo 2",
            width=8,
            bg="#c9c695",
            command=lambda: self._verificar(2),
        ).pack(side="left", padx=4)
        tk.Button(
            marco_botones,
            text="Tipo 3",
            width=8,
            bg="#c9c695",
            command=lambda: self._verificar(3),
        ).pack(side="left", padx=4)

        self.etiqueta_feedback = tk.Label(
            self,
            text="Selecciona un tipo para evaluar tu respuesta.",
            bg="#e0e0e0",
            font=("Segoe UI", 10),
            wraplength=700,
            justify="left",
        )
        self.etiqueta_feedback.pack(fill="x", padx=10, pady=(5, 10))

        tk.Button(
            self,
            text="Nueva Gramática",
            bg="#c9c695",
            font=("Segoe UI", 11, "bold"),
            command=self.cargar_nuevo_ejercicio,
        ).pack(pady=(0, 10))

    def cargar_nuevo_ejercicio(self):
        texto = self.modo.generar_ejercicio()
        self.caja_gramatica.config(state="normal")
        self.caja_gramatica.delete("1.0", "end")
        self.caja_gramatica.insert("1.0", texto)
        self.caja_gramatica.config(state="disabled")
        self.etiqueta_feedback.config(
            text="Nueva gramática generada. Elige qué tipo crees que es.",
            fg="black",
        )

    def _verificar(self, tipo: int):
        es_correcta, mensaje = self.modo.verificar_respuesta(tipo)
        self.etiqueta_feedback.config(
            text=mensaje,
            fg="green" if es_correcta else "red",
        )
