import re

class LexicalError(Exception):
    pass

class IndentationError(Exception):
    pass

# Tokens para miniSQL
TOKEN_SPEC = [
    # Palabras reservadas
    ('SELECT', r'\bSELECT\b'),
    ('FROM', r'\bFROM\b'),
    ('WHERE', r'\bWHERE\b'),
    ('INSERT', r'\bINSERT\b'),
    ('INTO', r'\bINTO\b'),
    ('VALUES', r'\bVALUES\b'),
    ('UPDATE', r'\bUPDATE\b'),
    ('SET', r'\bSET\b'),
    ('DELETE', r'\bDELETE\b'),
    ('CREATE', r'\bCREATE\b'),
    ('TABLE', r'\bTABLE\b'),
    ('DROP', r'\bDROP\b'),
    ('ALTER', r'\bALTER\b'),
    ('JOIN', r'\bJOIN\b'),
    ('ON', r'\bON\b'),
    ('AND', r'\bAND\b'),
    ('OR', r'\bOR\b'),
    ('NOT', r'\bNOT\b'),
    ('NULL', r'\bNULL\b'),
    ('IN', r'\bIN\b'),
    ('LIKE', r'\bLIKE\b'),
    ('BETWEEN', r'\bBETWEEN\b'),
    ('FUNCTION', r'\bFUNCTION\b'),
    ('END', r'\bEND\b'),

    # Operadores y símbolos
    ('COMMA', r','),
    ('SEMICOLON', r';'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('DOT', r'\.'),
    ('EQ', r'='),
    ('NE', r'<>|!='),
    ('GE', r'>='),
    ('LE', r'<='), 
    ('GT', r'>'),
    ('LT', r'<'),
    ('PLUS', r'\+'),
    ('MINUS', r'-'), 
    ('TIMES', r'\*'),
    ('DIVIDE', r'/'),

    # Literales
    ('NUMBER', r'\b\d+(\.\d+)?\b'),

    # Cadenas entre comillas simples
    ('STRING_SINGLE', r"'([^']*)'"),

    # Cadenas entre comillas dobles
    ('STRING_DOUBLE', r'"([^"]*)"'),

  
     # Comentarios
    ('COMMENT_LINE', r'--.*'),
    ('COMMENT_BLOCK', r'/\*[\s\S]*?\*/'),

    # Identificadores
    ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),

    # Espacios y saltos de línea
    ('NEWLINE', r'\n'), ('SKIP', r'[ \t]+'),

    # Cualquier otro carácter inválido
    ('UNKNOWN', r'.'),
   
]

TOKEN_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)

def check_indentation(lines):
    inside_function = False
    expected_indent = None
    for idx, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if not stripped or stripped.startswith('--'):
            continue
        indent = len(line) - len(stripped)
        if stripped.upper().startswith('FUNCTION '):
            inside_function = True
            expected_indent = indent + 4
            continue
        if inside_function:
            if indent < expected_indent and not stripped.upper().startswith('END'):
                raise IndentationError(
                    f"Error de indentación en línea {idx}"
                )
            if stripped.upper().startswith('END'):
                inside_function = False
                expected_indent = None

def tokenize(code):
    lines = code.splitlines()
    check_indentation(lines)

    tokens = []
    line_num = 1
    line_start = 0

    for mo in re.finditer(TOKEN_REGEX, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start

        if kind == 'NEWLINE':
            line_num += 1
            line_start = mo.end()
            continue
        elif kind == 'SKIP' or kind.startswith('COMMENT'):
            continue
        elif kind == 'UNKNOWN':
            raise LexicalError(f"Carácter inválido '{value}' en línea {line_num}, columna {column}")
        elif kind == 'STRING':
            if not value.endswith("'"):
                raise LexicalError(f"Cadena sin cerrar en línea {line_num}, columna {column}")
            value = value[1:-1]
            tokens.append((kind, value, line_num, column))
        else:
            tokens.append((kind, value, line_num, column))

    return tokens

