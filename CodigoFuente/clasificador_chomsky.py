from typing import List, Tuple
from estructuras_gramatica import Produccion


class ClasificadorChomsky:
    """
    Clasifica una gramática según la jerarquía de Chomsky.
    Tipos:
      - 3: Regular
      - 2: Libre de Contexto
      - 1: Sensible al Contexto
      - 0: Recursivamente Enumerable
    Devuelve SIEMPRE el tipo más restrictivo que cumple (3 > 2 > 1 > 0).
    """

    def __init__(self, producciones: List[Produccion]):
        self.producciones = producciones
        self.simbolo_inicial = producciones[0].alpha[0].valor if producciones else ""

    def _es_tipo_3(self) -> Tuple[bool, List[str]]:
        """
        Tipo 3 (Regular): A -> a | aB | ε
        Lado izquierdo: un solo No-Terminal.
        """
        violaciones: List[str] = []
        es_regular = True

        for p in self.producciones:
            if len(p.alpha) != 1 or p.alpha[0].es_terminal:
                violaciones.append(
                    f"Regla '{p}': no es Tipo 3, el lado izquierdo no es un solo No-Terminal."
                )
                es_regular = False
                continue

            if len(p.beta) == 0:
                # A -> ε (permitido)
                continue
            elif len(p.beta) == 1 and p.beta[0].es_terminal:
                # A -> a
                continue
            elif (
                len(p.beta) == 2
                and p.beta[0].es_terminal
                and not p.beta[1].es_terminal
            ):
                # A -> aB
                continue
            else:
                violaciones.append(
                    f"Regla '{p}': no es Tipo 3, lado derecho no cumple 'a', 'aB' o ε."
                )
                es_regular = False

        return es_regular, violaciones

    def _es_tipo_2(self) -> Tuple[bool, List[str]]:
        """
        Tipo 2 (Libre de Contexto):
        Lado izquierdo: un solo No-Terminal (sin contexto).
        """
        violaciones: List[str] = []
        es_libre_contexto = True

        for p in self.producciones:
            if len(p.alpha) != 1 or p.alpha[0].es_terminal:
                violaciones.append(
                    f"Regla '{p}': no es Tipo 2, el lado izquierdo no es un solo No-Terminal."
                )
                es_libre_contexto = False

        return es_libre_contexto, violaciones

    def _es_tipo_1(self) -> Tuple[bool, List[str]]:
        """
        Tipo 1 (Sensible al Contexto):
        Regla: |alpha| <= |beta| para todas las producciones,
        excepto S -> ε. Además, si S -> ε existe, S no puede
        aparecer en ningún lado derecho.
        """
        violaciones: List[str] = []
        es_sensible_contexto = True
        acepta_epsilon = False

        for p in self.producciones:
            if len(p.beta) == 0:
                # Producción a epsilon
                if len(p.alpha) == 1 and p.alpha[0].valor == self.simbolo_inicial:
                    acepta_epsilon = True
                else:
                    violaciones.append(
                        f"Regla '{p}': no es Tipo 1, producción a ε no permitida excepto S -> ε."
                    )
                    es_sensible_contexto = False
                continue

            if len(p.alpha) > len(p.beta):
                violaciones.append(
                    f"Regla '{p}': no es Tipo 1, acorta la cadena (|alpha| > |beta|)."
                )
                es_sensible_contexto = False

        if acepta_epsilon:
            # Si S -> ε existe, S no puede aparecer en el lado derecho
            for p in self.producciones:
                for s in p.beta:
                    if s.valor == self.simbolo_inicial:
                        violaciones.append(
                            f"Regla '{p}': no es Tipo 1, S -> ε existe pero S aparece en el lado derecho."
                        )
                        es_sensible_contexto = False
                        break

        return es_sensible_contexto, violaciones

    def clasificar(self) -> Tuple[int, str, List[str]]:
        """
        Devuelve (tipo_numero, texto_descriptivo, lista_justificacion).
        Escoge el tipo más restrictivo que sí se cumple.
        """
        es_t3, just_t3 = self._es_tipo_3()
        es_t2, just_t2 = self._es_tipo_2()
        es_t1, just_t1 = self._es_tipo_1()

        if es_t3:
            return 3, "Tipo 3 (Regular)", just_t3

        if es_t2:
            # Es Libre de Contexto pero no Regular
            return 2, "Tipo 2 (Libre de Contexto)", just_t3 or just_t2

        if es_t1:
            # Es Sensible al Contexto pero no Tipo 2
            return 1, "Tipo 1 (Sensible al Contexto)", just_t2 or just_t1

        # Si no cumple Tipo 1, es Tipo 0
        return 0, "Tipo 0 (Recursivamente Enumerable)", just_t2 or just_t1
