from typing import Dict, Any, Set, List, Optional
import tkinter as tk

import graphviz
from PIL import Image, ImageTk

from utilidades_generales import EPSILON_MT, MOVER_DERECHA, VentanaCentrada, Alerta, NodoArbol
from estructuras_gramatica import Produccion, Simbolo


# ======================
#   ESTRUCTURAS NFA
# ======================

class EstadoNFA:
    """Estado de un autómata no determinista (NFA)."""

    _contador_id = 0

    def __init__(self):
        self.id = EstadoNFA._contador_id
        EstadoNFA._contador_id += 1

    def __repr__(self):
        return f"q{self.id}"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, EstadoNFA) and self.id == other.id


class AutomataNFA:
    """Estructura sencilla para un NFA."""

    def __init__(self):
        self.transiciones: Dict[EstadoNFA, Dict[str, Set[EstadoNFA]]] = {}
        self.estado_inicial: Optional[EstadoNFA] = None
        self.estado_final: Optional[EstadoNFA] = None
        self.estados: Set[EstadoNFA] = set()

    def agregar_transicion(self, desde: EstadoNFA, simbolo: str, hacia: EstadoNFA):
        self.estados.add(desde)
        self.estados.add(hacia)
        self.transiciones.setdefault(desde, {}).setdefault(simbolo, set()).add(hacia)


# ==========================
#   AFD ↔ Gramática Regular
# ==========================

def convertir_afd_a_gramatica(afd: Dict[str, Any]) -> List[Produccion]:
    """
    Convierte una especificación de AFD (formato Proyecto 1)
    en una gramática regular equivalente.
    """
    producciones: List[Produccion] = []
    mapeo_estados: Dict[int, Simbolo] = {}
    todos_estados = set(afd["estActua"]) | set(afd["estsigui"]) | {afd["start_state"]}

    for estado in todos_estados:
        mapeo_estados[estado] = Simbolo(f"Q{estado}", es_terminal=False)

    for q_i, a, q_j in zip(afd["estActua"], afd["lecturas"], afd["estsigui"]):
        no_terminal_i = mapeo_estados[q_i]
        no_terminal_j = mapeo_estados[q_j]
        terminal_a = Simbolo(a, es_terminal=True)
        producciones.append(
            Produccion(lado_izquierdo=[no_terminal_i], lado_derecho=[terminal_a, no_terminal_j])
        )

    for q_f in afd["accept_states"]:
        if q_f in mapeo_estados:
            no_terminal_f = mapeo_estados[q_f]
            producciones.append(
                Produccion(lado_izquierdo=[no_terminal_f], lado_derecho=[])
            )

    return producciones


def convertir_gramatica_a_nfa(gramatica: List[Produccion]) -> AutomataNFA:
    """
    Convierte una gramática regular de Tipo 3 en un NFA (Thompson-like).
    Asume que todas las producciones son del tipo:
      A -> a B
      A -> a
      A -> ε
    """
    nfa = AutomataNFA()
    mapeo_estados: Dict[str, EstadoNFA] = {}

    EstadoNFA._contador_id = 0
    estado_final_unico = EstadoNFA()
    nfa.estado_final = estado_final_unico

    # Crear estados a partir de los no-terminales
    todos_no_terminales = set()
    for p in gramatica:
        todos_no_terminales.add(p.alpha[0].valor)
        for s in p.beta:
            if not s.es_terminal:
                todos_no_terminales.add(s.valor)

    for nombre_nt in todos_no_terminales:
        mapeo_estados[nombre_nt] = EstadoNFA()

    if not gramatica:
        return nfa

    nfa.estado_inicial = mapeo_estados[gramatica[0].alpha[0].valor]

    # Crear transiciones
    for p in gramatica:
        estado_A = mapeo_estados[p.alpha[0].valor]
        if len(p.beta) == 2:  # A -> aB
            simbolo, nt_B = p.beta[0].valor, p.beta[1].valor
            estado_B = mapeo_estados[nt_B]
            nfa.agregar_transicion(estado_A, simbolo, estado_B)
        elif len(p.beta) == 1:  # A -> a
            simbolo = p.beta[0].valor
            nfa.agregar_transicion(estado_A, simbolo, nfa.estado_final)
        elif len(p.beta) == 0:  # A -> ε
            nfa.agregar_transicion(estado_A, "ε", nfa.estado_final)

    return nfa


def _cerradura_epsilon(estados: Set[EstadoNFA], transiciones: Dict) -> Set[EstadoNFA]:
    pila = list(estados)
    clausura = set(estados)

    while pila:
        estado_actual = pila.pop()
        if estado_actual in transiciones and "ε" in transiciones[estado_actual]:
            for siguiente in transiciones[estado_actual]["ε"]:
                if siguiente not in clausura:
                    clausura.add(siguiente)
                    pila.append(siguiente)

    return frozenset(clausura)


def convertir_nfa_a_afd(nfa: AutomataNFA, alfabeto: Set[str]) -> Dict[str, Any]:
    """
    Convierte un NFA (con transiciones ε) en un AFD
    compatible con el formato del Proyecto 1.
    """
    if nfa.estado_inicial is None:
        raise ValueError("El NFA no tiene estado inicial definido.")

    q0_afd = _cerradura_epsilon({nfa.estado_inicial}, nfa.transiciones)
    estados_afd = {q0_afd}
    cola = [q0_afd]
    transiciones_afd: Dict[Any, Dict[str, Any]] = {}
    estados_finales_afd: Set[Any] = set()
    nombres_estados: Dict[Any, int] = {q0_afd: 0}
    contador_id = 1

    while cola:
        conjunto_actual = cola.pop(0)
        if nfa.estado_final in conjunto_actual:
            estados_finales_afd.add(conjunto_actual)

        transiciones_afd[conjunto_actual] = {}
        for simbolo in alfabeto:
            siguiente_conjunto = set()
            for estado_nfa in conjunto_actual:
                if (
                    estado_nfa in nfa.transiciones
                    and simbolo in nfa.transiciones[estado_nfa]
                ):
                    siguiente_conjunto.update(nfa.transiciones[estado_nfa][simbolo])

            if not siguiente_conjunto:
                continue

            clausura_siguiente = _cerradura_epsilon(siguiente_conjunto, nfa.transiciones)
            if clausura_siguiente not in estados_afd:
                estados_afd.add(clausura_siguiente)
                cola.append(clausura_siguiente)
                nombres_estados[clausura_siguiente] = contador_id
                contador_id += 1

            transiciones_afd[conjunto_actual][simbolo] = clausura_siguiente

    spec_final = {
        "nombre": "AFD Convertido",
        "start_state": 0,
        "accept_states": {nombres_estados[fs] for fs in estados_finales_afd},
        "alphabet": alfabeto,
        "estActua": [],
        "lecturas": [],
        "escribeC": [],
        "estsigui": [],
        "mueveCab": [],
    }

    for estado_desde, trans in transiciones_afd.items():
        for simbolo, estado_hacia in trans.items():
            spec_final["estActua"].append(nombres_estados[estado_desde])
            spec_final["lecturas"].append(simbolo)
            spec_final["estsigui"].append(nombres_estados[estado_hacia])
            spec_final["escribeC"].append(EPSILON_MT)
            spec_final["mueveCab"].append(MOVER_DERECHA)

    return spec_final


# ======================
#   Regex → NFA (Thompson)
# ======================

def _es_simbolo_regex(c: str) -> bool:
    return c not in {"(", ")", "|", "*", "."}


def _insertar_concatenacion_implicita(regex: str) -> str:
    """
    Inserta el operador '.' para concatenación donde sea necesario.
    Ejemplo: 'a(b|c)*' -> 'a.(b|c)*'
    """
    regex = regex.replace(" ", "")
    if not regex:
        return ""

    resultado = []
    n = len(regex)

    for i, c1 in enumerate(regex):
        resultado.append(c1)
        if i == n - 1:
            break
        c2 = regex[i + 1]

        if (
            ( _es_simbolo_regex(c1) or c1 in {")", "*", "ε"} )
            and ( _es_simbolo_regex(c2) or c2 in {"(", "ε"} )
        ):
            resultado.append(".")

    return "".join(resultado)


def _infix_a_postfix(regex: str) -> str:
    """
    Convierte una expresión regular en notación infija a postfija (Shunting-yard).
    Operadores: *, ., |
    Precedencia: * > . > |
    """
    precedencia = {"|": 1, ".": 2, "*": 3}
    salida = []
    pila = []

    for c in regex:
        if _es_simbolo_regex(c) or c == "ε":
            salida.append(c)
        elif c == "(":
            pila.append(c)
        elif c == ")":
            while pila and pila[-1] != "(":
                salida.append(pila.pop())
            if pila and pila[-1] == "(":
                pila.pop()
        else:
            while (
                pila
                and pila[-1] != "("
                and precedencia.get(pila[-1], 0) >= precedencia.get(c, 0)
            ):
                salida.append(pila.pop())
            pila.append(c)

    while pila:
        salida.append(pila.pop())

    return "".join(salida)


def expresion_regular_a_nfa(expresion: str) -> AutomataNFA:
    """
    Construye un NFA a partir de una expresión regular usando Thompson.
    Soporta: concatenación (implícita), | y *, paréntesis.
    """
    expresion = expresion.strip()
    if not expresion:
        raise ValueError("La expresión regular está vacía.")

    expresion = _insertar_concatenacion_implicita(expresion)
    postfix = _infix_a_postfix(expresion)
    pila: List[AutomataNFA] = []

    for c in postfix:
        if _es_simbolo_regex(c) or c == "ε":
            nfa = AutomataNFA()
            s = EstadoNFA()
            e = EstadoNFA()
            nfa.estado_inicial = s
            nfa.estado_final = e
            nfa.agregar_transicion(s, c, e)
            pila.append(nfa)

        elif c == ".":
            # concatenación
            if len(pila) < 2:
                raise ValueError("Expresión regular inválida (concatenación).")
            nfa2 = pila.pop()
            nfa1 = pila.pop()
            nfa1.agregar_transicion(nfa1.estado_final, "ε", nfa2.estado_inicial)
            # copiar transiciones
            for estado, trans in nfa2.transiciones.items():
                for simb, dests in trans.items():
                    for d in dests:
                        nfa1.agregar_transicion(estado, simb, d)
            nfa1.estado_final = nfa2.estado_final
            pila.append(nfa1)

        elif c == "|":
            # unión
            if len(pila) < 2:
                raise ValueError("Expresión regular inválida (unión).")
            nfa2 = pila.pop()
            nfa1 = pila.pop()

            nfa = AutomataNFA()
            s = EstadoNFA()
            e = EstadoNFA()
            nfa.estado_inicial = s
            nfa.estado_final = e

            # copiar transiciones
            for dic in (nfa1.transiciones, nfa2.transiciones):
                for estado, trans in dic.items():
                    for simb, dests in trans.items():
                        for d in dests:
                            nfa.agregar_transicion(estado, simb, d)

            nfa.agregar_transicion(s, "ε", nfa1.estado_inicial)
            nfa.agregar_transicion(s, "ε", nfa2.estado_inicial)
            nfa.agregar_transicion(nfa1.estado_final, "ε", e)
            nfa.agregar_transicion(nfa2.estado_final, "ε", e)

            pila.append(nfa)

        elif c == "*":
            # cierre de Kleene
            if not pila:
                raise ValueError("Expresión regular inválida (estrella).")
            nfa1 = pila.pop()
            nfa = AutomataNFA()
            s = EstadoNFA()
            e = EstadoNFA()
            nfa.estado_inicial = s
            nfa.estado_final = e

            for estado, trans in nfa1.transiciones.items():
                for simb, dests in trans.items():
                    for d in dests:
                        nfa.agregar_transicion(estado, simb, d)

            nfa.agregar_transicion(s, "ε", nfa1.estado_inicial)
            nfa.agregar_transicion(s, "ε", e)
            nfa.agregar_transicion(nfa1.estado_final, "ε", nfa1.estado_inicial)
            nfa.agregar_transicion(nfa1.estado_final, "ε", e)

            pila.append(nfa)

        else:
            raise ValueError(f"Símbolo de expresión regular no soportado: '{c}'")

    if len(pila) != 1:
        raise ValueError("Expresión regular inválida (pila final != 1).")

    return pila[0]


def obtener_alfabeto_desde_nfa(nfa: AutomataNFA) -> Set[str]:
    alfabeto: Set[str] = set()
    for trans in nfa.transiciones.values():
        for simb in trans.keys():
            if simb != "ε":
                alfabeto.add(simb)
    return alfabeto


# ===========================
#   AFD → Expresión Regular
# ===========================

def _union_regex(a: str, b: str) -> str:
    if not a:
        return b
    if not b:
        return a
    if a == b:
        return a
    return f"{a}|{b}"


def _concatenar_regex(a: str, b: str) -> str:
    if not a or not b:
        return ""
    if a == "ε":
        return b
    if b == "ε":
        return a

    def par(s: str) -> str:
        if "|" in s and not (s.startswith("(") and s.endswith(")")):
            return f"({s})"
        return s

    return par(a) + par(b)


def _estrella_regex(a: str) -> str:
    if not a:
        return ""
    if a == "ε":
        return "ε"
    if len(a) == 1:
        return a + "*"
    if a.startswith("(") and a.endswith(")"):
        return a + "*"
    return f"({a})*"


def convertir_afd_a_expresion_regular(afd: Dict[str, Any]) -> str:
    """
    Convierte un AFD a una expresión regular usando eliminación de estados.
    Usa el método de Matriz R_k[i][j].
    """
    estados = sorted(
        set(afd["estActua"]) | set(afd["estsigui"]) | {afd["start_state"]} | set(afd["accept_states"])
    )
    if not estados:
        return "∅"

    # Crear nuevo estado final único F
    nuevo_final = max(estados) + 1
    estados.append(nuevo_final)

    start = afd["start_state"]
    accept_states = set(afd["accept_states"])

    indices = {estado: i for i, estado in enumerate(estados)}
    n = len(estados)
    R = [["" for _ in range(n)] for _ in range(n)]

    # Inicializar R[-1]
    for desde, simb, hasta in zip(afd["estActua"], afd["lecturas"], afd["estsigui"]):
        i = indices[desde]
        j = indices[hasta]
        R[i][j] = _union_regex(R[i][j], simb)

    # Diagonales con ε
    for estado in estados:
        i = indices[estado]
        R[i][i] = _union_regex(R[i][i], "ε")

    # Agregar transiciones ε desde estados de aceptación al nuevo final
    idx_final = indices[nuevo_final]
    for qf in accept_states:
        i = indices[qf]
        R[i][idx_final] = _union_regex(R[i][idx_final], "ε")

    # También el final consigo mismo con ε
    R[idx_final][idx_final] = _union_regex(R[idx_final][idx_final], "ε")

    # Programa dinámico R_k
    for k in range(n):
        for i in range(n):
            for j in range(n):
                sin_k = R[i][j]
                if not R[i][k] or not R[k][j]:
                    con_k = ""
                else:
                    loop = _estrella_regex(R[k][k])
                    con_k = _concatenar_regex(R[i][k], _concatenar_regex(loop, R[k][j]))
                R[i][j] = _union_regex(sin_k, con_k)

    idx_start = indices[start]
    regex = R[idx_start][idx_final]
    return regex if regex else "∅"


# ======================
#   Diagramas y Árboles
# ======================

def dibujar_automata(
    spec: Dict[str, Any],
    ruta_salida: str = "automata_grafico",
    formato: str = "png",
) -> str:
    """
    Genera un diagrama de autómata usando Graphviz y devuelve
    la ruta del archivo generado.
    """
    dot = graphviz.Digraph(comment=spec.get("nombre", "Automata"))
    dot.attr(rankdir="LR")

    estados = set(spec["estActua"]) | set(spec["estsigui"]) | {spec["start_state"]}
    estado_inicial = str(spec["start_state"])
    estados_aceptacion = {str(s) for s in spec["accept_states"]}

    for e in estados:
        etiqueta = str(e)
        forma = "doublecircle" if etiqueta in estados_aceptacion else "circle"
        dot.node(etiqueta, shape=forma)

    dot.node("inicio", shape="point", style="invisible")
    dot.edge("inicio", estado_inicial, label="Inicio")

    for est_act, lectura, est_sig in zip(spec["estActua"], spec["lecturas"], spec["estsigui"]):
        dot.edge(str(est_act), str(est_sig), label=str(lectura))

    try:
        ruta = dot.render(filename=ruta_salida, view=False, cleanup=True, format=formato)
        return ruta
    except Exception as e:
        raise Exception(f"Error al generar el diagrama con Graphviz: {e}")


def mostrar_imagen_en_ventana(padre: tk.Misc, ruta_imagen: str, titulo: str):
    """
    Muestra una imagen en una ventana Tkinter con scroll.
    """
    ventana = tk.Toplevel(padre)
    ventana.title(titulo)
    ventana.configure(bg="#b9ede2")
    VentanaCentrada.centrar_ventana(ventana, 800, 600)

    marco = tk.Frame(ventana, bg="#b9ede2")
    marco.pack(fill="both", expand=True, padx=6, pady=6)

    lienzo = tk.Canvas(marco, bg="#dddddd", highlightthickness=0)
    barra_h = tk.Scrollbar(marco, orient="horizontal", command=lienzo.xview)
    barra_v = tk.Scrollbar(marco, orient="vertical", command=lienzo.yview)
    lienzo.configure(xscrollcommand=barra_h.set, yscrollcommand=barra_v.set)

    lienzo.grid(row=0, column=0, sticky="nsew")
    barra_v.grid(row=0, column=1, sticky="ns")
    barra_h.grid(row=1, column=0, sticky="ew")
    marco.grid_rowconfigure(0, weight=1)
    marco.grid_columnconfigure(0, weight=1)

    try:
        imagen_original = Image.open(ruta_imagen)
    except Exception as e:
        Alerta.mostrar(ventana, "Error", f"No se pudo cargar la imagen:\n{e}")
        return

    ventana._imagen_original = imagen_original
    ventana._imagen_tk = None
    ventana._id_imagen = lienzo.create_image(0, 0, image=None, anchor="nw")

    def redibujar(event=None):
        ancho = lienzo.winfo_width()
        alto = lienzo.winfo_height()
        if ancho < 2 or alto < 2:
            ventana.after(100, redibujar)
            return

        img_w, img_h = ventana._imagen_original.size
        escala = min(ancho / img_w, alto / img_h)
        nuevo_ancho = int(img_w * escala)
        nuevo_alto = int(img_h * escala)

        img_escalada = ventana._imagen_original.resize(
            (nuevo_ancho, nuevo_alto),
            Image.Resampling.LANCZOS,
        )
        ventana._imagen_tk = ImageTk.PhotoImage(img_escalada)
        lienzo.itemconfig(ventana._id_imagen, image=ventana._imagen_tk)
        lienzo.configure(scrollregion=lienzo.bbox("all"))

    lienzo.bind("<Configure>", redibujar)
    ventana.after(50, redibujar)


def mostrar_arbol_en_texto(padre: tk.Misc, raiz: NodoArbol):
    """
    Muestra un árbol de derivación en formato texto (ASCII).
    (Por si más adelante quieres enlazar el árbol de tu Proyecto 2.)
    """
    ventana = tk.Toplevel(padre)
    ventana.title("Árbol de derivación (ASCII)")
    ventana.configure(bg="#b9ede2")
    VentanaCentrada.centrar_ventana(ventana, 720, 520)

    marco = tk.Frame(ventana, bg="#b9ede2")
    marco.pack(fill="both", expand=True, padx=10, pady=10)

    texto = tk.Text(marco, font=("Courier", 10), wrap="none", bg="#c7ccc6", borderwidth=5)
    barra_v = tk.Scrollbar(marco, orient="vertical", command=texto.yview)
    barra_h = tk.Scrollbar(marco, orient="horizontal", command=texto.xview)
    texto.configure(yscrollcommand=barra_v.set, xscrollcommand=barra_h.set)

    texto.grid(row=0, column=0, sticky="nsew")
    barra_v.grid(row=0, column=1, sticky="ns")
    barra_h.grid(row=1, column=0, sticky="ew")
    marco.grid_rowconfigure(0, weight=1)
    marco.grid_columnconfigure(0, weight=1)

    def recorrer(nodo: NodoArbol, prefijo: str = ""):
        linea = nodo.simbolo
        if nodo.lexema is not None:
            linea += f" -> '{nodo.lexema}' [L:{nodo.linea}, C:{nodo.columna}]"
        texto.insert("end", prefijo + linea + "\n")
        for i, hijo in enumerate(nodo.hijos):
            es_ultimo = (i == len(nodo.hijos) - 1)
            nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
            conector = "└─ " if es_ultimo else "├─ "
            recorrer(hijo, nuevo_prefijo + conector)

    recorrer(raiz)
    texto.config(state=tk.DISABLED)
