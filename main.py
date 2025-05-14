from lexico.lexer import tokenize
from sintactico.parser import Parser
from semantico.semantic_analyzer import SemanticAnalyzer  

# Simulación de esquema de base de datos
db_schema = {
    'usuarios': ['nombre', 'edad', 'correo']
}

# Simulación de código SQL para prueba

with open("test.sql", encoding="utf-8") as f:
    code = f.read()


try:
    tokens = tokenize(code)
    parser = Parser(tokens)
    parser.parse()  # Verificación sintáctica
    semantic = SemanticAnalyzer(db_schema)  # Corregido
    semantic.analyze(tokens)  # Verificación semántica
    print("Análisis semántico correcto.")
except Exception as e:
    print("Error:", e)
