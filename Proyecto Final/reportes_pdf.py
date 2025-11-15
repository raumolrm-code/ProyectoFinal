import datetime
from typing import List, Tuple

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image as ReportlabImage,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch


def crear_reporte_pdf(
    ruta_salida: str,
    texto_gramatica: str,
    descripcion_tipo: str,
    lista_justificacion: List[str],
    ruta_diagrama_opcional: str | None = None,
) -> Tuple[bool, str]:
    """
    Crea un reporte PDF con:
    - Gramática analizada
    - Tipo de la jerarquía de Chomsky detectado
    - Justificación del agente
    - Diagrama de autómata
    """
    try:
        doc = SimpleDocTemplate(ruta_salida, pagesize=letter)
        estilos = getSampleStyleSheet()
        historia = []

        historia.append(
            Paragraph("Reporte de Análisis - Jerarquía de Chomsky", estilos["Title"])
        )
        historia.append(
            Paragraph(
                f"Generado el: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
                estilos["Normal"],
            )
        )
        historia.append(Spacer(1, 0.25 * inch))

        # Gramática
        historia.append(Paragraph("Gramática analizada", estilos["Heading2"]))
        texto_html = texto_gramatica.replace("\n", "<br/>")
        historia.append(Paragraph(texto_html, estilos["Code"]))
        historia.append(Spacer(1, 0.25 * inch))

        # Clasificación
        historia.append(Paragraph("Clasificación obtenida", estilos["Heading2"]))
        historia.append(Paragraph(descripcion_tipo, estilos["Heading3"]))
        historia.append(Spacer(1, 0.25 * inch))

        # Justificación
        historia.append(Paragraph("Justificación del agente", estilos["Heading2"]))
        if lista_justificacion:
            for j in lista_justificacion:
                historia.append(Paragraph(f"• {j}", estilos["Normal"]))
        else:
            historia.append(
                Paragraph("La gramática cumple todas las restricciones del tipo.", estilos["Normal"])
            )
        historia.append(Spacer(1, 0.25 * inch))

        # Diagrama opcional
        if ruta_diagrama_opcional:
            try:
                historia.append(Paragraph("Diagrama de Autómata", estilos["Heading2"]))
                historia.append(
                    ReportlabImage(
                        ruta_diagrama_opcional, width=6 * inch, height=4 * inch, kind="proportional"
                    )
                )
            except Exception as e:
                historia.append(
                    Paragraph(
                        f"(No se pudo cargar el diagrama: {e})",
                        estilos["Normal"],
                    )
                )

        doc.build(historia)
        return True, f"Reporte guardado en: {ruta_salida}"
    except Exception as e:
        return False, f"Error al generar el PDF: {e}"
