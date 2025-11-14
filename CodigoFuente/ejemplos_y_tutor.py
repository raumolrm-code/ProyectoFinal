import random
from typing import List, Tuple

from estructuras_gramatica import leer_gramatica_desde_texto
from clasificador_chomsky import ClasificadorChomsky
from estructuras_gramatica import Produccion


class GeneradorEjemplos:
    """
    Genera gramáticas de ejemplo para cada tipo de Chomsky.
    La idea es que sean sencillas pero variadas.
    """

    def __init__(self):
        self.no_terminales = ["S", "A", "B"]
        self.terminales = ["a", "b", "c"]

    def _elige_nt(self, excluir: str = "") -> str:
        candidatos = [nt for nt in self.no_terminales if nt != excluir]
        if not candidatos:
            return self.no_terminales[0]
        return random.choice(candidatos)

    def _elige_t(self) -> str:
        return random.choice(self.terminales)

    # ---------- Tipo 3 (Regular) ----------
    def generar_tipo_3(self) -> str:
        """
        Genera una gramática regular (Tipo 3).
        Forma típica: A -> a | aB | epsilon
        """
        reglas = []

        # Aseguramos al menos dos reglas para S
        reglas.append("S -> a A | b")
        reglas.append("A -> a S | c | epsilon")

        # Opcionalmente agregamos otras reglas pequeñas
        if random.random() < 0.5:
            reglas.append("B -> b S | c")

        return "\n".join(reglas)

    # ---------- Tipo 2 (Libre de Contexto pero NO regular) ----------
    def generar_tipo_2(self) -> str:
        """
        Genera una gramática libre de contexto que NO es regular.
        Ejemplo clásico: S -> a S b | a b
        """
        reglas = [
            "S -> a S b | a b",
            "A -> a A | b",  # regla libre de contexto adicional
        ]
        return "\n".join(reglas)

    # ---------- Tipo 1 (Sensible al Contexto pero NO Tipo 2) ----------
    def generar_tipo_1(self) -> str:
        """
        Genera una gramática sensible al contexto:
        Ejemplo: S A -> A S (lado izquierdo con más de un símbolo)
        """
        reglas = [
            "S A -> A S",
            "S -> a S | a",
            "A -> b A | b",
        ]
        return "\n".join(reglas)

    # ---------- Tipo 0 (General) ----------
    def generar_tipo_0(self) -> str:
        """
        Genera una gramática general (Tipo 0) que viola la condición de Tipo 1.
        Por ejemplo, una regla que acorta la cadena: S A -> S
        """
        reglas = [
            "S A -> S",        # acorta la cadena (|SA| > |S|)
            "S -> a S | a A",
            "A -> b A | b",
        ]
        return "\n".join(reglas)

    def generar_por_tipo(self, tipo: int) -> str:
        if tipo == 3:
            return self.generar_tipo_3()
        if tipo == 2:
            return self.generar_tipo_2()
        if tipo == 1:
            return self.generar_tipo_1()
        return self.generar_tipo_0()


class ModoTutor:
    """
    Lógica del modo tutor:
    - Genera una gramática aleatoria de un tipo.
    - El agente la clasifica.
    - El usuario intenta adivinar el tipo.
    """

    def __init__(self):
        self.generador = GeneradorEjemplos()
        self.gramatica_actual: str = ""
        self.tipo_correcto: int = -1
        self.justificacion_actual: List[str] = []

    def generar_ejercicio(self) -> str:
        """
        Genera una nueva gramática aleatoria que el agente
        pueda clasificar correctamente, y guarda la respuesta correcta.
        """
        while True:
            tipo_objetivo = random.randint(0, 3)  # 0,1,2,3
            texto = self.generador.generar_por_tipo(tipo_objetivo)

            try:
                producciones: List[Produccion] = leer_gramatica_desde_texto(texto)
                clasificador = ClasificadorChomsky(producciones)
                tipo_detectado, _, justificacion = clasificador.clasificar()
            except Exception:
                # Si algo sale mal, probamos con otra gramática
                continue

            # Aseguramos que el clasificador esté de acuerdo con el tipo que queríamos
            if tipo_detectado == tipo_objetivo:
                self.gramatica_actual = texto
                self.tipo_correcto = tipo_detectado
                self.justificacion_actual = justificacion
                return texto

    def verificar_respuesta(self, respuesta_usuario: int) -> Tuple[bool, str]:
        """
        Compara la respuesta del usuario con la del agente.
        Devuelve (es_correcta, mensaje_feedback).
        """
        if self.tipo_correcto < 0:
            return False, "Primero genera un ejercicio."

        es_correcta = (respuesta_usuario == self.tipo_correcto)
        encabezado = "¡CORRECTO! ✅\n\n" if es_correcta else (
            f"INCORRECTO ❌. La respuesta correcta era: Tipo {self.tipo_correcto}\n\n"
        )

        mensaje = encabezado
        mensaje += "— Justificación del agente —\n"
        if self.justificacion_actual:
            for j in self.justificacion_actual:
                mensaje += f"- {j}\n"
        else:
            mensaje += "La gramática cumple todas las restricciones del tipo detectado."

        return es_correcta, mensaje
