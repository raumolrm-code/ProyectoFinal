import re
from typing import List, Dict

from utilidades_generales import EPSILON_GRAMATICA


class Simbolo:
    """Un símbolo de la gramática (terminal o no-terminal)."""

    def __init__(self, valor: str, es_terminal: bool):
        self.valor = valor
        self.es_terminal = es_terminal

    def __repr__(self):
        return f"'{self.valor}'" if self.es_terminal else f"<{self.valor}>"


class Produccion:
    """Producción limpia: alpha -> beta (listas de símbolos)."""

    def __init__(self, lado_izquierdo: List[Simbolo], lado_derecho: List[Simbolo]):
        self.alpha = lado_izquierdo
        self.beta = lado_derecho

    def __repr__(self):
        alpha_str = " ".join(s.valor for s in self.alpha)
        beta_str = " ".join(s.valor for s in self.beta) if self.beta else "ε"
        return f"{alpha_str} -> {beta_str}"


def _es_no_terminal(nombre: str) -> bool:
    """
    Regla sencilla:
    - Si está entre < >  => No-Terminal
    - Si empieza en mayúscula => No-Terminal
    - En otro caso => Terminal
    """
    if not nombre:
        return False
    nombre = nombre.strip()
    if nombre.startswith("<") and nombre.endswith(">"):
        return True
    return nombre[0].isupper()


def _normalizar_no_terminal(nombre: str) -> str:
    nombre = nombre.strip()
    if nombre.startswith("<") and nombre.endswith(">") and len(nombre) >= 3:
        return nombre[1:-1]
    return nombre


def _crear_simbolo(token: str) -> Simbolo:
    es_nt = _es_no_terminal(token)
    valor = _normalizar_no_terminal(token) if es_nt else token
    return Simbolo(valor, es_terminal=not es_nt)


def leer_linea_gramatica(linea: str, numero_linea: int) -> List[Produccion]:
    """
    Lee una línea de la forma:
        S -> a S b | a b
    y la convierte en una o varias Produccion.
    """
    sin_comentario = linea.split("#", 1)[0].strip()
    if not sin_comentario:
        return []

    m = re.search(r"->|::=|→", sin_comentario)
    if not m:
        raise ValueError(
            f"Línea {numero_linea}: no se encontró '->', '::=' o '→' en la regla."
        )

    lado_izq = sin_comentario[:m.start()].strip()
    lado_der = sin_comentario[m.end():].strip()

    if not lado_izq:
        raise ValueError(f"Línea {numero_linea}: el lado izquierdo está vacío.")
    if not lado_der:
        raise ValueError(f"Línea {numero_linea}: el lado derecho está vacío.")

    tokens_izq = lado_izq.split()
    alpha = [_crear_simbolo(t) for t in tokens_izq]

    producciones: List[Produccion] = []
    alternativas = [alt.strip() for alt in lado_der.split("|")]

    for alt in alternativas:
        if not alt or alt in {EPSILON_GRAMATICA, "ε", "E", "eps", "EPS"}:
            beta: List[Simbolo] = []
        else:
            tokens_der = alt.split()
            beta = [_crear_simbolo(t) for t in tokens_der]
        producciones.append(Produccion(alpha, beta))

    return producciones


def leer_gramatica_desde_texto(texto: str) -> List[Produccion]:
    """
    Lee un bloque de texto con varias líneas de gramática
    y devuelve la lista de producciones.
    """
    producciones: List[Produccion] = []
    for i, linea in enumerate(texto.splitlines(), start=1):
        if not linea.strip():
            continue
        prods_linea = leer_linea_gramatica(linea, i)
        producciones.extend(prods_linea)

    if not producciones:
        raise ValueError("La gramática está vacía o solo contiene comentarios/espacios.")
    return producciones


def producciones_a_texto(producciones: List[Produccion]) -> str:
    """
    Convierte una lista de Produccion a una gramática en texto,
    agrupando alternativas por lado izquierdo.
    """
    agrupado: Dict[str, List[str]] = {}
    for p in producciones:
        alpha_str = " ".join(s.valor for s in p.alpha)
        beta_str = " ".join(s.valor for s in p.beta) if p.beta else EPSILON_GRAMATICA
        agrupado.setdefault(alpha_str, []).append(beta_str)

    lineas = []
    for alpha_str, betas in agrupado.items():
        rhs = " | ".join(betas)
        lineas.append(f"{alpha_str} -> {rhs}")
    return "\n".join(lineas)
