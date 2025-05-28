# Compilador_Interprete_MINISQL

## 1. Analizador Léxico

**Definición:**  
El analizador léxico (*scanner*) es la primera fase de un compilador. Se encarga de leer el código fuente y dividirlo en unidades significativas llamadas *tokens* (como palabras clave, identificadores, operadores y literales).

**Objetivo:**  
Transformar la secuencia de caracteres del código fuente en una secuencia de tokens que puedan ser fácilmente procesados por el analizador sintáctico.

## 2. Analizador Sintáctico

**Definición:**  
El analizador sintáctico (*parser*) toma los tokens generados por el analizador léxico y verifica si su secuencia cumple con las reglas gramaticales del lenguaje. Genera una estructura jerárquica conocida como árbol sintáctico.

**Objetivo:**  
Comprobar que la estructura del programa sea válida conforme a la gramática del lenguaje.

## 3. Analizador Semántico

**Definición:**  
El analizador semántico verifica que las estructuras sintácticamente correctas tengan un significado válido en el contexto del lenguaje, comprobando reglas como tipos de datos, uso de identificadores y operaciones permitidas.

**Objetivo:**  
Asegurar que el programa tenga sentido lógico y semántico más allá de su correcta sintaxis.


| Analizador       | Función Principal                              | Importancia Clave                                              |
|------------------|-------------------------------------------------|-----------------------------------------------------------------|
| **Léxico**       | Convierte el texto en tokens                   | Simplifica el análisis posterior y detecta errores básicos      |
| **Sintáctico**   | Verifica la estructura gramatical del código   | Asegura que el código esté bien formado                         |
| **Semántico**    | Verifica el significado lógico del programa    | Asegura que el código tenga coherencia y sentido lógico         |


     

