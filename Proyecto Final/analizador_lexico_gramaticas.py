import re
from typing import List, Tuple, Optional


class PatronesGramaticas:
    """Expresiones regulares para reconocer los símbolos de una gramática."""

    RE_PRODUCCION = re.compile(r"->|::=")
    RE_PIPE = re.compile(r"\|")
    RE_NO_TERMINAL_BRACKETS = re.compile(r"<[a-zA-Z_][a-zA-Z0-9_]*>")
    RE_NO_TERMINAL_MAYUS = re.compile(r"[A-Z][A-Z0-9_]*")
    RE_TERMINAL_MINUS = re.compile(r"[a-z][a-z0-9_]*")
    RE_EPSILON = re.compile(r"\b(epsilon)\b|ε")
    RE_TERMINAL_COMILLAS = re.compile(r"'.*?'")
    RE_ESPACIOS = re.compile(r"\s+")
    RE_COMENTARIO = re.compile(r"#.*")


class AnalizadorLexicoGramaticas:
    """
    Analizador léxico para gramáticas formales.
    Entrega tokens de la forma (lexema, tipo, linea, columna).
    """

    def __init__(self):
        self.P = PatronesGramaticas()
        self.reglas = [
            (self.P.RE_ESPACIOS, None),
            (self.P.RE_COMENTARIO, None),
            (self.P.RE_PRODUCCION, "PRODUCCION"),
            (self.P.RE_PIPE, "PIPE"),
            (self.P.RE_EPSILON, "EPSILON"),
            (self.P.RE_NO_TERMINAL_BRACKETS, "NO_TERMINAL"),
            (self.P.RE_NO_TERMINAL_MAYUS, "NO_TERMINAL"),
            (self.P.RE_TERMINAL_MINUS, "TERMINAL"),
            (self.P.RE_TERMINAL_COMILLAS, "TERMINAL_COMILLAS"),
        ]

    def tokenizar_linea(self, linea: str, numero_linea: int) -> List[Tuple[str, str, int, int]]:
        """
        Recorre una línea y devuelve la lista de tokens válidos detectados.
        """
        tokens: List[Tuple[str, str, int, int]] = []
        i, n = 0, len(linea)

        while i < n:
            columna = i + 1
            encontrado = False

            for regex, tipo in self.reglas:
                m = regex.match(linea, i)
                if m:
                    i = m.end()
                    if tipo:
                        lexema = m.group(0)
                        if tipo == "TERMINAL_COMILLAS":
                            tipo = "TERMINAL"
                            lexema = lexema[1:-1]
                        tokens.append((lexema, tipo, numero_linea, columna))
                    encontrado = True
                    break

            if not encontrado:
                lexema_invalido = linea[i]
                tokens.append((lexema_invalido, "INVALIDO", numero_linea, columna))
                i += 1

        return tokens
