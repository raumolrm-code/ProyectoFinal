Descripción general
Chomsky Classifier AI es una herramienta interactiva que ayuda a estudiantes y docentes a trabajar con lenguajes formales. El programa permite escribir gramáticas, analizarlas y clasificarlas dentro de la Jerarquía de Chomsky (Tipo 0, 1, 2 o 3). Además, integra conversores entre modelos equivalentes, un modo tutor tipo “quiz”, comparador de gramáticas y generación automática de diagramas y reportes en PDF.

La idea central del proyecto es que la computadora actúe como un “agente inteligente” que no solo responde con un número de tipo, sino que explica por qué una gramática o un autómata pertenecen a cierta clase, mostrando paso a paso las reglas que se cumplen o que se rompen.

¿Qué hace el proyecto?

El proyecto ofrece los siguientes módulos principales:

Clasificador de gramáticas

La persona escribe una gramática formal usando producciones del tipo S -> a S b o A -> a | epsilon.

El sistema analiza la estructura, limpia las producciones y las revisa contra las reglas de la Jerarquía de Chomsky.

Como resultado, indica si la gramática es de Tipo 3 (Regular), Tipo 2 (Libre de contexto), Tipo 1 (Sensible al contexto) o Tipo 0 (Recursivamente enumerable).

Incluye un modo explicativo que muestra por qué se aceptó o se rompió cada tipo.

Conversor de modelos

Permite transformar un autómata finito determinista (AFD) en una gramática regular equivalente.

Permite ir encadenando conversiones: Gramática Regular → AFN → AFD, y AFD → Gramática Regular.

Genera diagramas de estados del autómata usando Graphviz.

Modo Tutor (Quiz)

Genera automáticamente gramáticas aleatorias de diferentes tipos.

Pide a la persona usuaria que indique a qué tipo de Chomsky pertenece cada gramática.

Después compara la respuesta con el análisis del agente y muestra una retroalimentación inmediata, explicando el razonamiento.

Comparador de equivalencias (heurístico)

Permite escribir dos gramáticas y estimar si generan el mismo lenguaje hasta una longitud máxima de cadenas n.

No es una prueba matemática absoluta, pero sirve como apoyo para trabajos y experimentos.

Visualizador y reportes

Genera diagramas de autómatas en formato de imagen usando Graphviz.

Permite exportar un reporte en PDF con la gramática, la clasificación, la justificación y, opcionalmente, el diagrama generado.

¿Por qué el proyecto es útil?

Apoya el aprendizaje: convierte temas abstractos de Teoría de Autómatas y Lenguajes Formales en algo visual y manipulable.

Explica, no solo responde: el modo explicativo muestra qué reglas se cumplen y cuáles se violan, lo que ayuda a entender los errores de diseño de una gramática.

Integra varios modelos: une gramáticas, autómatas y expresiones regulares en una sola interfaz, mostrando cómo se relacionan entre sí.

Sirve como laboratorio virtual: el modo tutor y el comparador de gramáticas permiten hacer ejercicios rápidos sin tener que escribir código adicional.

¿Cómo pueden comenzar las personas usuarias con el proyecto?
1. Requisitos previos

Python 3.10 o superior instalado.

Librerías de Python:

- graphviz

- Pillow

- reportlab

Librería estándar tkinter (incluida en la mayoría de instalaciones de Python).

Graphviz instalado en el sistema operativo y agregado a la variable de entorno PATH para poder generar diagramas:

En Windows, normalmente se instala en C:\Program Files\Graphviz o similar.

Es importante que el ejecutable dot pueda usarse desde la terminal.

Instalación de las dependencias de Python (en la carpeta del proyecto): pip install graphviz Pillow reportlab

Sugerencias de uso

Probar primero el módulo de Clasificador de Gramáticas con ejemplos sencillos.

Asegurarse de que Graphviz está bien configurado antes de usar la generación de diagramas.

Utilizar el Modo Tutor para practicar antes de exámenes o tareas.

Guardar los reportes PDF como evidencia de los análisis realizados.
