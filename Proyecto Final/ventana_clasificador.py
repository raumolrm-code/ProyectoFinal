import tkinter as tk
from tkinter import scrolledtext, filedialog

from utilidades_generales import VentanaCentrada, Alerta
from estructuras_gramatica import leer_gramatica_desde_texto, producciones_a_texto
from clasificador_chomsky import ClasificadorChomsky
from reportes_pdf import crear_reporte_pdf


class TextoConNumerosLinea(tk.Frame):
    """
    Widget de texto con números de línea a la izquierda.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#b9ede2")
        self.canvas_lineas = tk.Canvas(self, width=40, bg="#e0e0e0", highlightthickness=0)
        self.texto = tk.Text(self, **kwargs)
        self.barra = tk.Scrollbar(self, orient="vertical", command=self._scroll_vertical)

        self.canvas_lineas.pack(side="left", fill="y")
        self.texto.pack(side="left", fill="both", expand=True)
        self.barra.pack(side="right", fill="y")

        self.texto.config(yscrollcommand=self._sync_scroll)
        self.texto.bind("<KeyRelease>", self._actualizar_lineas)
        self.texto.bind("<MouseWheel>", self._actualizar_lineas)
        self.texto.bind("<Button-4>", self._actualizar_lineas)  # Linux
        self.texto.bind("<Button-5>", self._actualizar_lineas)

        self._actualizar_lineas()

    def _scroll_vertical(self, *args):
        self.texto.yview(*args)
        self._actualizar_lineas()

    def _sync_scroll(self, *args):
        self.barra.set(*args)
        self._actualizar_lineas()

    def _actualizar_lineas(self, event=None):
        self.canvas_lineas.delete("all")
        i = self.texto.index("@0,0")
        while True:
            dline = self.texto.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linea = str(i).split(".")[0]
            self.canvas_lineas.create_text(
                2, y, anchor="nw", text=linea, fill="#606060", font=("Consolas", 9)
            )
            i = self.texto.index(f"{i}+1line")
        self.canvas_lineas.configure(scrollregion=self.canvas_lineas.bbox("all"))

    # Métodos de conveniencia
    def get(self, *args, **kwargs):
        return self.texto.get(*args, **kwargs)

    def insert(self, *args, **kwargs):
        self.texto.insert(*args, **kwargs)
        self._actualizar_lineas()

    def delete(self, *args, **kwargs):
        self.texto.delete(*args, **kwargs)
        self._actualizar_lineas()

    def config(self, *args, **kwargs):
        self.texto.config(*args, **kwargs)


class VentanaClasificador(tk.Toplevel, VentanaCentrada):
    """
    Ventana principal para clasificar gramáticas ingresadas por el usuario.
    """

    def __init__(self, master):
        super().__init__(master)
        self.title("Clasificador de Gramáticas - Jerarquía Chomsky")
        self.configure(bg="#b9ede2")
        self.centrar_ventana(self, 960, 600)

        self.producciones = []
        self.tipo_descripcion = ""
        self.justificacion = []
        self.texto_gramatica_original = ""

        self._construir_interfaz()

    def _construir_interfaz(self):
        marco = tk.Frame(self, bg="#b9ede2")
        marco.pack(fill="both", expand=True, padx=10, pady=10)

        marco.grid_rowconfigure(1, weight=1)
        marco.grid_columnconfigure(0, weight=1)
        marco.grid_columnconfigure(1, weight=1)

        # Etiquetas de cabecera
        tk.Label(
            marco,
            text="Gramática (Entrada)",
            bg="#b9ede2",
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            marco,
            text="Resultado y Justificación",
            bg="#b9ede2",
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=1, sticky="w")

        # Lado izquierdo: entrada
        marco_izq = tk.Frame(marco, bg="#b9ede2")
        marco_izq.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        marco_izq.grid_rowconfigure(0, weight=1)
        marco_izq.grid_columnconfigure(0, weight=1)

        self.caja_entrada = TextoConNumerosLinea(
            marco_izq,
            font=("Consolas", 11),
            wrap="none",
        )
        self.caja_entrada.pack(fill="both", expand=True)

        ejemplo = (
            "# Ejemplo de gramática de Tipo 2:\n"
            "S -> a S b | a b\n"
            "\n"
            "# Reglas:\n"
            "# - Usa mayúsculas para No-Terminales (S, A, B...)\n"
            "# - Usa minúsculas para terminales (a, b, c...)\n"
            "# - Usa 'epsilon' o 'ε' para la cadena vacía.\n"
        )
        self.caja_entrada.insert("1.0", ejemplo)

        # Lado derecho: salida
        marco_der = tk.Frame(marco, bg="#b9ede2")
        marco_der.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        marco_der.grid_rowconfigure(0, weight=1)
        marco_der.grid_columnconfigure(0, weight=1)

        self.caja_salida = scrolledtext.ScrolledText(
            marco_der,
            font=("Consolas", 11),
            wrap="word",
            state="disabled",
        )
        self.caja_salida.pack(fill="both", expand=True)

        # Botones inferiores
        marco_botones = tk.Frame(marco, bg="#b9ede2")
        marco_botones.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        self.boton_clasificar = tk.Button(
            marco_botones,
            text="Clasificar Gramática",
            font=("Segoe UI", 11, "bold"),
            bg="#c9c695",
            command=self.ejecutar_clasificacion,
        )
        self.boton_clasificar.pack(side="left", padx=5)

        self.boton_pdf = tk.Button(
            marco_botones,
            text="Exportar Reporte PDF",
            font=("Segoe UI", 11),
            bg="#c9c695",
            command=self.exportar_pdf,
            state="disabled",
        )
        self.boton_pdf.pack(side="left", padx=5)

    def _mostrar_salida(self, texto: str):
        self.caja_salida.config(state="normal")
        self.caja_salida.delete("1.0", "end")
        self.caja_salida.insert("1.0", texto)
        self.caja_salida.config(state="disabled")

    def ejecutar_clasificacion(self):
        self.boton_clasificar.config(text="Clasificando...", state="disabled")
        self.boton_pdf.config(state="disabled")
        self._mostrar_salida("Procesando gramática...")

        texto = self.caja_entrada.get("1.0", "end")
        self.texto_gramatica_original = texto

        try:
            self.producciones = leer_gramatica_desde_texto(texto)
            clasificador = ClasificadorChomsky(self.producciones)
            tipo, descripcion, justificacion = clasificador.clasificar()

            self.tipo_descripcion = descripcion
            self.justificacion = justificacion

            texto_normalizado = producciones_a_texto(self.producciones)

            salida = []
            salida.append(f"--- TIPO DETECTADO: {descripcion} ---\n")
            salida.append("--- PRODUCCIONES ---")
            salida.append(texto_normalizado)
            salida.append("\n--- JUSTIFICACIÓN ---")
            if justificacion:
                for j in justificacion:
                    salida.append(f"- {j}")
            else:
                salida.append("La gramática cumple todas las restricciones del tipo.")

            self._mostrar_salida("\n".join(salida))
            self.boton_pdf.config(state="normal")

        except Exception as e:
            self._mostrar_salida(f"Error al analizar la gramática:\n\n{e}")

        self.boton_clasificar.config(text="Clasificar Gramática", state="normal")

    def exportar_pdf(self):
        if not self.producciones:
            Alerta.mostrar(self, "Error", "Primero clasifica una gramática.")
            return

        ruta = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Guardar reporte como...",
        )
        if not ruta:
            return

        ok, mensaje = crear_reporte_pdf(
            ruta,
            self.texto_gramatica_original,
            self.tipo_descripcion,
            self.justificacion,
        )
        if ok:
            Alerta.mostrar(self, "Éxito", mensaje)
        else:
            Alerta.mostrar(self, "Error", mensaje)
