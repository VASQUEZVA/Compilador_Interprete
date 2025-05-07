import re

class LexicalError(Exception):
    pass

class IndentationError(Exception):
    pass

# Definición de tokens para miniSQL

TOKEN_SPEC = [
    ('SELECT', r'\bSELECT\b'),
    ('FROM', r'\bFROM\b'),
    ('WHERE', r'\bWHERE\b'),
    ('INSERT', r'\bINSERT\b'),
    ('INTO', r'\bINTO\b'),
    ('VALUES', r'\bVALUES\b'),
    ('UPDATE', r'\bUPDATE\b'),
    ('SET', r'\bSET\b'),
    ('DELETE', r'\bDELETE\b'),
    ('FUNCTION', r'\bFUNCTION\b'),
    ('END', r'\bEND\b'),
    ('COMMA', r','),
    ('SEMICOLON', r';'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('EQ', r'='),
    ('GT', r'>'),
    ('LT', r'<'),
    ('GE', r'>='),
    ('LE', r'<='),
    ('NE', r'!='),
    ('NUMBER', r'\b\d+\b'),
    ('STRING', r"'[^']*'"),
    ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
    ('UNKNOWN', r'.'),  # cualquier otro carácter inválido
]

TOKEN_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)

def check_indentation(lines):
    inside_function = False
    expected_indent = None
    for idx, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if not stripped or stripped.startswith('--'):  # Comentario o línea vacía
            continue

        indent = len(line) - len(stripped)

        if stripped.upper().startswith('FUNCTION '):
            inside_function = True
            expected_indent = indent + 4
            continue

        if inside_function:
            if indent < expected_indent and not stripped.upper().startswith('END'):
                raise IndentationError(
                    f"Error de indentación en línea {idx}: se esperaban al menos {expected_indent} espacios"
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
        elif kind == 'SKIP':
            continue
        elif kind == 'UNKNOWN':
            raise LexicalError(f"Carácter inválido '{value}' en línea {line_num}")
        else:
            tokens.append((kind, value, line_num, column))

    return tokens

