from typing import Dict, Any, Tuple, List, Set
from utilidades_generales import EPSILON_MT, MOVER_DERECHA, MOVER_IZQUIERDA, MOVER_SIN_CAMBIO


class DefinicionesAutomatas:
    """
    Autómatas de ejemplo en el mismo formato que tu Proyecto 1.
    Sirven para probar el conversor y los diagramas.
    """

    @staticmethod
    def convertir_delta_a_listas(delta: Dict[Tuple[int, str], Tuple[str, int, int]]):
        estados_actuales: List[int] = []
        lecturas: List[str] = []
        escribe: List[str] = []
        estados_siguiente: List[int] = []
        movimientos: List[int] = []

        for (estado, leido), (escribir, estado_sig, mover) in delta.items():
            estados_actuales.append(estado)
            lecturas.append(leido)
            escribe.append(escribir)
            estados_siguiente.append(estado_sig)
            movimientos.append(mover)

        return estados_actuales, lecturas, escribe, estados_siguiente, movimientos

    @staticmethod
    def automata_l1() -> Dict[str, Any]:
        """
        Lenguaje L1: (ab)*
        """
        delta = {
            (0, "a"): (EPSILON_MT, 1, MOVER_DERECHA),
            (1, "b"): (EPSILON_MT, 0, MOVER_DERECHA),
        }
        E, L, W, S, M = DefinicionesAutomatas.convertir_delta_a_listas(delta)
        return {
            "nombre": "L1: (ab)*",
            "start_state": 0,
            "accept_states": {0},
            "alphabet": {"a", "b"},
            "estActua": E,
            "lecturas": L,
            "escribeC": W,
            "estsigui": S,
            "mueveCab": M,
        }

    @staticmethod
    def automata_l2() -> Dict[str, Any]:
        """
        Lenguaje L2: a(a|b)*b
        """
        delta = {
            (0, "a"): (EPSILON_MT, 1, MOVER_DERECHA),
            (1, "a"): (EPSILON_MT, 1, MOVER_DERECHA),
            (1, "b"): (EPSILON_MT, 2, MOVER_DERECHA),
            (2, "a"): (EPSILON_MT, 1, MOVER_DERECHA),
            (2, "b"): (EPSILON_MT, 2, MOVER_DERECHA),
        }
        E, L, W, S, M = DefinicionesAutomatas.convertir_delta_a_listas(delta)
        return {
            "nombre": "L2: a(a|b)*b",
            "start_state": 0,
            "accept_states": {2},
            "alphabet": {"a", "b"},
            "estActua": E,
            "lecturas": L,
            "escribeC": W,
            "estsigui": S,
            "mueveCab": M,
        }

    @staticmethod
    def obtener_lista() -> List[Dict[str, Any]]:
        return [
            DefinicionesAutomatas.automata_l1(),
            DefinicionesAutomatas.automata_l2(),
        ]
