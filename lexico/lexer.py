import re

class LexicalError(Exception):
    pass

class IndentationError(Exception):
    pass

#Declarar palabras reservadas en un set para chequeo dinámico
RESERVED_KEYWORDS = {
    'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'UPDATE',
    'SET', 'DELETE', 'CREATE', 'TABLE', 'DROP', 'ALTER', 'JOIN',
    'ON', 'AND', 'OR', 'NOT', 'NULL', 'IN', 'LIKE', 'BETWEEN', 'FUNCTION', 'END',
    'AS', 'DISTINCT', 'GROUP', 'BY', 'HAVING', 'ORDER', 'ASC', 'DESC',
    'LIMIT', 'OFFSET', 'UNION', 'INTERSECT', 'EXCEPT', 'ALL', 'ANY',
    'SOME', 'EXISTS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END_CASE',
    'CAST', 'CONVERT', 'COALESCE', 'IF', 'ELSEIF', 'TRIGGER',
    'PROCEDURE', 'RETURN', 'DECLARE', 'BEGIN', 'END', 'LOOP', 'WHILE',
    'REPEAT', 'UNTIL', 'FOR', 'DO', 'LEAVE', 'CONTINUE',
    'DECLARE', 'CURSOR', 'OPEN', 'FETCH', 'CLOSE', 'EXCEPTION',
    'RAISE', 'SIGNAL', 'SQLSTATE', 'SQLCODE', 'RETURNING', 'LIMIT',
    'OFFSET', 'WITH', 'RECURSIVE', 'TABLESAMPLE', 'TABLESAMPLE_SYSTEM',
    'COMMA', 'SEMICOLON', 'LPAREN', 'RPAREN', 'DOT', 'EQ', 'NE',
    'GE', 'LE', 'GT', 'LT', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'ASSIGN', 'NOT_EQ', 'AND_OP', 'OR_OP', 'LIKE_OP', 'BETWEEN_OP',
    'IN_OP', 'IS_OP', 'NOT_OP', 'NULL_OP', 'NUMBER', 'STRING',
    'COMMENT_LINE', 'COMMENT_BLOCK', 'IDENTIFIER', 'NEWLINE', 'SKIP',
    'UNKNOWN', 'EOF','UPDATE', 'INSERT', 'DELETE', 'ALTER', 'JOIN',
}

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
    ('AS', r'\bAS\b'),
    ('DISTINCT', r'\bDISTINCT\b'),
    ('GROUP', r'\bGROUP\b'),
    ('BY', r'\bBY\b'),
    ('HAVING', r'\bHAVING\b'),
    ('ORDER', r'\bORDER\b'),
    ('ASC', r'\bASC\b'),
    ('DESC', r'\bDESC\b'),
    ('UNION', r'\bUNION\b'),
    ('INTERSECT', r'\bINTERSECT\b'),
    ('EXCEPT', r'\bEXCEPT\b'),
    ('ALL', r'\bALL\b'),
    ('ANY', r'\bANY\b'),
    ('SOME', r'\bSOME\b'),
    ('EXISTS', r'\bEXISTS\b'),
    ('CASE', r'\bCASE\b'),
    ('WHEN', r'\bWHEN\b'),
    ('THEN', r'\bTHEN\b'),
    ('ELSE', r'\bELSE\b'),
    ('END_CASE', r'\bEND CASE\b'),
    ('CAST', r'\bCAST\b'),
    ('CONVERT', r'\bCONVERT\b'),
    ('COALESCE', r'\bCOALESCE\b'),
    ('IF', r'\bIF\b'),
    ('ELSEIF', r'\bELSEIF\b'),
    ('TRIGGER', r'\bTRIGGER\b'),
    ('PROCEDURE', r'\bPROCEDURE\b'),
    ('FUNCTION', r'\bFUNCTION\b'),
    ('BEGIN', r'\bBEGIN\b'),
    ('END', r'\bEND\b'),
    ('LOOP', r'\bLOOP\b'),
    ('WHILE', r'\bWHILE\b'),
    ('REPEAT', r'\bREPEAT\b'),
    ('UNTIL', r'\bUNTIL\b'),
    ('FOR', r'\bFOR\b'),
    ('DO', r'\bDO\b'),
    ('LEAVE', r'\bLEAVE\b'),
    ('CONTINUE', r'\bCONTINUE\b'),
    ('RETURN', r'\bRETURN\b'),
    ('DECLARE', r'\bDECLARE\b'),
    ('CURSOR', r'\bCURSOR\b'),
    ('OPEN', r'\bOPEN\b'),
    ('FETCH', r'\bFETCH\b'),
    ('CLOSE', r'\bCLOSE\b'),
    ('EXCEPTION', r'\bEXCEPTION\b'),
    ('RAISE', r'\bRAISE\b'),
    ('SIGNAL', r'\bSIGNAL\b'),
    ('SQLSTATE', r'\bSQLSTATE\b'),
    ('SQLCODE', r'\bSQLCODE\b'),
    ('RETURNING', r'\bRETURNING\b'),
    ('LIMIT', r'\bLIMIT\b'),
    ('OFFSET', r'\bOFFSET\b'),
    ('WITH', r'\bWITH\b'),
    ('RECURSIVE', r'\bRECURSIVE\b'),
    ('TABLESAMPLE', r'\bTABLESAMPLE\b'),
    ('TABLESAMPLE_SYSTEM', r'\bTABLESAMPLE SYSTEM\b'),
   


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
    ('NOT_EQ', r'<>|!='),
    ('OR_OP', r'OR'),
    ('LIKE_OP', r'LIKE'),
    ('BETWEEN_OP', r'BETWEEN'),
    ('IN_OP', r'IN'),
    ('IS_OP', r'IS'),
    ('NOT_OP', r'NOT'),
    ('NULL_OP', r'NULL'),


    # Literales
    ('NUMBER', r'\b\d+(\.\d+)?([eE][+-]?\d+)?\b'),

    # Cadenas entre comillas simples y dobles
    ('STRING', r"""('([^'\\]|\\.)*'|"([^"\\]|\\.)*")"""),

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
TOKEN_PATTERN = re.compile(TOKEN_REGEX, re.IGNORECASE | re.MULTILINE)

# Función para verificar la indentación
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

    for mo in TOKEN_PATTERN.finditer(code):
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
            # --- CAMBIO: Remover comillas inicial y final simples o dobles ---
            if (value[0] == "'" and value[-1] != "'") or (value[0] == '"' and value[-1] != '"'):
                raise LexicalError(f"Cadena sin cerrar en línea {line_num}, columna {column}")
            value = value[1:-1]
            tokens.append((kind, value, line_num, column))
        elif kind == 'IDENTIFIER':
            #  CAMBIO: Identificar si es palabra reservada
            if value.upper() in RESERVED_KEYWORDS:
                kind = value.upper()
            tokens.append((kind, value, line_num, column))
        else:
            tokens.append((kind, value, line_num, column))

    #  Token EOF para facilitar parsing posterior
    tokens.append(('EOF', '', line_num, 0))

    return tokens

