class SyntaxError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', '', -1, -1)

    def match(self, expected_type):
        token_type, value, line, col = self.current_token()
        if token_type == expected_type:
            self.pos += 1
            return value
        else:
            raise SyntaxError(f"Se esperaba '{expected_type}' pero se encontró '{value}' en línea {line}")

    def parse(self):
        while self.pos < len(self.tokens):
            token_type, *_ = self.current_token()
            if token_type == 'SELECT':
                self.parse_select()
            elif token_type == 'INSERT':
                self.parse_insert()
            elif token_type == 'FUNCTION':
                self.parse_function()
            else:
                raise SyntaxError(f"Instrucción desconocida: {token_type}")

    def parse_select(self):
        self.match('SELECT')
        self.parse_identifier_list()
        self.match('FROM')
        self.match('IDENTIFIER')
        if self.current_token()[0] == 'WHERE':
            self.match('WHERE')
            self.parse_condition()
        self.match('SEMICOLON')

    def parse_insert(self):
        self.match('INSERT')
        self.match('INTO')
        self.match('IDENTIFIER')
        self.match('VALUES')
        self.match('LPAREN')
        self.parse_value_list()
        self.match('RPAREN')
        self.match('SEMICOLON')

    def parse_function(self):
        self.match('FUNCTION')
        self.match('IDENTIFIER')
        while self.current_token()[0] != 'END':
            self.parse()  # Recurisve parse inside function
        self.match('END')

    def parse_identifier_list(self):
        self.match('IDENTIFIER')
        while self.current_token()[0] == 'COMMA':
            self.match('COMMA')
            self.match('IDENTIFIER')

    def parse_value_list(self):
        if self.current_token()[0] not in ('NUMBER', 'STRING'):
            raise SyntaxError("Se esperaba un valor")
        self.match(self.current_token()[0])
        while self.current_token()[0] == 'COMMA':
            self.match('COMMA')
            self.match(self.current_token()[0])

    def parse_condition(self):
        self.match('IDENTIFIER')
        op = self.current_token()[0]
        if op not in ('EQ', 'GT', 'LT', 'GE', 'LE', 'NE'):
            raise SyntaxError("Operador de comparación inválido")
        self.match(op)
        if self.current_token()[0] not in ('NUMBER', 'STRING', 'IDENTIFIER'):
            raise SyntaxError("Valor de comparación inválido")
        self.match(self.current_token()[0])
