from typing import List, Dict, Set, Tuple, Optional
from utilidades_generales import EPSILON_GRAMATICA, NodoArbol


class GeneradorTablaLL1:
    """
    Calcula conjuntos FIRST, FOLLOW y la tabla LL(1) para una gramática dada.
    La gramática G se representa como: { NoTerminal: [ [simbolos], [simbolos], ... ] }
    """
    def __init__(self, gramatica: Dict[str, List[List[str]]], simbolo_inicial: str):
        self.G = gramatica
        self.simbolo_inicial = simbolo_inicial
        self.no_terminales = set(self.G.keys())
        self.terminales = self._inferir_terminales()

        # FIRST, FOLLOW y tabla M
        self.FIRST: Dict[str, Set[str]] = {
            s: set() for s in list(self.no_terminales) + list(self.terminales) + [EPSILON_GRAMATICA]
        }
        self.FOLLOW: Dict[str, Set[str]] = {A: set() for A in self.no_terminales}
        self.tabla_M: Dict[str, Dict[str, List[List[str]]]] = {}
        self.conflictos: List[Tuple[str, str, List[List[str]]]] = []

        self._calcular_conjuntos_first()
        self._calcular_conjuntos_follow()

    def _inferir_terminales(self) -> Set[str]:
        terminales = set()
        for producciones in self.G.values():
            for prod in producciones:
                for simbolo in prod:
                    if simbolo not in self.G and simbolo != EPSILON_GRAMATICA:
                        terminales.add(simbolo)
        terminales.add("$")
        return terminales

    def _first_de_secuencia(self, secuencia: List[str]) -> Set[str]:
        resultado = set()
        if not secuencia:
            resultado.add(EPSILON_GRAMATICA)
            return resultado

        for simbolo in secuencia:
            if simbolo not in self.FIRST:
                if simbolo in self.terminales:
                    self.FIRST[simbolo] = {simbolo}
                else:
                    return set()
            first_simbolo = self.FIRST[simbolo]
            resultado.update(first_simbolo - {EPSILON_GRAMATICA})
            if EPSILON_GRAMATICA not in first_simbolo:
                return resultado

        resultado.add(EPSILON_GRAMATICA)
        return resultado

    def _calcular_conjuntos_first(self):
        for A in self.no_terminales:
            self.FIRST[A] = set()
        for t in self.terminales:
            self.FIRST[t] = {t}
        self.FIRST[EPSILON_GRAMATICA] = {EPSILON_GRAMATICA}

        cambio = True
        while cambio:
            cambio = False
            for A, producciones in self.G.items():
                for prod in producciones:
                    first_alpha = self._first_de_secuencia(prod)
                    antes = len(self.FIRST[A])
                    self.FIRST[A].update(first_alpha)
                    if len(self.FIRST[A]) != antes:
                        cambio = True

    def _calcular_conjuntos_follow(self):
        for A in self.no_terminales:
            self.FOLLOW[A] = set()
        self.FOLLOW[self.simbolo_inicial].add("$")

        cambio = True
        while cambio:
            cambio = False
            for A, producciones in self.G.items():
                for prod in producciones:
                    for i, B in enumerate(prod):
                        if B in self.no_terminales:
                            beta = prod[i + 1:]
                            first_beta = self._first_de_secuencia(beta)
                            antes = len(self.FOLLOW[B])
                            self.FOLLOW[B].update(first_beta - {EPSILON_GRAMATICA})
                            if EPSILON_GRAMATICA in first_beta or not beta:
                                self.FOLLOW[B].update(self.FOLLOW[A])
                            if len(self.FOLLOW[B]) != antes:
                                cambio = True

    def construir_tabla(self) -> Dict[str, Dict[str, List[List[str]]]]:
        self.tabla_M = {A: {} for A in self.no_terminales}
        self.conflictos = []

        for A, producciones in self.G.items():
            for prod in producciones:
                first_alpha = self._first_de_secuencia(prod)
                for a in (first_alpha - {EPSILON_GRAMATICA}):
                    celda = self.tabla_M[A].setdefault(a, [])
                    if prod not in celda:
                        celda.append(prod)
                        if len(celda) > 1:
                            # conflicto LL(1)
                            existe = any(c[0] == A and c[1] == a for c in self.conflictos)
                            if not existe:
                                self.conflictos.append((A, a, [p[:] for p in celda]))
                if EPSILON_GRAMATICA in first_alpha:
                    for b in self.FOLLOW[A]:
                        celda = self.tabla_M[A].setdefault(b, [])
                        if prod not in celda:
                            celda.append(prod)
                            if len(celda) > 1:
                                existe = any(c[0] == A and c[1] == b for c in self.conflictos)
                                if not existe:
                                    self.conflictos.append((A, b, [p[:] for p in celda]))
        return self.tabla_M


def analizar_sintactico(
    lista_tokens: List[Tuple[str, str, int, int]],
    tabla_M: Dict[str, Dict[str, List[List[str]]]],
    simbolo_inicial: str,
    first_sets: Dict[str, Set[str]],
    follow_sets: Dict[str, Set[str]],
) -> Tuple[Optional[NodoArbol], Optional[str]]:
    """
    Analizador sintáctico LL(1) genérico.
    Recibe la lista de tokens y la tabla M, y devuelve:
      (raiz_del_arbol, mensaje_error)   # mensaje_error = None si todo salió bien
    """
    no_terminales = set(tabla_M.keys())
    entrada = [(tok[0], tok[1], tok[2], tok[3]) for tok in lista_tokens]

    # Añadir token de fin de cadena
    if entrada:
        ultimo_lexema, _, ult_lin, ult_col = entrada[-1]
        fin_lin = ult_lin
        fin_col = ult_col + (len(ultimo_lexema) if ultimo_lexema else 1)
    else:
        fin_lin, fin_col = 1, 1
    entrada.append(("$", "$", fin_lin, fin_col))

    pila: List[NodoArbol] = []
    raiz = NodoArbol(simbolo_inicial)
    pila.append(NodoArbol("$"))
    pila.append(raiz)

    i = 0
    while pila:
        nodo_X = pila.pop()
        X = nodo_X.simbolo

        if i >= len(entrada):
            return None, "Error interno: se intentó leer más allá del fin de la entrada."

        lexema_actual, tipo_actual, lin_act, col_act = entrada[i]

        if X == EPSILON_GRAMATICA:
            # símbolo epsilon en la pila, se ignora
            continue

        # Caso: X es terminal
        if X not in no_terminales and X != "$":
            if X == tipo_actual:
                nodo_X.lexema = lexema_actual
                nodo_X.linea = lin_act
                nodo_X.columna = col_act
                i += 1
                continue
            else:
                encontrado = f"'{lexema_actual}'" if tipo_actual != "$" else "<fin>"
                return None, (
                    f"[Línea {lin_act} | Columna {col_act}] "
                    f"Se encontró {encontrado} (tipo {tipo_actual}), pero se esperaba {X}."
                )

        # Caso: fin de pila
        if X == "$":
            if tipo_actual == "$":
                return raiz, None  # éxito total
            else:
                return None, (
                    f"[Línea {lin_act} | Columna {col_act}] "
                    f"Se encontró '{lexema_actual}' (tipo {tipo_actual}) después del fin esperado."
                )

        # Caso: no-terminal
        fila = tabla_M.get(X, {})
        candidatos = fila.get(tipo_actual, [])

        if not candidatos:
            encontrado = f"'{lexema_actual}'" if tipo_actual != "$" else "<fin>"
            esperados = ", ".join(sorted(list(fila.keys()))) if fila else "<ninguno>"
            return None, (
                f"[Línea {lin_act} | Columna {col_act}] "
                f"Token inesperado {encontrado} (tipo {tipo_actual}). "
                f"Para el No-Terminal <{X}> se esperaba uno de: {esperados}."
            )

        produccion = candidatos[0]
        hijos = [NodoArbol(simbolo) for simbolo in produccion]
        for h in hijos:
            nodo_X.agregar_hijo(h)
        for h in reversed(hijos):
            if h.simbolo != EPSILON_GRAMATICA:
                pila.append(h)

    return None, "Error inesperado: se terminó el ciclo sin aceptar la entrada."
