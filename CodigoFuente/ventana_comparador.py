import tkinter as tk
from tkinter import scrolledtext

from utilidades_generales import VentanaCentrada, Alerta
from analizador_lexico_gramaticas import AnalizadorLexicoGramaticas
from motor_ll1 import GeneradorTablaLL1, analizar_sintactico
from estructuras_gramatica import (
    GRAMATICA_DE_GRAMATICAS,
    SIMBOLO_INICIAL_GRAMATICA,
    extraer_producciones,
)
from equivalencias import comparar_gramaticas


class VentanaComparadorEquivalencia(tk.Toplevel, VentanaCentrada):
    """Ventana para comparar dos gramáticas (equivalencia heurística)."""

    def __init__(self, padre):
        super().__init__(padre)
        self.title("4. Comparador de Equivalencia")
        self.configure(bg="#b9ede2")
        self.centrar_ventana(self, 900, 600)

        self.analizador_lexico = AnalizadorLexicoGramaticas()
        self.generador_tabla = GeneradorTablaLL1(GRAMATICA_DE_GRAMATICAS, SIMBOLO_INICIAL_GRAMATICA)
        self.tabla_M = self.generador_tabla.construir_tabla()

        self._crear_interfaz()

    def _crear_interfaz(self):
        marco_principal = tk.Frame(self, bg="#b9ede2")
        marco_principal.pack(fill="both", expand=True, padx=10, pady=10)
        marco_principal.grid_rowconfigure(1, weight=1)
        marco_principal.grid_columnconfigure(0, weight=1)
        marco_principal.grid_columnconfigure(1, weight=1)

        tk.Label(
            marco_principal,
            text="Gramática 1",
            font=("Times New Roman", 14, "bold"),
            bg="#b9ede2",
        ).grid(row=0, column=0, sticky="w")
        self.caja_g1 = scrolledtext.ScrolledText(
            marco_principal, font=("Courier", 11), wrap="word", height=10
        )
        self.caja_g1.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        tk.Label(
            marco_principal,
            text="Gramática 2",
            font=("Times New Roman", 14, "bold"),
            bg="#b9ede2",
        ).grid(row=0, column=1, sticky="w")
        self.caja_g2 = scrolledtext.ScrolledText(
            marco_principal, font=("Courier", 11), wrap="word", height=10
        )
        self.caja_g2.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

        # Ejemplos base
        self.caja_g1.insert("1.0", "S -> a A\nA -> b")
        self.caja_g2.insert("1.0", "S -> a b")

        # Parte inferior
        marco_inferior = tk.Frame(marco_principal, bg="#b9ede2")
        marco_inferior.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="w")

        tk.Label(marco_inferior, text="Longitud máxima (n):", bg="#b9ede2").pack(side="left")
        self.entrada_n = tk.Spinbox(marco_inferior, from_=1, to=10, width=5)
        self.entrada_n.pack(side="left", padx=5)
        self.entrada_n.delete(0, "end")
        self.entrada_n.insert(0, "5")

        tk.Button(
            marco_inferior,
            text="Comparar Gramáticas",
            command=self.ejecutar_comparacion,
            font=("Times New Roman", 12, "bold"),
            bg="#c9c695",
        ).pack(side="left", padx=10)

        self.etiqueta_resultado = tk.Label(
            marco_principal,
            text="Resultado de la comparación...",
            bg="#e0e0e0",
            wraplength=850,
            justify="left",
        )
        self.etiqueta_resultado.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky="ew")

    def _parsear_gramatica(self, texto: str):
        tokens = []
        for i, linea in enumerate(texto.splitlines()):
            tokens.extend(
                [t for t in self.analizador_lexico.tokenizar_linea(linea, i + 1) if t[1] != "INVALIDO"]
            )

        arbol, error = analizar_sintactico(
            tokens,
            self.tabla_M,
            SIMBOLO_INICIAL_GRAMATICA,
            self.generador_tabla.FIRST,
            self.generador_tabla.FOLLOW,
        )
        if error:
            Alerta.mostrar(self, "Error de Parseo", f"No se pudo analizar la gramática:\n{error}")
            return None

        producciones = extraer_producciones(arbol)
        if not producciones:
            Alerta.mostrar(self, "Error de Parseo", "No se extrajeron producciones.")
            return None

        return producciones

    def ejecutar_comparacion(self):
        texto_g1 = self.caja_g1.get("1.0", tk.END)
        texto_g2 = self.caja_g2.get("1.0", tk.END)

        try:
            n = int(self.entrada_n.get())
        except ValueError:
            Alerta.mostrar(self, "Error", "La longitud máxima debe ser un número entero.")
            return

        g1 = self._parsear_gramatica(texto_g1)
        if not g1:
            return
        g2 = self._parsear_gramatica(texto_g2)
        if not g2:
            return

        equivalentes, texto = comparar_gramaticas(g1, g2, n)
        self.etiqueta_resultado.config(text=texto, fg="green" if equivalentes else "red")
