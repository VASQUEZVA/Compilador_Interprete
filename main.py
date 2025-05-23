from lexico.lexer import tokenize
from sintactico.parser import Parser
from semantico.semantic_analyzer import SemanticAnalyzer  


db_schema = {

    'usuarios': {
        'nombre': 'VARCHAR',
        'edad': 'INT',
        'correo': 'VARCHAR'
    }
}


with open("test.sql", encoding="utf-8") as f:
    code = f.read()


try:
    tokens = tokenize(code)
    parser = Parser(tokens)
    parser.parse()  # Verificación sintáctica
    semantic = SemanticAnalyzer(db_schema) # Inicialización del analizador semántico
    semantic.analyze(tokens)  # Verificación semántica
    print("Análisis completados con exito.")
except Exception as e:
    print("Error:", e)

print("Tokens generados:")
for token in tokens:
    print(token)

