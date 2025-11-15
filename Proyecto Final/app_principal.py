import tkinter as tk

from utilidades_generales import VentanaCentrada, Alerta
from ventana_clasificador import VentanaClasificador
from ventana_conversor import VentanaConversor
from ventana_tutor import VentanaTutor
from ventana_equivalencias import VentanaEquivalencias


class AplicacionPrincipal(tk.Tk, VentanaCentrada):
    """
    Menú principal del proyecto "Jerarquía de Chomsky".
    Desde aquí se abren las distintas herramientas.
    """

    def __init__(self):
        super().__init__()
        self.title("Chomsky Classifier AI - Menú Principal")
        self.configure(bg="#1E283D")
        self.centrar_ventana(self, 520, 420)

        tk.Label(
            self,
            text="Jerarquía de Chomsky",
            bg="#1E283D",
            fg="#e5e7eb",
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=(20, 10))

        tk.Label(
            self,
            text="Selecciona un módulo para iniciar",
            bg="#1E283D",
            fg="#94a3b8",
            font=("Segoe UI", 11),
        ).pack(pady=(0, 20))

        estilo_boton = {
            "font": ("Segoe UI", 11, "bold"),
            "bg": "#c9c695",
            "width": 32,
            "pady": 8,
        }

        tk.Button(
            self,
            text="1. Clasificador de Gramáticas",
            command=self.abrir_clasificador,
            **estilo_boton,
        ).pack(pady=6)

        tk.Button(
            self,
            text="2. Conversor de Modelos (Regex / AFD / Gramática)",
            command=self.abrir_conversor,
            **estilo_boton,
        ).pack(pady=6)

        tk.Button(
            self,
            text="3. Modo Tutor (Quiz de Tipos)",
            command=self.abrir_tutor,
            **estilo_boton,
        ).pack(pady=6)

        tk.Button(
            self,
            text="4. Comparador de Equivalencia de Gramáticas",
            command=self.abrir_equivalencias,
            **estilo_boton,
        ).pack(pady=6)

    # --------- Acciones para abrir ventanas ---------
    def abrir_clasificador(self):
        try:
            ventana = VentanaClasificador(self)
            ventana.grab_set()
        except Exception as e:
            Alerta.mostrar(self, "Error", f"No se pudo abrir el clasificador:\n{e}")

    def abrir_conversor(self):
        try:
            ventana = VentanaConversor(self)
            ventana.grab_set()
        except Exception as e:
            Alerta.mostrar(self, "Error", f"No se pudo abrir el conversor:\n{e}")

    def abrir_tutor(self):
        try:
            ventana = VentanaTutor(self)
            ventana.grab_set()
        except Exception as e:
            Alerta.mostrar(self, "Error", f"No se pudo abrir el modo tutor:\n{e}")

    def abrir_equivalencias(self):
        try:
            ventana = VentanaEquivalencias(self)
            ventana.grab_set()
        except Exception as e:
            Alerta.mostrar(self, "Error", f"No se pudo abrir el comparador:\n{e}")


if __name__ == "__main__":
    app = AplicacionPrincipal()
    app.mainloop()
