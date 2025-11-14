from typing import List, Dict, Set, Tuple

from estructuras_gramatica import Produccion, Simbolo


class AnalizadorEquivalencia:
    """
    Genera, de forma heurística, el conjunto de cadenas que
    produce una gramática hasta cierta longitud máxima n.
    Se asume que la gramática es al menos de Tipo 2 (alpha = 1 No-Terminal).
    """

    def __init__(self, producciones: List[Produccion], n_max: int):
        self.n_max = n_max
        self.simbolo_inicial = producciones[0].alpha[0].valor if producciones else ""
        self.mapa_gramatica: Dict[str, List[List[Simbolo]]] = {}

        for p in producciones:
            # Solo consideramos reglas de la forma A -> beta (un No-Terminal en alpha)
            if len(p.alpha) == 1 and not p.alpha[0].es_terminal:
                A = p.alpha[0].valor
                self.mapa_gramatica.setdefault(A, []).append(p.beta)

    def _generar(
        self,
        secuencia: List[Simbolo],
        cache: Dict[str, Set[str]],
        longitud_actual: int,
    ) -> Set[str]:
        """
        Genera todas las cadenas posibles derivando la secuencia dada,
        sin exceder la longitud máxima.
        """
        if longitud_actual > self.n_max:
            return set()

        if not secuencia:
            return {""}

        simbolo_actual = secuencia[0]
        resto = secuencia[1:]

        if simbolo_actual.es_terminal:
            # Avanzamos con ese terminal
            cadenas_resto = self._generar(
                resto, cache, longitud_actual + len(simbolo_actual.valor)
            )
            resultado = set()
            for s in cadenas_resto:
                nueva = simbolo_actual.valor + s
                if len(nueva) <= self.n_max:
                    resultado.add(nueva)
            return resultado

        # Es No-Terminal
        nombre_nt = simbolo_actual.valor

        if nombre_nt in cache:
            cadenas_nt = cache[nombre_nt]
        else:
            cadenas_nt: Set[str] = set()
            cache[nombre_nt] = set()  # marca "en progreso" para evitar recursión infinita

            if nombre_nt in self.mapa_gramatica:
                for beta in self.mapa_gramatica[nombre_nt]:
                    cadenas_nt.update(self._generar(beta, cache, longitud_actual))

            cache[nombre_nt] = cadenas_nt

        cadenas_resto = self._generar(resto, cache, longitud_actual)
        resultado_final: Set[str] = set()

        for s_nt in cadenas_nt:
            for s_resto in cadenas_resto:
                nueva = s_nt + s_resto
                if len(nueva) <= self.n_max:
                    resultado_final.add(nueva)

        return resultado_final

    def generar_cadenas(self) -> Set[str]:
        """
        Genera las cadenas posibles desde el símbolo inicial hasta longitud n_max.
        """
        if not self.simbolo_inicial:
            return set()
        simbolo_inicial = Simbolo(self.simbolo_inicial, es_terminal=False)
        return self._generar([simbolo_inicial], {}, 0)


def comparar_gramaticas(
    g1: List[Produccion],
    g2: List[Produccion],
    n_max: int = 5,
) -> Tuple[bool, str]:
    """
    Compara dos gramáticas generando sus lenguajes hasta longitud n_max.
    Devuelve (son_equivalentes, mensaje_explicativo).
    """
    try:
        set1 = AnalizadorEquivalencia(g1, n_max).generar_cadenas()
        set2 = AnalizadorEquivalencia(g2, n_max).generar_cadenas()
    except Exception as e:
        return False, f"Error durante la generación de cadenas (posible recursión infinita): {e}"

    if set1 == set2:
        return True, (
            f"HEURÍSTICA: Posible equivalencia.\n\n"
            f"Ambas gramáticas generan el mismo conjunto de {len(set1)} "
            f"cadenas (hasta longitud {n_max})."
        )

    solo_g1 = list(set1 - set2)[:5]
    solo_g2 = list(set2 - set1)[:5]

    mensaje = (
        f"HEURÍSTICA: No equivalentes (para n = {n_max}).\n\n"
        f"Cadenas solo en Gramática 1: {solo_g1}\n"
        f"Cadenas solo en Gramática 2: {solo_g2}"
    )
    return False, mensaje
