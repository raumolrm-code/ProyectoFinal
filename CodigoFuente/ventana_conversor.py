import tkinter as tk
from tkinter import scrolledtext

from utilidades_generales import VentanaCentrada, Alerta
from estructuras_gramatica import (
    leer_gramatica_desde_texto,
    producciones_a_texto,
)
from conversor_y_diagramas import (
    expresion_regular_a_nfa,
    convertir_nfa_a_afd,
    convertir_afd_a_gramatica,
    convertir_gramatica_a_nfa,
    obtener_alfabeto_desde_nfa,
    convertir_afd_a_expresion_regular,
    dibujar_automata,
    mostrar_imagen_en_ventana,
)
from automatas_ejemplo import DefinicionesAutomatas


class VentanaConversor(tk.Toplevel, VentanaCentrada):
    """
    Ventana para conversión entre:
      - Expresión Regular → AFN → AFD → Gramática Regular
      - Gramática Regular → NFA → AFD → Expresión Regular
      - AFD de ejemplo → Gramática / Diagrama
    """

    def __init__(self, master):
        super().__init__(master)
        self.title("Conversor de Modelos - Chomsky Classifier AI")
        self.configure(bg="#b9ede2")
        self.centrar_ventana(self, 1000, 620)
        self._construir_interfaz()

    def _construir_interfaz(self):
        marco = tk.Frame(self, bg="#b9ede2")
        marco.pack(fill="both", expand=True, padx=10, pady=10)
        marco.grid_rowconfigure(1, weight=1)
        marco.grid_columnconfigure(0, weight=1)
        marco.grid_columnconfigure(1, weight=1)

        # ------------ Panel Izquierdo: Regex → ... ------------
        tk.Label(
            marco,
            text="Desde Expresión Regular",
            bg="#b9ede2",
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, sticky="w")

        panel_regex = tk.Frame(marco, bg="#b9ede2", bd=1, relief="groove")
        panel_regex.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        panel_regex.grid_rowconfigure(2, weight=1)
        panel_regex.grid_columnconfigure(0, weight=1)

        tk.Label(
            panel_regex,
            text="Expresión Regular (alfabeto de letras minúsculas, operadores: |, *, paréntesis)",
            bg="#b9ede2",
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 2))

        self.entrada_regex = tk.Entry(panel_regex, font=("Consolas", 11))
        self.entrada_regex.grid(row=1, column=0, sticky="ew", padx=5)
        self.entrada_regex.insert(0, "a(b|c)*")

        self.salida_regex = scrolledtext.ScrolledText(
            panel_regex, font=("Consolas", 11), wrap="word"
        )
        self.salida_regex.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        botones_regex = tk.Frame(panel_regex, bg="#b9ede2")
        botones_regex.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 5))

        tk.Button(
            botones_regex,
            text="Regex → AFN → AFD → Gramática",
            bg="#c9c695",
            font=("Segoe UI", 10, "bold"),
            command=self.convertir_desde_regex,
        ).pack(side="left", padx=2)

        tk.Button(
            botones_regex,
            text="Ver diagrama del AFD",
            bg="#c9c695",
            font=("Segoe UI", 10),
            command=self.ver_diagrama_desde_regex,
        ).pack(side="left", padx=2)

        self._afd_desde_regex = None  # para guardar el último AFD

        # ------------ Panel Derecho: Gramática → ... ------------
        tk.Label(
            marco,
            text="Desde Gramática Regular (Tipo 3)",
            bg="#b9ede2",
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=1, sticky="w")

        panel_gram = tk.Frame(marco, bg="#b9ede2", bd=1, relief="groove")
        panel_gram.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        panel_gram.grid_rowconfigure(1, weight=1)
        panel_gram.grid_columnconfigure(0, weight=1)

        tk.Label(
            panel_gram,
            text="Gramática Regular (solo reglas Tipo 3, ej: S -> a A | b)",
            bg="#b9ede2",
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 2))

        self.entrada_gramatica = scrolledtext.ScrolledText(
            panel_gram, font=("Consolas", 11), wrap="word", height=8
        )
        self.entrada_gramatica.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.entrada_gramatica.insert(
            "1.0",
            "S -> a A | b\nA -> a S | epsilon\n",
        )

        botones_gram = tk.Frame(panel_gram, bg="#b9ede2")
        botones_gram.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 5))

        tk.Button(
            botones_gram,
            text="Gramática → NFA → AFD → Regex",
            bg="#c9c695",
            font=("Segoe UI", 10, "bold"),
            command=self.convertir_desde_gramatica,
        ).pack(side="left", padx=2)

        tk.Button(
            botones_gram,
            text="Ver diagrama del AFD",
            bg="#c9c695",
            font=("Segoe UI", 10),
            command=self.ver_diagrama_desde_gramatica,
        ).pack(side="left", padx=2)

        self.salida_gram = scrolledtext.ScrolledText(
            panel_gram, font=("Consolas", 11), wrap="word", height=6
        )
        self.salida_gram.grid(row=3, column=0, sticky="nsew", padx=5, pady=(0, 5))

        self._afd_desde_gramatica = None

        # ------------ Panel Inferior: AFD de ejemplo ------------
        panel_inferior = tk.Frame(self, bg="#b9ede2")
        panel_inferior.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(
            panel_inferior,
            text="AFD de ejemplo (Proyecto 1) → Gramática / Diagrama",
            bg="#b9ede2",
            font=("Segoe UI", 11, "bold"),
        ).pack(side="left")

        tk.Button(
            panel_inferior,
            text="L1: (ab)* → Gramática",
            bg="#c9c695",
            font=("Segoe UI", 10),
            command=self.uso_ejemplo_l1,
        ).pack(side="left", padx=5)

        tk.Button(
            panel_inferior,
            text="L1: Ver diagrama",
            bg="#c9c695",
            font=("Segoe UI", 10),
            command=self.ver_diagrama_ejemplo_l1,
        ).pack(side="left", padx=5)

    # ==========================
    #   Acciones de conversión
    # ==========================

    def convertir_desde_regex(self):
        self.salida_regex.delete("1.0", "end")
        self._afd_desde_regex = None

        expresion = self.entrada_regex.get().strip()
        if not expresion:
            Alerta.mostrar(self, "Error", "Ingresa una expresión regular.")
            return

        try:
            nfa = expresion_regular_a_nfa(expresion)
            alfabeto = obtener_alfabeto_desde_nfa(nfa)
            afd = convertir_nfa_a_afd(nfa, alfabeto)
            self._afd_desde_regex = afd
            gram = convertir_afd_a_gramatica(afd)
            texto_gram = producciones_a_texto(gram)
        except Exception as e:
            Alerta.mostrar(self, "Error", f"No se pudo convertir la expresión regular:\n{e}")
            return

        salida = []
        salida.append("=== Resultado de la conversión ===\n")
        salida.append(f"Expresión regular: {expresion}\n")
        salida.append(f"Alfabeto detectado: {sorted(list(alfabeto))}\n")
        salida.append("--- Gramática regular equivalente ---")
        salida.append(texto_gram)

        self.salida_regex.insert("1.0", "\n".join(salida))

    def ver_diagrama_desde_regex(self):
        if not self._afd_desde_regex:
            Alerta.mostrar(self, "Error", "Primero convierte una expresión regular.")
            return
        try:
            ruta = dibujar_automata(self._afd_desde_regex, "afd_desde_regex")
            mostrar_imagen_en_ventana(self, ruta, "Diagrama del AFD (desde Regex)")
        except Exception as e:
            Alerta.mostrar(self, "Error", str(e))

    def convertir_desde_gramatica(self):
        self.salida_gram.delete("1.0", "end")
        self._afd_desde_gramatica = None

        texto = self.entrada_gramatica.get("1.0", "end")
        try:
            producciones = leer_gramatica_desde_texto(texto)
            nfa = convertir_gramatica_a_nfa(producciones)
            alfabeto = obtener_alfabeto_desde_nfa(nfa)
            afd = convertir_nfa_a_afd(nfa, alfabeto)
            self._afd_desde_gramatica = afd
            regex = convertir_afd_a_expresion_regular(afd)
        except Exception as e:
            Alerta.mostrar(self, "Error", f"No se pudo convertir la gramática:\n{e}")
            return

        salida = []
        salida.append("=== Resultado de la conversión ===\n")
        salida.append("--- Gramática original ingresada ---")
        salida.append(texto.strip())
        salida.append("")
        salida.append(f"Alfabeto detectado en el NFA/AFD: {sorted(list(alfabeto))}")
        salida.append(f"Expresión regular equivalente (aprox): {regex}")

        self.salida_gram.insert("1.0", "\n".join(salida))

    def ver_diagrama_desde_gramatica(self):
        if not self._afd_desde_gramatica:
            Alerta.mostrar(self, "Error", "Primero convierte una gramática.")
            return
        try:
            ruta = dibujar_automata(self._afd_desde_gramatica, "afd_desde_gramatica")
            mostrar_imagen_en_ventana(self, ruta, "Diagrama del AFD (desde Gramática)")
        except Exception as e:
            Alerta.mostrar(self, "Error", str(e))

    def uso_ejemplo_l1(self):
        spec = DefinicionesAutomatas.automata_l1()
        gram = convertir_afd_a_gramatica(spec)
        texto_gram = producciones_a_texto(gram)
        self.salida_regex.delete("1.0", "end")
        self.salida_regex.insert(
            "1.0",
            f"AFD de ejemplo: {spec['nombre']}\n\n--- Gramática regular equivalente ---\n{texto_gram}",
        )

    def ver_diagrama_ejemplo_l1(self):
        spec = DefinicionesAutomatas.automata_l1()
        try:
            ruta = dibujar_automata(spec, "afd_ejemplo_l1")
            mostrar_imagen_en_ventana(self, ruta, "Diagrama AFD L1: (ab)*")
        except Exception as e:
            Alerta.mostrar(self, "Error", str(e))
