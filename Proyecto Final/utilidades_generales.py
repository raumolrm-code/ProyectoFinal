import tkinter as tk
from tkinter import messagebox
from typing import List, Optional

# Constantes para autómatas
BLANCO_MT = "□"
EPSILON_MT = "ε"
MOVER_DERECHA = 1
MOVER_IZQUIERDA = -1
MOVER_SIN_CAMBIO = 0

# Constante para epsilon en gramáticas (texto)
EPSILON_GRAMATICA = "epsilon"


class NodoArbol:
    """Nodo simple para representar un árbol de derivación (por si quieres usarlo)."""

    def __init__(self, simbolo: str):
        self.simbolo = simbolo
        self.hijos: List["NodoArbol"] = []
        self.lexema: Optional[str] = None
        self.linea: Optional[int] = None
        self.columna: Optional[int] = None

    def agregar_hijo(self, hijo: "NodoArbol") -> None:
        self.hijos.append(hijo)

    def __repr__(self):
        return f"<Nodo: {self.simbolo} (Lex: {self.lexema})>"


class VentanaCentrada:
    """Mezcla para centrar ventanas en pantalla."""

    @staticmethod
    def centrar_ventana(ventana: tk.Misc, ancho: int, alto: int) -> None:
        ventana.update_idletasks()
        ancho_pantalla = ventana.winfo_screenwidth()
        alto_pantalla = ventana.winfo_screenheight()
        x = int(ancho_pantalla / 2 - ancho / 2)
        y = int(alto_pantalla / 2 - alto / 2)
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


class Alerta(VentanaCentrada):
    """Cuadros de mensaje sencillos."""

    @staticmethod
    def mostrar(padre: tk.Misc, titulo: str, mensaje: str) -> None:
        try:
            messagebox.showerror(titulo, mensaje, parent=padre)
        except Exception:
            print(f"ALERTA [{titulo}]: {mensaje}")
