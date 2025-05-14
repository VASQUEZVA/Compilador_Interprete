class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self, tables):
        self.tables = tables

    def analyze(self, tokens):
        pos = 0
        while pos < len(tokens):
            token_type, value, *_ = tokens[pos]
            if token_type == 'SELECT':
                pos = self.check_select(tokens, pos)
            elif token_type == 'INSERT':
                pos = self.check_insert(tokens, pos)
            elif token_type == 'FUNCTION':
                pos = self.skip_function(tokens, pos)
            else:
                pos += 1  # ignorar otros tokens
        return True

    def check_select(self, tokens, pos):
        pos += 1  # SELECT
        columns = []
        while tokens[pos][0] == 'IDENTIFIER':
            columns.append(tokens[pos][1])
            pos += 1
            if tokens[pos][0] == 'COMMA':
                pos += 1
            else:
                break
        if tokens[pos][0] != 'FROM':
            raise SemanticError("Falta FROM después de SELECT")
        pos += 1
        table = tokens[pos][1]
        if table not in self.tables:
            raise SemanticError(f"La tabla '{table}' no existe")
        for col in columns:
            if col not in self.tables[table]:
                raise SemanticError(f"La columna '{col}' no existe en '{table}'")
        return self.skip_to_next_statement(tokens, pos)

    def check_insert(self, tokens, pos):
        pos += 2  # INSERT INTO
        table = tokens[pos][1]
        if table not in self.tables:
            raise SemanticError(f"La tabla '{table}' no existe")
        pos += 1
        if tokens[pos][0] != 'VALUES':
            raise SemanticError("Falta VALUES en INSERT")
        pos += 1
        if tokens[pos][0] != 'LPAREN':
            raise SemanticError("Falta paréntesis en VALUES")
        pos += 1
        values = 0
        while tokens[pos][0] in ('STRING', 'NUMBER'):
            values += 1
            pos += 1
            if tokens[pos][0] == 'COMMA':
                pos += 1
            else:
                break
        if tokens[pos][0] != 'RPAREN':
            raise SemanticError("Falta cierre de paréntesis en VALUES")
        if values != len(self.tables[table]):
            raise SemanticError(f"Se esperaban {len(self.tables[table])} valores, se recibieron {values}")
        return self.skip_to_next_statement(tokens, pos)

    def skip_function(self, tokens, pos):
        pos += 1
        while tokens[pos][0] != 'END':
            pos += 1
        return pos + 1

    def skip_to_next_statement(self, tokens, pos):
        while pos < len(tokens) and tokens[pos][0] != 'SEMICOLON':
            pos += 1
        return pos + 1
